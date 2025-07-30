"""
Tests for the main SDK functionality
"""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from realitydefender import (
    RealityDefender,
    RealityDefenderError,
    get_detection_result,
    upload_file,
)
from realitydefender.detection.results import (
    get_detection_results,
    format_result_list,
    get_media_results,
)


@pytest.fixture
def mock_client() -> AsyncMock:
    """Create a mock HTTP client"""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest_asyncio.fixture
async def sdk_instance(mock_client: AsyncMock) -> RealityDefender:
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
    sdk = RealityDefender(api_key="test-api-key")
    assert sdk.api_key == "test-api-key"
    assert sdk.client.base_url == "https://api.prd.realitydefender.xyz"
    assert sdk.client.api_key == "test-api-key"

    # Test with missing API key
    with pytest.raises(RealityDefenderError) as exc_info:
        RealityDefender(api_key="")
    assert exc_info.value.code == "unauthorized"


@pytest.mark.asyncio
async def test_upload(sdk_instance: RealityDefender, mock_client: AsyncMock) -> None:
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
    sdk_instance: RealityDefender, mock_client: AsyncMock
) -> None:
    """Test getting detection results"""
    # Setup mock response
    mock_client.get.return_value = {
        "resultsSummary": {
            "status": "FAKE",
            "metadata": {"finalScore": 95.5},
        },
        "models": [
            {
                "name": "model1",
                "status": "FAKE",
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
    assert result["status"] == "MANIPULATED"
    assert result["score"] == 0.955
    assert len(result["models"]) == 2
    assert [m["name"] for m in result["models"]] == ["model1", "model2"]
    assert [m["score"] for m in result["models"]] == [0.973, None]


@pytest.mark.asyncio
async def test_poll_for_results(
    sdk_instance: RealityDefender, mock_client: AsyncMock
) -> None:
    """Test polling for results"""
    # Setup mock to return 'ANALYZING' first, then 'MANIPULATED'
    mock_client.get.side_effect = [
        {
            "requestId": "test-request-id-1",
            "resultsSummary": {"status": "ANALYZING", "metadata": {"finalScore": None}},
            "models": [],
        },
        {
            "requestId": "test-request-id-2",
            "resultsSummary": {
                "status": "FAKE",
                "metadata": {"finalScore": 95.5},
            },
            "models": [
                {
                    "name": "model1",
                    "status": "FAKE",
                    "finalScore": 97.3,
                    "predictionNumber": 0.973,
                },
                {"name": "model1", "status": "NOT_APPLICABLE", "finalScore": 0},
            ],
        },
    ]

    # Mock the emit method
    mock_emit = AsyncMock()
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
                "request_id": "test-request-id-2",
                "status": "MANIPULATED",
                "score": 0.955,
                "models": [{"name": "model1", "status": "MANIPULATED", "score": 0.973}],
            },
        )


@pytest.mark.asyncio
async def test_poll_for_results_error(
    sdk_instance: RealityDefender, mock_client: AsyncMock
) -> None:
    """Test polling with errors"""
    # Set up error to be emitted
    mock_client.get.side_effect = RealityDefenderError("Not found", "not_found")

    # Mock the emit method
    mock_emit = AsyncMock()
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
async def test_direct_functions(mock_client: AsyncMock) -> None:
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


@pytest.mark.asyncio
async def test_get_media_results_success(mock_client: AsyncMock) -> None:
    """Test successful media results retrieval"""
    mock_response = {"totalItems": 10, "mediaList": []}
    mock_client.get.return_value = mock_response

    result = await get_media_results(mock_client, page_number=1, size=5)

    mock_client.get.assert_called_once_with(
        path="/api/v2/media/users/pages/1", params={"size": "5"}
    )
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_media_results_with_filters(mock_client: AsyncMock) -> None:
    """Test media results with date and name filters"""
    mock_client.get.return_value = {"totalItems": 1, "mediaList": []}

    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)

    await get_media_results(
        mock_client, name="test", start_date=start_date, end_date=end_date
    )

    mock_client.get.assert_called_once_with(
        path="/api/v2/media/users/pages/0",
        params={
            "size": "10",
            "name": "test",
            "startDate": "2023-01-01",
            "endDate": "2023-12-31",
        },
    )


@pytest.mark.asyncio
async def test_get_media_results_error_handling(mock_client: AsyncMock) -> None:
    """Test error handling in get_media_results"""
    mock_client.get.side_effect = Exception("Network error")

    with pytest.raises(RealityDefenderError) as exc_info:
        await get_media_results(mock_client)

    assert exc_info.value.code == "unknown_error"


def test_format_result_list_success() -> None:
    """Test successful formatting of result list"""
    response = {
        "totalItems": 1,
        "totalPages": 1,
        "currentPage": 0,
        "currentPageItemsCount": 1,
        "mediaList": [
            {
                "resultsSummary": {"status": "REAL", "metadata": {"finalScore": 10}},
                "models": [{"name": "face", "status": "REAL", "predictionNumber": 0.1}],
            }
        ],
    }

    result = format_result_list(response)

    assert result["total_items"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["status"] == "REAL"


@pytest.mark.asyncio
async def test_get_detection_results_success(mock_client: AsyncMock) -> None:
    """Test successful detection results retrieval"""
    mock_response = {
        "totalItems": 1,
        "totalPages": 1,
        "currentPage": 0,
        "currentPageItemsCount": 1,
        "mediaList": [
            {
                "resultsSummary": {
                    "status": "AUTHENTIC",
                    "metadata": {"finalScore": 10},
                },
                "models": [
                    {"name": "face", "status": "AUTHENTIC", "predictionNumber": 0.1}
                ],
            }
        ],
    }
    mock_client.get.return_value = mock_response

    result = await get_detection_results(mock_client)

    assert result["total_items"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["status"] == "AUTHENTIC"
    assert result["items"][0]["score"] == 0.1


@pytest.mark.asyncio
async def test_get_detection_results_retry_logic(mock_client: AsyncMock) -> None:
    """Test retry logic in get_detection_results"""
    mock_client.get.side_effect = [
        RealityDefenderError("Temporary error", "server_error"),
        {
            "totalItems": 1,
            "totalPages": 1,
            "currentPage": 0,
            "currentPageItemsCount": 1,
            "mediaList": [],
        },
    ]

    result = await get_detection_results(
        mock_client, max_attempts=2, polling_interval=1
    )

    assert mock_client.get.call_count == 2
    assert result["total_items"] == 1


@pytest.mark.asyncio
async def test_get_detection_results_error_handling(mock_client: AsyncMock) -> None:
    """Test error handling in get_detection_results"""
    mock_client.get.side_effect = Exception("Network error")

    with pytest.raises(RealityDefenderError) as exc_info:
        await get_detection_results(mock_client, max_attempts=2, polling_interval=1)

    assert exc_info.value.code == "unknown_error"
