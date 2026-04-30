"""Tests for user feedback API helpers."""

from unittest.mock import AsyncMock, patch

import pytest

from realitydefender import RealityDefender, RealityDefenderError


def _feedback_response(**overrides: object) -> dict[str, object]:
    response: dict[str, object] = {
        "id": "fb-1",
        "userId": "user-1",
        "requestId": "req-a",
        "institutionId": "inst-1",
        "category": "CONFIRMATION",
        "label": "REAL",
        "createdAt": "2026-01-01T00:00:00.000Z",
        "text": None,
        "userName": None,
        "userEmail": "user@example.com",
        "orgName": "Reality Defender",
        "mediaType": "VIDEO",
        "mediaViewUrl": "https://app.example/media/req-a",
        "mediaSource": "API",
    }
    response.update(overrides)
    return response


@pytest.mark.asyncio
async def test_create_user_feedback_posts_json() -> None:
    client = AsyncMock()
    client.post = AsyncMock(return_value=_feedback_response())

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    out = await sdk.create_user_feedback(
        "req-a",
        "REAL",
        "CONFIRMATION",
        comment="ok",
    )

    client.post.assert_called_once_with(
        "/api/v2/user-feedback",
        json={
            "requestId": "req-a",
            "label": "REAL",
            "feedbackCategory": "CONFIRMATION",
            "comment": "ok",
        },
    )
    assert out["requestId"] == "req-a"


@pytest.mark.asyncio
async def test_create_user_feedback_omits_comment_when_none() -> None:
    client = AsyncMock()
    client.post = AsyncMock(
        return_value=_feedback_response(
            id="fb-2",
            requestId="req-b",
            category="FALSE_NEGATIVE",
            label="SYNTHETIC",
            text=None,
        )
    )

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    await sdk.create_user_feedback(
        "req-b",
        "SYNTHETIC",
        "FALSE_NEGATIVE",
    )

    client.post.assert_called_once_with(
        "/api/v2/user-feedback",
        json={
            "requestId": "req-b",
            "label": "SYNTHETIC",
            "feedbackCategory": "FALSE_NEGATIVE",
        },
    )


@pytest.mark.asyncio
async def test_create_user_feedback_raises_when_response_missing_required_fields() -> (
    None
):
    client = AsyncMock()
    client.post = AsyncMock(return_value={"id": "fb-only"})

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    with pytest.raises(RealityDefenderError) as exc_info:
        await sdk.create_user_feedback(
            "req-z",
            "REAL",
            "OTHER",
        )

    assert exc_info.value.code == "server_error"
    assert "requestId" in str(exc_info.value)


def test_create_user_feedback_sync() -> None:
    client = AsyncMock()
    client.post = AsyncMock(
        return_value=_feedback_response(
            id="sync",
            requestId="r1",
            category="OTHER",
            label="UNKNOWN",
        )
    )

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="k")
        sdk.client = client
        result = sdk.create_user_feedback_sync("r1", "UNKNOWN", "OTHER")

    assert result["requestId"] == "r1"
    client.post.assert_called_once()
