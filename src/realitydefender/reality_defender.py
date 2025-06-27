"""
Main RealityDefender class for interacting with the Reality Defender API
"""

import asyncio
import atexit
import os
from typing import Any, Callable, Coroutine, Optional, TypeVar, cast

import asyncio_atexit  # type:ignore

from realitydefender.client import create_http_client
from realitydefender.core.constants import DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT
from realitydefender.core.events import EventEmitter
from realitydefender.detection.results import get_detection_result
from realitydefender.detection.upload import upload_file
from realitydefender.errors import RealityDefenderError
from realitydefender.types import (
    DetectionResult,
    ErrorHandler,
    ResultHandler,
    UploadResult,
)

T = TypeVar("T")


class RealityDefender(EventEmitter):
    """
    Main SDK class for interacting with the Reality Defender API
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        """
        Creates a new Reality Defender SDK instance

        Args:
            api_key: Reality Defender API key
            base_url: Base URL to connect to Reality Defender API

        Raises:
            RealityDefenderError: If API key is missing
        """
        super().__init__()

        if not api_key:
            raise RealityDefenderError("API key is required", "unauthorized")

        self.api_key = api_key
        self.client = create_http_client(
            {"api_key": self.api_key, "base_url": base_url}
        )

        # register handlers to clean anything up at exit
        atexit.register(self.cleanup_sync)

        try:
            asyncio_atexit.register(self.cleanup)
        except RuntimeError:
            # If there is no async loop running, then we can't register cleanup
            pass

    async def upload(self, file_path: str) -> UploadResult:
        """
        Upload a file to Reality Defender for analysis (async version)

        Args:
            file_path: Path to file to upload

        Returns:
            Dictionary with request_id and media_id

        Raises:
            RealityDefenderError: If upload fails
        """
        try:
            result = await upload_file(self.client, file_path)
            return result
        except RealityDefenderError:
            raise
        except Exception as error:
            raise RealityDefenderError(f"Upload failed: {str(error)}", "upload_failed")

    def upload_sync(self, file_path: str) -> UploadResult:
        """
        Upload a file to Reality Defender for analysis (synchronous version)

        This is a convenience wrapper around the async upload method.

        Args:
            file_path: Path to file to upload

        Returns:
            Dictionary with request_id and media_id

        Raises:
            RealityDefenderError: If upload fails
        """
        return self._run_async(self.upload(file_path))

    async def get_result(
        self,
        request_id: str,
        max_attempts: int = DEFAULT_POLLING_INTERVAL,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
    ) -> DetectionResult:
        """
        Get the detection result for a specific request ID (async version)

        Args:
            request_id: The request ID to get results for
            max_attempts: Maximum number of attempts to get results
            polling_interval: How long to wait between attempts

        Returns:
            Detection result with status and scores
        """
        return await get_detection_result(
            self.client,
            request_id,
            max_attempts=max_attempts,
            polling_interval=polling_interval,
        )

    def get_result_sync(
        self,
        request_id: str,
        max_attempts: int = DEFAULT_POLLING_INTERVAL,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
    ) -> DetectionResult:
        """
        Get the detection result for a specific request ID (synchronous version)

        This is a convenience wrapper around the async get_result method.

        Args:
            request_id: The request ID to get results for
            max_attempts: Maximum number of attempts to get results
            polling_interval: How long to wait between attempts

        Returns:
            Detection result with status and scores
        """
        return self._run_async(
            self.get_result(
                request_id, max_attempts=max_attempts, polling_interval=polling_interval
            )
        )

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
        upload_result = self.upload_sync(file_path=file_path)
        request_id = upload_result["request_id"]

        # Get the result
        return self.get_result_sync(request_id)

    async def poll_for_results(
        self,
        request_id: str,
        polling_interval: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
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
            self.on("result", cast(ResultHandler, on_result))
        if on_error:
            # Cast to ErrorHandler to satisfy type checker
            self.on("error", cast(ErrorHandler, on_error))

        # Create and run the polling task
        polling_task = self.poll_for_results(request_id, polling_interval, timeout)
        self._run_async(polling_task)  # Discard the return value

    @classmethod
    def _run_async(cls, coro: Coroutine[Any, Any, T]) -> T:
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

    async def cleanup(self) -> None:
        """
        Clean up resources used by the SDK

        This should be called when you're done using the SDK to ensure all resources
        are properly released.
        """
        if hasattr(self, "client") and self.client:
            await self.client.close()

    def cleanup_sync(self) -> None:
        """
        Synchronous version of cleanup

        This should be called when you're done using the SDK to ensure all resources
        are properly released.
        """
        self._run_async(self.cleanup())  # Discard the return value

    def __del__(self) -> None:
        """
        Destructor to ensure resources are cleaned up

        This will attempt to close any open sessions when the object is garbage collected.
        It's still recommended to explicitly call cleanup() or cleanup_sync() when done.
        """
        try:
            if hasattr(self, "client") and self.client:
                # We can't use asyncio directly in __del__, so we'll try our best
                # to clean up without relying on async operations
                if hasattr(self.client, "session") and self.client.session:
                    # Mark session for closing on GC - it's not perfect but better than nothing
                    self.client.session._closed = True
        except Exception:
            # Suppress any errors during cleanup
            pass
