"""
User feedback API helpers — validate inputs, POST, then validate required fields on the response before returning.
"""

from typing import Any, Dict, Optional, cast

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import API_PATHS
from realitydefender.errors import RealityDefenderError
from realitydefender.model import FeedbackLabel, UserFeedback, UserFeedbackCategory


def _user_feedback_from_api_response(raw: Dict[str, Any]) -> UserFeedback:
    """Validate JSON from POST /user-feedback and build a :class:`UserFeedback`."""
    required_fields = (
        "id",
        "userId",
        "requestId",
        "institutionId",
        "category",
        "label",
        "createdAt",
    )
    missing = [field for field in required_fields if raw.get(field) is None]
    if missing:
        raise RealityDefenderError(
            f"Invalid response from API - missing {', '.join(missing)}",
            "server_error",
        )

    feedback: UserFeedback = {
        "id": str(raw["id"]),
        "userId": str(raw["userId"]),
        "requestId": str(raw["requestId"]),
        "institutionId": str(raw["institutionId"]),
        "category": cast(UserFeedbackCategory, raw["category"]),
        "label": cast(FeedbackLabel, raw["label"]),
        "createdAt": str(raw["createdAt"]),
    }

    if "text" in raw:
        feedback["text"] = None if raw["text"] is None else str(raw["text"])
    if "userName" in raw:
        feedback["userName"] = None if raw["userName"] is None else str(raw["userName"])
    if "userEmail" in raw:
        feedback["userEmail"] = (
            None if raw["userEmail"] is None else str(raw["userEmail"])
        )
    if "orgName" in raw:
        feedback["orgName"] = None if raw["orgName"] is None else str(raw["orgName"])
    if "mediaType" in raw:
        feedback["mediaType"] = (
            None if raw["mediaType"] is None else str(raw["mediaType"])
        )
    if "mediaViewUrl" in raw:
        feedback["mediaViewUrl"] = (
            None if raw["mediaViewUrl"] is None else str(raw["mediaViewUrl"])
        )
    if "mediaSource" in raw:
        feedback["mediaSource"] = (
            None if raw["mediaSource"] is None else str(raw["mediaSource"])
        )

    return feedback


async def create_user_feedback(
    client: HttpClient,
    *,
    request_id: str,
    label: FeedbackLabel,
    feedback_category: UserFeedbackCategory,
    comment: Optional[str] = None,
) -> UserFeedback:
    """
    Submit user feedback for a completed scan result (POST ``/api/v2/user-feedback``).

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
        raw: Dict[str, Any] = await client.post(
            API_PATHS["USER_FEEDBACK"], json=payload
        )
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(
            f"User feedback submission failed: {str(e)}", "upload_failed"
        )

    return _user_feedback_from_api_response(raw)
