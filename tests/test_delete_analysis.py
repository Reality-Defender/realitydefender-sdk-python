"""Tests for deleting a scan analysis."""

from unittest.mock import AsyncMock, patch

import pytest

from realitydefender import RealityDefender, RealityDefenderError


@pytest.mark.asyncio
async def test_delete_analysis_calls_media_endpoint() -> None:
    client = AsyncMock()
    client.delete = AsyncMock(return_value=None)

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    await sdk.delete_analysis("  req-1  ")

    client.delete.assert_called_once_with("/api/media/req-1")


@pytest.mark.asyncio
async def test_delete_analysis_requires_request_id() -> None:
    client = AsyncMock()
    client.delete = AsyncMock()

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    with pytest.raises(RealityDefenderError) as exc_info:
        await sdk.delete_analysis("   ")

    assert exc_info.value.code == "invalid_request"
    client.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_analysis_propagates_not_found() -> None:
    client = AsyncMock()
    client.delete = AsyncMock(
        side_effect=RealityDefenderError("Resource not found", "not_found")
    )

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="test-key")
        sdk.client = client

    with pytest.raises(RealityDefenderError) as exc_info:
        await sdk.delete_analysis("missing")

    assert exc_info.value.code == "not_found"


def test_delete_analysis_sync() -> None:
    client = AsyncMock()
    client.delete = AsyncMock(return_value=None)

    with patch(
        "realitydefender.reality_defender.create_http_client", return_value=client
    ):
        sdk = RealityDefender(api_key="k")
        sdk.client = client
        sdk.delete_analysis_sync("req-sync")

    client.delete.assert_called_once_with("/api/media/req-sync")
