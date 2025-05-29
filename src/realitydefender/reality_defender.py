"""
Main RealityDefender class for interacting with the Reality Defender API
"""

import asyncio
import os
from typing import Any, Callable, Optional, cast

from .client import create_http_client
from .core.constants import DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT
from .core.events import EventEmitter
from .detection.results import get_detection_result
from .detection.upload import upload_file
from .errors import RealityDefenderError
from .types import (
    DetectionResult,
    GetResultOptions,
    RealityDefenderConfig,
    UploadOptions,
    UploadResult,
)


class RealityDefender(EventEmitter):
    """
    Main SDK class for interacting with the Reality Defender API
    """

    def __init__(self, config: RealityDefenderConfig) -> None:
        """
        Creates a new Reality Defender SDK instance

        Args:
            config: Configuration options including API key

        Raises:
            RealityDefenderError: If API key is missing
        """
        super().__init__()

        if not config.get("api_key"):
            raise RealityDefenderError("API key is required", "unauthorized")

        self.api_key = config["api_key"]
        self.client = create_http_client(
            {"api_key": self.api_key, "base_url": config.get("base_url")}
        )

    async def upload(self, options: UploadOptions) -> UploadResult:
        """
        Upload a file to Reality Defender for analysis (async version)

        Args:
            options: Upload options including file path

        Returns:
            Dictionary with request_id and media_id

        Raises:
            RealityDefenderError: If upload fails
        """
        try:
            result = await upload_file(self.client, options)
            return result
        except RealityDefenderError:
            raise
        except Exception as error:
            raise RealityDefenderError(f"Upload failed: {str(error)}", "upload_failed")

    def upload_sync(self, options: UploadOptions) -> UploadResult:
        """
        Upload a file to Reality Defender for analysis (synchronous version)

        This is a convenience wrapper around the async upload method.

        Args:
            options: Upload options including file path

        Returns:
            Dictionary with request_id and media_id

        Raises:
            RealityDefenderError: If upload fails
        """
        return self._run_async(self.upload(options))

    def upload_file(self, file_path: str) -> UploadResult:
        """
        Upload a file to Reality Defender for analysis (simplified version)

        This is a more Pythonic convenience method that takes a direct file path.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dictionary with request_id and media_id

        Raises:
            RealityDefenderError: If upload fails
        """
        if not os.path.exists(file_path):
            raise RealityDefenderError(f"File not found: {file_path}", "invalid_file")

        return self.upload_sync({"file_path": file_path})

    async def get_result(
        self, request_id: str, options: Optional[GetResultOptions] = None
    ) -> DetectionResult:
        """
        Get the detection result for a specific request ID (async version)

        Args:
            request_id: The request ID to get results for
            options: Optional parameters for polling

        Returns:
            Detection result with status and scores
        """
        if options is None:
            options = {}
        return await get_detection_result(self.client, request_id, options)

    def get_result_sync(
        self, request_id: str, options: Optional[GetResultOptions] = None
    ) -> DetectionResult:
        """
        Get the detection result for a specific request ID (synchronous version)

        This is a convenience wrapper around the async get_result method.

        Args:
            request_id: The request ID to get results for
            options: Optional parameters for polling

        Returns:
            Detection result with status and scores
        """
        return self._run_async(self.get_result(request_id, options))

    def detect_file(self, file_path: str) -> DetectionResult:
        """
        Convenience method to upload and detect a file in one step

        This is a fully synchronous method that handles all async operations internally.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Detection result with status and scores

        Raises:
            RealityDefenderError: If upload or detection fails
        """
        # Validation - more Pythonic to check path early
        if not os.path.exists(file_path):
            raise RealityDefenderError(f"File not found: {file_path}", "invalid_file")

        # Upload the file
        upload_result = self.upload_sync({"file_path": file_path})
        request_id = upload_result["request_id"]

        # Get the result
        return self.get_result_sync(request_id)

    def poll_for_results(
        self,
        request_id: str,
        polling_interval: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> asyncio.Task:
        """
        Start polling for results with event-based callback (async version)

        Args:
            request_id: The request ID to poll for
            polling_interval: Interval in milliseconds between polls (default: 2000)
            timeout: Maximum time to poll in milliseconds (default: 60000)

        Returns:
            Asyncio task that can be awaited
        """
        polling_interval = polling_interval or DEFAULT_POLLING_INTERVAL
        timeout = timeout or DEFAULT_TIMEOUT

        return asyncio.create_task(
            self._poll_for_results(request_id, polling_interval, timeout)
        )

    def poll_for_results_sync(
        self,
        request_id: str,
        *,  # Force keyword arguments for better readability
        polling_interval: Optional[int] = None,
        timeout: Optional[int] = None,
        on_result: Optional[Callable[[DetectionResult], None]] = None,
        on_error: Optional[Callable[[RealityDefenderError], None]] = None,
    ) -> None:
        """
        Start polling for results with synchronous callbacks

        This is a convenience wrapper around the async poll_for_results method.

        Args:
            request_id: The request ID to poll for
            polling_interval: Interval in milliseconds between polls (default: 2000)
            timeout: Maximum time to poll in milliseconds (default: 60000)
            on_result: Callback function when result is received
            on_error: Callback function when error occurs
        """
        # Add event handlers if provided
        if on_result:
            # Cast to ResultHandler to satisfy type checker
            from .types.events import ResultHandler
            self.on("result", cast(ResultHandler, on_result))
        if on_error:
            # Cast to ErrorHandler to satisfy type checker
            from .types.events import ErrorHandler
            self.on("error", cast(ErrorHandler, on_error))

        # Create and run the polling task
        polling_task = self.poll_for_results(request_id, polling_interval, timeout)
        self._run_async(polling_task)  # Discard the return value

    async def _poll_for_results(
        self, request_id: str, polling_interval: int, timeout: int
    ) -> None:
        """
        Internal implementation of polling for results

        Args:
            request_id: The request ID to poll for
            polling_interval: Interval in milliseconds between polls
            timeout: Maximum time to poll in milliseconds
        """
        elapsed = 0
        max_wait_time = timeout
        is_completed = False

        # Check if timeout is already zero/expired before starting
        if timeout <= 0:
            self.emit(
                "error", RealityDefenderError("Polling timeout exceeded", "timeout")
            )
            return

        while not is_completed and elapsed < max_wait_time:
            try:
                result = await self.get_result(request_id)

                if result["status"] == "ANALYZING":
                    elapsed += polling_interval
                    await asyncio.sleep(polling_interval / 1000)  # Convert to seconds
                else:
                    # We have a final result
                    is_completed = True
                    self.emit("result", result)
            except RealityDefenderError as error:
                if error.code == "not_found":
                    # Result not ready yet, continue polling
                    elapsed += polling_interval
                    await asyncio.sleep(polling_interval / 1000)  # Convert to seconds
                else:
                    # Any other error is emitted and polling stops
                    is_completed = True
                    self.emit("error", error)
            except Exception as error:
                is_completed = True
                self.emit("error", RealityDefenderError(str(error), "unknown_error"))

        # Check if we timed out
        if not is_completed and elapsed >= max_wait_time:
            self.emit(
                "error", RealityDefenderError("Polling timeout exceeded", "timeout")
            )

    def _run_async(self, coro: Any) -> Any:
        """
        Run an async coroutine in a new event loop

        Args:
            coro: Coroutine to run

        Returns:
            The result of the coroutine

        Raises:
            RealityDefenderError: If the async operation fails
        """
        try:
            # Get the current event loop, or create a new one if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                # If there's no event loop in this thread, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # If the loop is already running, use run_coroutine_threadsafe
                # This will likely happen in a GUI application or web server
                future = asyncio.run_coroutine_threadsafe(coro, loop)
                return future.result()
            else:
                # If not running, we can use the loop directly
                return loop.run_until_complete(coro)
        except Exception as e:
            # Convert any asyncio errors to our own error format
            if isinstance(e, RealityDefenderError):
                raise e
            raise RealityDefenderError(
                f"Async operation failed: {str(e)}", "unknown_error"
            )
