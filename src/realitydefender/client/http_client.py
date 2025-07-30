"""
HTTP client for making requests to the Reality Defender API
"""

import json
from typing import Any, Dict, Optional, Tuple, TypedDict

import aiohttp
import ssl
import certifi

from realitydefender.core.constants import DEFAULT_API_ENDPOINT
from realitydefender.errors import RealityDefenderError


class ClientConfig(TypedDict, total=False):
    """Configuration for HTTP client"""

    api_key: str
    base_url: Optional[str]


class HttpClient:
    """
    HTTP client for Reality Defender API
    """

    def __init__(self, config: ClientConfig):
        """
        Initialize the HTTP client

        Args:
            config: Configuration including API key and base URL
        """
        self.api_key = config["api_key"]
        self.base_url = config.get("base_url") or DEFAULT_API_ENDPOINT
        self.session: Optional[aiohttp.ClientSession] = None

    async def ensure_session(self) -> aiohttp.ClientSession:
        """
        Ensure an HTTP session exists or create one

        Returns:
            Active aiohttp.ClientSession
        """
        if self.session is None or self.session.closed:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            conn = aiohttp.TCPConnector(ssl=ssl_context)

            self.session = aiohttp.ClientSession(
                connector=conn,
                headers={
                    "X-API-KEY": self.api_key,
                    "Accept": "application/json",
                },
            )
        return self.session

    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            RealityDefenderError: If the request fails
        """
        session = await self.ensure_session()
        url = f"{self.base_url}{path}"

        try:
            async with session.get(url, params=params) as response:
                return await self._handle_response(response)
        except aiohttp.ClientError as e:
            raise RealityDefenderError(f"HTTP request failed: {str(e)}", "server_error")

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Tuple[str, bytes, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API

        Args:
            path: API endpoint path
            data: Request body data
            files: Files to upload

        Returns:
            Response data as dictionary

        Raises:
            RealityDefenderError: If the request fails
        """
        session = await self.ensure_session()
        url = f"{self.base_url}{path}"

        form_data = aiohttp.FormData()

        # Add regular data
        if data:
            for key, value in data.items():
                form_data.add_field(key, str(value))

        # Add files
        if files:
            for field_name, (filename, content, content_type) in files.items():
                form_data.add_field(
                    field_name, content, filename=filename, content_type=content_type
                )

        try:
            async with session.post(url, data=form_data) as response:
                return await self._handle_response(response)
        except aiohttp.ClientError as e:
            raise RealityDefenderError(f"HTTP request failed: {str(e)}", "server_error")

    async def _handle_response(
        self, client_response: aiohttp.ClientResponse
    ) -> Dict[str, Any]:
        """
        Handle HTTP response and check for errors

        Args:
            client_response: HTTP response from aiohttp

        Returns:
            Parsed JSON response

        Raises:
            RealityDefenderError: If the response contains an error
        """
        json_content: Dict[str, Any] | None = None
        code: str
        response: str
        try:
            json_content = await client_response.json()
            code = json_content.get("code") or ""
            response = json_content.get("response") or "Unknown error"
        except json.JSONDecodeError:
            text_content: str = await client_response.text()
            code = ""
            response = text_content

        # Handle error responses.
        if client_response.status == 400:
            if code in ["free-tier-not-allowed", "upload-limit-reached"]:
                raise RealityDefenderError(response, "unauthorized")
            else:
                raise RealityDefenderError(
                    f"Invalid request: {response}", "invalid_request"
                )

        elif client_response.status == 401:
            raise RealityDefenderError("Invalid API key", "unauthorized")

        elif client_response.status == 404:
            raise RealityDefenderError("Resource not found", "not_found")

        elif client_response.status > 400:
            # Anything else is a generic API error, originated from the server.
            raise RealityDefenderError(f"API error: {response}", "server_error")

        elif json_content is None:
            raise RealityDefenderError(
                f"Invalid JSON response: {response}", "server_error"
            )

        # Return response unchanged.
        return json_content

    async def close(self) -> None:
        """Close the HTTP session if it exists"""
        if self.session and not self.session.closed:
            await self.session.close()


def create_http_client(config: ClientConfig) -> HttpClient:
    """
    Create a new HTTP client for the Reality Defender API

    Args:
        config: Client configuration including API key

    Returns:
        Configured HTTP client
    """
    return HttpClient(config)
