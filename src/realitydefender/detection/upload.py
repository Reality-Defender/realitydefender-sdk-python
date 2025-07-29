"""
File upload functionality for detection
"""

import os
from typing import Any, Dict

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS
from realitydefender.errors import RealityDefenderError
from realitydefender.model import UploadResult
from realitydefender.utils.file_utils import get_file_info


async def get_signed_url(client: HttpClient, filename: str) -> Dict[str, Any]:
    """
    Get a signed URL for uploading a file

    Args:
        client: HTTP client for API requests
        filename: Name of the file to upload

    Returns:
        Response containing signedUrl, requestId, and mediaId

    Raises:
        RealityDefenderError: If the request fails
    """
    try:
        response = await client.post(
            API_PATHS["SIGNED_URL"], data={"fileName": filename}
        )
        return response
    except Exception as e:
        if isinstance(e, RealityDefenderError):
            raise
        raise RealityDefenderError(
            f"Failed to get signed URL: {str(e)}", "unknown_error"
        )


async def upload_to_signed_url(
    client: HttpClient, signed_url: str, file_path: str
) -> None:
    """
    Upload file content to a signed URL

    Args:
        client: HTTP client for API requests
        signed_url: URL for uploading
        file_path: Path to the file to upload

    Raises:
        RealityDefenderError: If upload fails
    """
    try:
        # Get file information
        _, content, content_type = get_file_info(file_path)

        session = await client.ensure_session()

        # Upload directly to the signed URL
        async with session.put(
            signed_url, data=content, headers={"Content-Type": content_type}
        ) as response:
            if response.status >= 400:
                text = await response.text()
                raise RealityDefenderError(
                    f"Upload failed with status {response.status}: {text}",
                    "upload_failed",
                )
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(f"Upload failed: {str(e)}", "upload_failed")


async def upload_file(client: HttpClient, file_path: str) -> UploadResult:
    """
    Upload a file to Reality Defender for analysis

    Args:
        client: HTTP client for API requests
        file_path: Path to the file to upload

    Returns:
        Dictionary with request_id and media_id

    Raises:
        RealityDefenderError: If upload fails
    """
    if not file_path:
        raise RealityDefenderError("file_path is required for upload", "invalid_file")

    try:
        # Get the filename
        filename = os.path.basename(file_path)

        # Get signed URL
        signed_url_response = await get_signed_url(client, filename)

        # Handle regular API response format
        request_id: str = signed_url_response.get("requestId", "")
        media_id: str = signed_url_response.get("mediaId", "")
        signed_url = signed_url_response.get("response", {}).get("signedUrl", "")

        if not request_id or not media_id or not signed_url:
            raise RealityDefenderError(
                "Invalid response from API - missing requestId, mediaId, or signedUrl",
                "server_error",
            )

        # Upload to signed URL
        await upload_to_signed_url(client, signed_url, file_path)

        # Return result
        return {"request_id": request_id, "media_id": media_id}
    except RealityDefenderError:
        # Re-raise existing SDK errors
        raise
    except Exception as e:
        # Convert other errors to SDK errors
        raise RealityDefenderError(f"Upload failed: {str(e)}", "upload_failed")
