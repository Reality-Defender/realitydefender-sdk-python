"""
Detection results retrieval and processing
"""

from typing import Any, Dict, TypeVar

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import (
    API_PATHS,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_POLLING_INTERVAL,
)
from realitydefender.errors import RealityDefenderError
from realitydefender.types import DetectionResult, ModelResult
from realitydefender.utils.async_utils import sleep

# Generic type for the HTTP client
ClientType = TypeVar("ClientType", bound=HttpClient)


async def get_media_result(client: ClientType, request_id: str) -> Dict[str, Any]:
    """
    Get the raw media result from the API

    Args:
        client: HTTP client for API requests
        request_id: The request ID to get results for

    Returns:
        Raw API response

    Raises:
        RealityDefenderError: If the request fails
    """
    try:
        path = f"{API_PATHS['MEDIA_RESULT']}/{request_id}"
        return await client.get(path)
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(f"Failed to get result: {str(e)}", "unknown_error")


def format_result(response: Dict[str, Any]) -> DetectionResult:
    """
    Format the raw API response into a user-friendly result

    Args:
        response: Raw API response

    Returns:
        Simplified detection result
    """

    # Handle regular API responses
    if "resultsSummary" in response:
        results_summary = response.get("resultsSummary", {})
        status = results_summary.get("status", "UNKNOWN")

        # Replace FAKE with ARTIFICIAL
        if status == "FAKE":
            status = "ARTIFICIAL"

        # Get the score and normalize it to a float between 0 and 1
        raw_score = results_summary.get("metadata", {}).get("finalScore")
        score = None
        if raw_score is not None:
            try:
                score = raw_score / 100.0
            except (ValueError, TypeError):
                score = None

        # Extract active models (not NOT_APPLICABLE)
        models_data = [
            m for m in response.get("models", []) if m.get("status") != "NOT_APPLICABLE"
        ]

        # Format models
        models: list[ModelResult] = []
        for model in models_data:
            predicted_number = model.get("predictionNumber")
            if isinstance(predicted_number, (int, float)):
                model_score = predicted_number
            else:
                model_score = None

            # Replace FAKE with ARTIFICIAL in model status
            model_status = model.get("status", "UNKNOWN")
            if model_status == "FAKE":
                model_status = "ARTIFICIAL"

            models.append(
                {
                    "name": model.get("name", "Unknown"),
                    "status": model_status,
                    "score": model_score,
                }
            )

        return {"status": status, "score": score, "models": models}

    # Return a default empty result if we couldn't parse the response
    return {"status": "UNKNOWN", "score": None, "models": []}


async def get_detection_result(
    client: ClientType,
    request_id: str,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    polling_interval: int = DEFAULT_POLLING_INTERVAL,
) -> DetectionResult:
    """
    Get the detection result for a specific request

    Args:
        client: HTTP client for API requests
        request_id: The request ID to get results for
        max_attempts: Maximum number of attempts to get results
        polling_interval: How long to wait between attempts

    Returns:
        Detection result with status and scores

    Raises:
        RealityDefenderError: If the request fails
    """
    if not request_id:
        raise RealityDefenderError("request_id is required", "not_found")

    attempts = 0

    while attempts < max_attempts:
        try:
            # Get the current media result
            media_result = await get_media_result(client, request_id)

            # Format the result
            result = format_result(media_result)

            # If the status is not ANALYZING, return the results immediately
            if result["status"] != "ANALYZING":
                return result

            # If we've reached the maximum attempts, return the current result even if still analyzing
            if attempts >= max_attempts - 1:
                return result

            # Increment attempts and wait before trying again
            attempts += 1
            await sleep(polling_interval)

        except RealityDefenderError as e:
            # If not found and we have attempts left, wait and try again
            if e.code == "not_found" and attempts < max_attempts - 1:
                attempts += 1
                await sleep(polling_interval)
                continue
            # Otherwise re-raise the error
            raise

        except Exception as e:
            # Convert other errors to SDK errors
            raise RealityDefenderError(
                f"Failed to get detection result: {str(e)}", "server_error"
            )

    # This should never be reached, but just in case
    media_result = await get_media_result(client, request_id)
    return format_result(media_result)
