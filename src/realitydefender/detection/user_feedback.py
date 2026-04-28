"""
User feedback (V2) API helpers — mirrors detection/social.py (validate, then POST).
"""

from typing import Any, Dict, Optional

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS
from realitydefender.errors import RealityDefenderError
from realitydefender.model import FeedbackLabel, UserFeedbackCategory, UserFeedbackV2


async def create_user_feedback_v2(
    client: HttpClient,
    *,
    request_id: str,
    label: FeedbackLabel,
    feedback_category: UserFeedbackCategory,
    comment: Optional[str] = None,
) -> UserFeedbackV2:
    """
    Submit user feedback V2 for a completed scan result (POST ``/api/v2/user-feedback``).

    Args:
        client: SDK HTTP client
        request_id: Media / detection request ID
        label: Content judgment (REAL, SYNTHETIC, …)
        feedback_category: Why you are submitting feedback
        comment: Optional free-text note

    Returns:
        Created feedback record from the API
    """
    if not (request_id and str(request_id).strip()):
        raise RealityDefenderError("request_id is required", "invalid_request")
    if not (label and str(label).strip()):
        raise RealityDefenderError("label is required", "invalid_request")
    if not (feedback_category and str(feedback_category).strip()):
        raise RealityDefenderError("feedback_category is required", "invalid_request")

    payload: Dict[str, Any] = {
        "requestId": request_id.strip(),
        "label": label,
        "feedbackCategory": feedback_category,
    }
    if comment is not None:
        payload["comment"] = comment

    try:
        await client.ensure_session()

        result = await client.post(
            API_PATHS["USER_FEEDBACK_V2"], json=payload
        )
        return result  # type: ignore[return-value]
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(
            f"User feedback submission failed: {str(e)}", "upload_failed"
        )
