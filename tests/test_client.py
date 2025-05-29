"""
Tests for the HTTP client module
"""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from realitydefender.client.http_client import HttpClient, create_http_client
from realitydefender.errors import RealityDefenderError


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


@pytest.mark.asyncio
async def test_create_http_client() -> None:
    """Test creating an HTTP client"""
    client = create_http_client({"api_key": "test-api-key"})
    assert isinstance(client, HttpClient)
    assert client.api_key == "test-api-key"

    # Test with custom base_url
    client = create_http_client(
        {"api_key": "test-api-key", "base_url": "https://custom-api.example.com"}
    )
    assert client.base_url == "https://custom-api.example.com"


@pytest.mark.asyncio
async def test_ensure_session(http_client: HttpClient) -> None:
    """Test that ensure_session creates a session when needed"""
    assert http_client.session is None

    session = await http_client.ensure_session()
    assert session is not None
    assert http_client.session is not None
    assert session is http_client.session

    # Test that it reuses the existing session
    second_session = await http_client.ensure_session()
    assert second_session is session


@pytest.mark.asyncio
async def test_get_success(http_client: HttpClient, mock_response: AsyncMock) -> None:
    """Test successful GET request"""
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await http_client.get("/test")
        assert result == {"data": {"test": "value"}}


@pytest.mark.asyncio
async def test_get_error(http_client: HttpClient, mock_response: AsyncMock) -> None:
    """Test GET request with error status"""
    mock_response.status = 404

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(RealityDefenderError) as exc_info:
            await http_client.get("/test")

        assert exc_info.value.code == "not_found"

    # Test unauthorized error
    mock_response.status = 401

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(RealityDefenderError) as exc_info:
            await http_client.get("/test")

        assert exc_info.value.code == "unauthorized"


@pytest.mark.asyncio
async def test_post_success(http_client: HttpClient, mock_response: AsyncMock) -> None:
    """Test successful POST request"""
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result = await http_client.post(
            "/test",
            data={"key": "value"},
            files={"file": ("filename.jpg", b"content", "image/jpeg")},
        )
        assert result == {"data": {"test": "value"}}


@pytest.mark.asyncio
async def test_post_error(http_client: HttpClient, mock_response: AsyncMock) -> None:
    """Test POST request with error"""
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={"error": {"message": "Server error"}})

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        with pytest.raises(RealityDefenderError) as exc_info:
            await http_client.post("/test")

        assert exc_info.value.code == "server_error"
        assert "Server error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_network_error(http_client: HttpClient) -> None:
    """Test handling of network errors"""
    with patch(
        "aiohttp.ClientSession.get", side_effect=aiohttp.ClientError("Network error")
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await http_client.get("/test")

        assert exc_info.value.code == "server_error"
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_close(http_client: HttpClient) -> None:
    """Test closing the client session"""
    # Create a mock session
    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    # Replace the client's session with our mock
    http_client.session = mock_session

    # Close it
    await http_client.close()

    # Verify the session was closed
    mock_session.close.assert_called_once()
