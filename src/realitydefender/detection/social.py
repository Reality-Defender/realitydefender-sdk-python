from urllib.parse import urlparse
import validators

from realitydefender import UploadResult, RealityDefenderError
from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS


async def upload_social_media_link(
    client: HttpClient, social_media_link: str
) -> UploadResult:
    if not social_media_link or social_media_link.strip() == "":
        raise RealityDefenderError(
            "Social media link is required", "invalid_request"
        )

    try:
        # Check if this is an actual URL.
        parse_result = urlparse(social_media_link)
        if not all([
            parse_result.scheme in ('http', 'https'),
            parse_result.netloc,
            len(parse_result.netloc.strip()) > 0
        ]):
            raise RealityDefenderError(
                f"Invalid social media link: {social_media_link}",
                "invalid_request",
            )

        if not validators.domain(parse_result.netloc):
            raise Exception()
    except Exception:
        raise RealityDefenderError(
            f"Invalid social media link: {social_media_link}",
            "invalid_request",
        )

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
