import os
import tempfile
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, patch

import pytest
import aiohttp

from realitydefender.client.http_client import HttpClient, create_http_client
from realitydefender.detection.upload import (
    get_signed_url,
    upload_to_signed_url,
    upload_file,
)
from realitydefender.errors import RealityDefenderError
from realitydefender.model import UploadResult


@pytest.fixture
def http_client() -> HttpClient:
    """Create an HTTP client for testing"""
    return create_http_client({"api_key": "test-api-key"})


@pytest.fixture
def mock_response() -> AsyncMock:
    """Create a mock aiohttp.ClientResponse"""
    mock = AsyncMock(spec=aiohttp.ClientResponse)
    mock.status = 200
    mock.json = AsyncMock(return_value={"data": {"test": "value"}})
    mock.text = AsyncMock(return_value="response text")
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def temp_test_file() -> Generator[str, Any, None]:
    """Create a temporary test file and return its path"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# Tests for get_signed_url function
@pytest.mark.asyncio
async def test_get_signed_url_success_return_type(
    http_client: HttpClient, mock_response: AsyncMock
) -> None:
    """Test successful signed URL retrieval returns correct type"""
    mock_response.json = AsyncMock(
        return_value={
            "requestId": "test-request-id",
            "mediaId": "test-media-id",
            "response": {"signedUrl": "https://signed-url.com"},
        }
    )

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result: Dict[str, Any] = await get_signed_url(http_client, "test.jpg")

    assert isinstance(result, dict)
    assert "requestId" in result
    assert "mediaId" in result
    assert "response" in result


@pytest.mark.asyncio
async def test_get_signed_url_reality_defender_error_propagation(
    http_client: HttpClient, mock_response: AsyncMock
) -> None:
    """Test that RealityDefenderError is properly propagated with correct types"""
    original_error = RealityDefenderError("API error", "unauthorized")

    with patch("aiohttp.ClientSession.post", side_effect=original_error):
        with pytest.raises(RealityDefenderError) as exc_info:
            await get_signed_url(http_client, "test.jpg")

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "unauthorized"
    assert str(raised_error) == "API error (Code: unauthorized)"


@pytest.mark.asyncio
async def test_upload_to_signed_url_success_return_type(
    http_client: HttpClient, mock_response: AsyncMock, temp_test_file: str
) -> None:
    with patch("realitydefender.detection.upload.get_file_info") as mock_get_file_info:
        mock_get_file_info.return_value = ("test.txt", b"test content", "text/plain")

        with patch("aiohttp.ClientSession.put", return_value=mock_response) as session:
            await upload_to_signed_url(
                http_client, "https://signed-url.com", temp_test_file
            )
            session.assert_called_once_with(
                "https://signed-url.com",
                data=b"test content",
                headers={"Content-Type": "text/plain"},
            )


@pytest.mark.asyncio
async def test_upload_file_success_test_format_return_type(
    http_client: HttpClient, temp_test_file: str
) -> None:
    """Test successful file upload with test mock response format returns correct type"""
    # Mock get_signed_url response with test format
    signed_url_response: Dict[str, Any] = {
        "requestId": "test-request-id",
        "mediaId": "test-media-id",
        "response": {"signedUrl": "https://signed-url.com"},
    }

    with (
        patch("realitydefender.detection.upload.get_signed_url") as mock_get_signed_url,
        patch("realitydefender.detection.upload.upload_to_signed_url"),
    ):
        mock_get_signed_url.return_value = signed_url_response

        result: UploadResult = await upload_file(http_client, file_path=temp_test_file)

        # Verify return type matches UploadResult
        assert isinstance(result, dict)
        assert "request_id" in result
        assert "media_id" in result
        assert isinstance(result["request_id"], str)
        assert isinstance(result["media_id"], str)
        assert result == {"request_id": "test-request-id", "media_id": "test-media-id"}


@pytest.mark.asyncio
async def test_upload_file_invalid_api_response_exception_type(
    http_client: HttpClient, temp_test_file: str
) -> None:
    """Test upload failure with invalid API response raises correct exception type"""
    # Mock get_signed_url response missing required fields
    signed_url_response: Dict[str, Any] = {
        "requestId": "test-request-id"
        # Missing mediaId and response.signedUrl
    }

    with patch(
        "realitydefender.detection.upload.get_signed_url"
    ) as mock_get_signed_url:
        mock_get_signed_url.return_value = signed_url_response

        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_file(http_client, file_path=temp_test_file)

        raised_error: RealityDefenderError = exc_info.value
        assert isinstance(raised_error, RealityDefenderError)
        assert raised_error.code == "server_error"
        assert "Invalid response from API" in str(raised_error)


@pytest.mark.asyncio
async def test_upload_file_converts_generic_error_type(
    http_client: HttpClient, temp_test_file: str
) -> None:
    """Test that generic errors are converted to RealityDefenderError with correct type"""
    with patch(
        "realitydefender.detection.upload.get_signed_url"
    ) as mock_get_signed_url:
        mock_get_signed_url.side_effect = ValueError("Unexpected error")

        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_file(http_client, file_path=temp_test_file)

        raised_error: RealityDefenderError = exc_info.value
        assert isinstance(raised_error, RealityDefenderError)
        assert raised_error.code == "upload_failed"
        assert "Upload failed: Unexpected error" in str(raised_error)


@pytest.mark.asyncio
async def test_upload_file_empty_strings_handling(http_client: HttpClient) -> None:
    """Test handling of empty string values in responses"""
    signed_url_response: Dict[str, Any] = {
        "requestId": "",  # Empty string
        "mediaId": "test-media-id",
        "response": {"signedUrl": "https://signed-url.com"},
    }

    with patch(
        "realitydefender.detection.upload.get_signed_url"
    ) as mock_get_signed_url:
        mock_get_signed_url.return_value = signed_url_response
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_file(http_client, file_path="/some/path")

        raised_error: RealityDefenderError = exc_info.value
        assert isinstance(raised_error, RealityDefenderError)
        assert raised_error.code == "server_error"


@pytest.mark.asyncio
async def test_upload_file_none_values_handling(http_client: HttpClient) -> None:
    """Test handling of None values in responses"""
    signed_url_response: Dict[str, Any] = {
        "requestId": "test-request-id",
        "mediaId": None,  # None value
        "response": {"signedUrl": "https://signed-url.com"},
    }

    with patch(
        "realitydefender.detection.upload.get_signed_url"
    ) as mock_get_signed_url:
        mock_get_signed_url.return_value = signed_url_response
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_file(http_client, file_path="/some/path")

        raised_error: RealityDefenderError = exc_info.value
        assert isinstance(raised_error, RealityDefenderError)
        assert raised_error.code == "server_error"
