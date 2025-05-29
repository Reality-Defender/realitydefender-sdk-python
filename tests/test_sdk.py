"""
Tests for the main SDK functionality
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from realitydefender import (
    RealityDefender,
    RealityDefenderError,
    get_detection_result,
    upload_file,
)


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock HTTP client"""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest_asyncio.fixture
async def sdk_instance(mock_client: MagicMock) -> RealityDefender:
    """Create a patched SDK instance with a mock client"""
    with patch("realitydefender.create_http_client", return_value=mock_client):
        sdk = RealityDefender({"api_key": "test-api-key"})
        sdk.client = mock_client
        return sdk


@pytest.mark.asyncio
async def test_sdk_initialization() -> None:
    """Test SDK initialization"""
    # Test with valid API key
    with patch("realitydefender.create_http_client") as mock_create_client:
        sdk = RealityDefender({"api_key": "test-api-key"})
        mock_create_client.assert_called_once()
        assert sdk.api_key == "test-api-key"

    # Test with missing API key
    with pytest.raises(RealityDefenderError) as exc_info:
        RealityDefender({})
    assert exc_info.value.code == "unauthorized"


@pytest.mark.asyncio
async def test_upload(sdk_instance: RealityDefender, mock_client: MagicMock) -> None:
    """Test file upload functionality"""
    # Setup mock response
    mock_client.post.return_value = {
        "data": {"request_id": "test-request-id", "media_id": "test-media-id"}
    }

    # Test with valid options
    with patch(
        "realitydefender.detection.upload.get_file_info",
        return_value=("test.jpg", b"file_content", "image/jpeg"),
    ):
        result = await sdk_instance.upload({"file_path": "/path/to/test.jpg"})
        assert result == {"request_id": "test-request-id", "media_id": "test-media-id"}

    # Test with error
    mock_client.post.side_effect = RealityDefenderError(
        "Upload failed", "upload_failed"
    )

    with pytest.raises(RealityDefenderError) as exc_info:
        await sdk_instance.upload({"file_path": "/path/to/test.jpg"})
    assert exc_info.value.code in ["upload_failed", "invalid_file"]


@pytest.mark.asyncio
async def test_get_result(sdk_instance: RealityDefender, mock_client: MagicMock) -> None:
    """Test getting detection results"""
    # Setup mock response
    mock_client.get.return_value = {
        "data": {
            "status": "ARTIFICIAL",
            "score": 95.5,
            "models": [{"name": "model1", "status": "ARTIFICIAL", "score": 97.3}],
        }
    }

    # Test getting results
    result = await sdk_instance.get_result("test-request-id")
    assert result["status"] == "ARTIFICIAL"
    assert result["score"] == 95.5
    assert len(result["models"]) == 1
    assert result["models"][0]["name"] == "model1"


@pytest.mark.asyncio
async def test_poll_for_results(sdk_instance: RealityDefender, mock_client: MagicMock) -> None:
    """Test polling for results"""
    # Setup mock to return 'ANALYZING' first, then 'ARTIFICIAL'
    mock_client.get.side_effect = [
        {"data": {"status": "ANALYZING", "score": None, "models": []}},
        {
            "data": {
                "status": "ARTIFICIAL",
                "score": 95.5,
                "models": [{"name": "model1", "status": "ARTIFICIAL", "score": 97.3}],
            }
        },
    ]

    # Mock the emit method
    mock_emit = MagicMock()
    with patch.object(sdk_instance, 'emit', mock_emit):
        # Test polling
        with patch("asyncio.sleep", AsyncMock()):
            task = sdk_instance.poll_for_results(
                "test-request-id", polling_interval=10, timeout=1000
            )
            await task

        # Check that emit was called with the result
        mock_emit.assert_called_with(
            "result",
            {
                "status": "ARTIFICIAL",
                "score": 95.5,
                "models": [{"name": "model1", "status": "ARTIFICIAL", "score": 97.3}],
            },
        )


@pytest.mark.asyncio
async def test_poll_for_results_error(sdk_instance: RealityDefender, mock_client: MagicMock) -> None:
    """Test polling with errors"""
    # Set up error to be emitted
    mock_client.get.side_effect = RealityDefenderError("Not found", "not_found")

    # Mock the emit method
    mock_emit = MagicMock()
    with patch.object(sdk_instance, 'emit', mock_emit):
        # Test polling with not_found error
        with patch("asyncio.sleep", AsyncMock()):
            with patch("realitydefender.core.constants.DEFAULT_MAX_ATTEMPTS", 2):
                task = sdk_instance.poll_for_results(
                    "test-request-id", polling_interval=10, timeout=1000
                )
                await task

        # Check that error was emitted
        assert mock_emit.call_args[0][0] == "error"
        assert isinstance(mock_emit.call_args[0][1], RealityDefenderError)
        assert mock_emit.call_args[0][1].code == "timeout"


@pytest.mark.asyncio
async def test_direct_functions(mock_client: MagicMock) -> None:
    """Test direct function usage"""
    # Setup mock response for upload
    mock_client.post.return_value = {
        "data": {"request_id": "test-request-id", "media_id": "test-media-id"}
    }

    # Test direct upload function
    with patch(
        "realitydefender.detection.upload.get_file_info",
        return_value=("test.jpg", b"file_content", "image/jpeg"),
    ):
        result = await upload_file(mock_client, {"file_path": "/path/to/test.jpg"})
        assert result == {"request_id": "test-request-id", "media_id": "test-media-id"}

    # Setup mock response for get_result
    mock_client.get.return_value = {
        "data": {
            "status": "AUTHENTIC",
            "score": 12.3,
            "models": [{"name": "model1", "status": "AUTHENTIC", "score": 8.1}],
        }
    }

    # Test direct get_detection_result function
    result = await get_detection_result(mock_client, "test-request-id")
    assert result["status"] == "AUTHENTIC"
    assert result["score"] == 12.3
    assert len(result["models"]) == 1
