"""
Delete a scan request.
"""

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS
from realitydefender.errors import RealityDefenderError


async def delete_request(client: HttpClient, request_id: str) -> None:
    """
    Delete a scan request (DELETE ``/api/media/{request_id}``).

    The API responds with 204 No Content.

    Args:
        client: HTTP client for API requests
        request_id: Request ID returned by upload or social media upload

    Raises:
        RealityDefenderError: If the request id is missing or the API call fails
    """
    if not (request_id and str(request_id).strip()):
        raise RealityDefenderError("request_id is required", "invalid_request")

    await client.delete(f"{API_PATHS['DELETE_MEDIA']}/{str(request_id).strip()}")
