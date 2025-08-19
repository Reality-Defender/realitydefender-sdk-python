from realitydefender import UploadResult, RealityDefenderError
from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS


async def upload_social_media_link(
    client: HttpClient, social_media_link: str
) -> UploadResult:
    try:
        await client.ensure_session()

        response = await client.post(
            API_PATHS["SOCIAL_MEDIA"], data={"socialLink": social_media_link}
        )

        request_id = response.get("requestId", "")
        if not request_id:
            raise RealityDefenderError(
                "Invalid response from API - missing requestId",
                "server_error",
            )

        return {"request_id": request_id, "media_id": None}
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(
            f"Social media link upload failed: {str(e)}", "upload_failed"
        )
