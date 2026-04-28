"""Tests for user feedback API helpers."""

from unittest.mock import AsyncMock, patch

import pytest

from realitydefender import RealityDefender


@pytest.mark.asyncio
async def test_create_user_feedback_posts_json() -> None:
    client = AsyncMock()
    client.post = AsyncMock(
        return_value={"id": "fb-1", "requestId": "req-a", "category": "CONFIRMATION"}
    )

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
    client.post = AsyncMock(return_value={"id": "fb-2"})

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


def test_create_user_feedback_sync() -> None:
    client = AsyncMock()
    client.post = AsyncMock(return_value={"id": "sync", "requestId": "r1"})

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="k")
        sdk.client = client
        result = sdk.create_user_feedback_sync("r1", "UNKNOWN", "OTHER")

    assert result["requestId"] == "r1"
    client.post.assert_called_once()
