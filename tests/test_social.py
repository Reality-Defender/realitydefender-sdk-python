from unittest.mock import AsyncMock, patch

import pytest
import aiohttp

from realitydefender.client.http_client import HttpClient, create_http_client
from realitydefender.detection.social import upload_social_media_link
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


# Tests for upload_social_media_link function
@pytest.mark.asyncio
async def test_upload_social_media_link_success_return_type(
    http_client: HttpClient, mock_response: AsyncMock
) -> None:
    """Test successful social media link upload returns correct type"""
    mock_response.json = AsyncMock(
        return_value={
            "requestId": "test-request-id",
        }
    )

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result: UploadResult = await upload_social_media_link(
            http_client, "https://example.com/social-post"
        )

    # Verify return type matches UploadResult
    assert isinstance(result, dict)
    assert "request_id" in result
    assert "media_id" in result
    assert isinstance(result["request_id"], str)
    assert result["media_id"] is None
    assert result == {"request_id": "test-request-id", "media_id": None}


@pytest.mark.asyncio
async def test_upload_social_media_link_ensures_session(
    http_client: HttpClient, mock_response: AsyncMock
) -> None:
    """Test that upload_social_media_link calls ensure_session"""
    mock_response.json = AsyncMock(
        return_value={
            "requestId": "test-request-id",
        }
    )

    with (
        patch.object(http_client, "ensure_session") as mock_ensure_session,
        patch.object(
            http_client, "post", return_value={"requestId": "test-request-id"}
        ),
    ):
        await upload_social_media_link(http_client, "https://example.com/social-post")

        mock_ensure_session.assert_called_once()


@pytest.mark.asyncio
async def test_upload_social_media_link_posts_correct_data(
    http_client: HttpClient,
) -> None:
    """Test that upload_social_media_link posts with correct data format"""
    social_link = "https://example.com/social-post"

    with (
        patch.object(http_client, "ensure_session"),
        patch.object(
            http_client, "post", return_value={"requestId": "test-request-id"}
        ) as mock_post,
    ):
        await upload_social_media_link(http_client, social_link)

        mock_post.assert_called_once_with(
            "/api/files/social", data={"socialLink": social_link}
        )


@pytest.mark.asyncio
async def test_upload_social_media_link_reality_defender_error_propagation(
    http_client: HttpClient,
) -> None:
    """Test that RealityDefenderError is properly propagated with correct types"""
    original_error = RealityDefenderError("API error", "unauthorized")

    with (
        patch.object(http_client, "ensure_session"),
        patch.object(http_client, "post", side_effect=original_error),
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "unauthorized"
    assert str(raised_error) == "API error (Code: unauthorized)"


@pytest.mark.asyncio
async def test_upload_social_media_link_converts_generic_error_type(
    http_client: HttpClient,
) -> None:
    """Test that generic errors are converted to RealityDefenderError with correct type"""
    with (
        patch.object(http_client, "ensure_session"),
        patch.object(http_client, "post", side_effect=ValueError("Unexpected error")),
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "upload_failed"
    assert "Social media link upload failed: Unexpected error" in str(raised_error)


@pytest.mark.asyncio
async def test_upload_social_media_link_missing_request_id_handling(
    http_client: HttpClient,
) -> None:
    """Test handling of missing requestId in response"""
    with (
        patch.object(http_client, "ensure_session"),
        patch.object(http_client, "post", return_value={}),  # Empty response
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "server_error"
    assert "Invalid response from API - missing requestId" in str(raised_error)


@pytest.mark.asyncio
async def test_upload_social_media_link_none_request_id_handling(
    http_client: HttpClient,
) -> None:
    """Test handling of None requestId in response"""
    with (
        patch.object(http_client, "ensure_session"),
        patch.object(
            http_client, "post", return_value={"requestId": None}
        ),  # None value
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "server_error"


@pytest.mark.asyncio
async def test_upload_social_media_link_various_social_media_urls(
    http_client: HttpClient,
) -> None:
    """Test upload with various social media URL formats"""
    test_urls = [
        "https://twitter.com/user/status/123456",
        "https://facebook.com/posts/123456",
        "https://instagram.com/p/ABC123/",
        "https://tiktok.com/@user/video/123456",
        "https://youtube.com/watch?v=ABC123",
        "https://linkedin.com/posts/activity-123456",
    ]

    for url in test_urls:
        with (
            patch.object(http_client, "ensure_session"),
            patch.object(
                http_client, "post", return_value={"requestId": f"request-{hash(url)}"}
            ) as mock_post,
        ):
            result = await upload_social_media_link(http_client, url)

            assert result["request_id"] == f"request-{hash(url)}"
            assert result["media_id"] is None
            mock_post.assert_called_with("/api/files/social", data={"socialLink": url})


@pytest.mark.asyncio
async def test_upload_social_media_link_session_error_handling(
    http_client: HttpClient,
) -> None:
    """Test error handling when ensure_session fails"""
    with patch.object(
        http_client,
        "ensure_session",
        side_effect=RealityDefenderError("Session failed", "unauthorized"),
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "unauthorized"
    assert "Session failed" in str(raised_error)


@pytest.mark.asyncio
async def test_upload_social_media_link_http_error_handling(
    http_client: HttpClient,
) -> None:
    """Test handling of HTTP errors during post request"""
    with (
        patch.object(http_client, "ensure_session"),
        patch.object(
            http_client, "post", side_effect=aiohttp.ClientError("Connection failed")
        ),
    ):
        with pytest.raises(RealityDefenderError) as exc_info:
            await upload_social_media_link(
                http_client, "https://example.com/social-post"
            )

    raised_error: RealityDefenderError = exc_info.value
    assert isinstance(raised_error, RealityDefenderError)
    assert raised_error.code == "upload_failed"
    assert "Social media link upload failed: Connection failed" in str(raised_error)
