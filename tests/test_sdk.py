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
    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=mock_client
    ):
        sdk = RealityDefender(api_key="test-api-key")
        sdk.client = mock_client
        return sdk


@pytest.mark.asyncio
async def test_sdk_initialization() -> None:
    """Test SDK initialization"""
    # Test with valid API key
    with patch(
        "realitydefender.reality_defender.create_http_client"
    ) as mock_create_client:
        sdk = RealityDefender(api_key="test-api-key")
        mock_create_client.assert_called_once()
        assert sdk.api_key == "test-api-key"

    # Test with missing API key
    with pytest.raises(RealityDefenderError) as exc_info:
        RealityDefender(api_key="")
    assert exc_info.value.code == "unauthorized"


@pytest.mark.asyncio
async def test_upload(sdk_instance: RealityDefender, mock_client: MagicMock) -> None:
    """Test file upload functionality"""
    # Setup mock response
    mock_client.post.return_value = {
        "requestId": "test-request-id",
        "mediaId": "test-media-id",
        "response": {"signedUrl": "https://signed-url.com"},
    }

    # Test with valid options
    with (
        patch(
            "realitydefender.detection.upload.get_file_info",
            return_value=("test.jpg", b"file_content", "image/jpeg"),
        ),
        patch("realitydefender.detection.upload.upload_to_signed_url"),
    ):
        result = await sdk_instance.upload(file_path="/path/to/test.jpg")
        assert result == {"request_id": "test-request-id", "media_id": "test-media-id"}

    # Test with error
    mock_client.post.side_effect = RealityDefenderError(
        "Upload failed", "upload_failed"
    )

    with pytest.raises(RealityDefenderError) as exc_info:
        await sdk_instance.upload(file_path="/path/to/test.jpg")
    assert exc_info.value.code in ["upload_failed", "invalid_file"]


@pytest.mark.asyncio
async def test_get_result(
    sdk_instance: RealityDefender, mock_client: MagicMock
) -> None:
    """Test getting detection results"""
    # Setup mock response
    mock_client.get.return_value = {
        "resultsSummary": {
            "status": "ARTIFICIAL",
            "metadata": {"finalScore": 95.5},
        },
        "models": [
            {
                "name": "model1",
                "status": "ARTIFICIAL",
                "finalScore": 97.3,
                "predictionNumber": 0.973,
            },
            {
                "name": "model2",
                "status": "COMPLETED",
                "predictionNumber": {
                    "reason": "relevance: no faces detected/faces too small",
                    "decision": "NOT_EVALUATED",
                },
                "normalizedPredictionNumber": None,
                "rollingAvgNumber": None,
                "finalScore": None,
            },
            {
                "name": "model3",
                "status": "NOT_APPLICABLE",
                "predictionNumber": {
                    "reason": "relevance: no faces detected/faces too small",
                    "decision": "NOT_EVALUATED",
                },
                "normalizedPredictionNumber": None,
                "rollingAvgNumber": None,
                "finalScore": None,
            },
        ],
    }

    # Test getting results
    result = await sdk_instance.get_result("test-request-id")
    assert result["status"] == "ARTIFICIAL"
    assert result["score"] == 0.955
    assert len(result["models"]) == 2
    assert [m["name"] for m in result["models"]] == ["model1", "model2"]
    assert [m["score"] for m in result["models"]] == [0.973, None]


@pytest.mark.asyncio
async def test_poll_for_results(
    sdk_instance: RealityDefender, mock_client: MagicMock
) -> None:
    """Test polling for results"""
    # Setup mock to return 'ANALYZING' first, then 'ARTIFICIAL'
    mock_client.get.side_effect = [
        {
            "resultsSummary": {"status": "ANALYZING", "metadata": {"finalScore": None}},
            "models": [],
        },
        {
            "resultsSummary": {
                "status": "ARTIFICIAL",
                "metadata": {"finalScore": 95.5},
            },
            "models": [
                {
                    "name": "model1",
                    "status": "ARTIFICIAL",
                    "finalScore": 97.3,
                    "predictionNumber": 0.973,
                },
                {"name": "model1", "status": "NOT_APPLICABLE", "finalScore": 0},
            ],
        },
    ]

    # Mock the emit method
    mock_emit = MagicMock()
    with patch.object(sdk_instance, "emit", mock_emit):
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
                "score": 0.955,
                "models": [{"name": "model1", "status": "ARTIFICIAL", "score": 0.973}],
            },
        )


@pytest.mark.asyncio
async def test_poll_for_results_error(
    sdk_instance: RealityDefender, mock_client: MagicMock
) -> None:
    """Test polling with errors"""
    # Set up error to be emitted
    mock_client.get.side_effect = RealityDefenderError("Not found", "not_found")

    # Mock the emit method
    mock_emit = MagicMock()
    with patch.object(sdk_instance, "emit", mock_emit):
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
        "requestId": "test-request-id",
        "mediaId": "test-media-id",
        "response": {"signedUrl": "https://signed-url.com"},
    }

    # Test direct upload function
    with (
        patch(
            "realitydefender.detection.upload.get_file_info",
            return_value=("test.jpg", b"file_content", "image/jpeg"),
        ),
        patch("realitydefender.detection.upload.upload_to_signed_url"),
    ):
        result = await upload_file(mock_client, file_path="/path/to/test.jpg")
        assert result == {"request_id": "test-request-id", "media_id": "test-media-id"}

    # Setup mock response for get_result
    mock_client.get.return_value = {
        "resultsSummary": {
            "status": "AUTHENTIC",
            "metadata": {"finalScore": 12.3},
        },
        "models": [
            {
                "name": "model1",
                "status": "AUTHENTIC",
                "finalScore": 97,
                "predictionNumber": 0.97,
            },
            {
                "name": "model2",
                "status": "COMPLETED",
                "predictionNumber": {
                    "reason": "relevance: no faces detected/faces too small",
                    "decision": "NOT_EVALUATED",
                },
                "normalizedPredictionNumber": None,
                "rollingAvgNumber": None,
                "finalScore": None,
            },
            {
                "name": "model3",
                "status": "NOT_APPLICABLE",
                "predictionNumber": {
                    "reason": "relevance: no faces detected/faces too small",
                    "decision": "NOT_EVALUATED",
                },
                "normalizedPredictionNumber": None,
                "rollingAvgNumber": None,
                "finalScore": None,
            },
        ],
    }

    # Test direct get_detection_result function
    detection_result = await get_detection_result(mock_client, "test-request-id")
    assert detection_result["status"] == "AUTHENTIC"
    assert abs((detection_result["score"] or 0) - 0.123) < 0.0001
    assert len(detection_result["models"]) == 2
    assert [m["score"] for m in detection_result["models"]] == [0.97, None]
