"""
Detection results retrieval and processing
"""

from datetime import date
from typing import Any, Dict, TypeVar, Optional

from realitydefender.client.http_client import HttpClient
from realitydefender.core.constants import (
    API_PATHS,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_POLLING_INTERVAL,
)
from realitydefender.errors import RealityDefenderError
from realitydefender.model import DetectionResult, ModelResult, DetectionResultList
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


async def get_media_results(
    client: ClientType,
    page_number: int = 0,
    size: int = 10,
    name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Fetches media results from the specified client with optional filters such as page number, size, name,
    start date, and end date. This is an asynchronous function and communicates with an external API
    to retrieve media result data. It accurately handles specific and general exceptions, ensuring proper error
    reporting in case the request fails.

    Parameters:
        client: ClientType
            The client instance used for making HTTP requests to the API.
        page_number: int, optional
            The page number of the results to fetch.
        size: int, optional
            The number of results to fetch per page.
        name: str or None, optional
            Filter results by name.
        start_date: date or None, optional
            Filter results that were created or updated starting from this date.
        end_date: date or None, optional
            Filter results that were created or updated up until this date.

    Returns:
        list[dict[str, any]]
            A list of dictionaries containing the media results retrieved from the API.

    Raises:
        RealityDefenderError
            Raised if the request fails or if an unknown error occurs during the process.
    """
    try:
        path = f"{API_PATHS['ALL_MEDIA_RESULTS']}/{page_number}"
        params = {"size": str(size)}
        if name:
            params["name"] = str(name)
        if start_date:
            params["startDate"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["endDate"] = end_date.strftime("%Y-%m-%d")

        return await client.get(path=path, params=params)
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(f"Failed to get results: {str(e)}", "unknown_error")


def format_result(response: Dict[str, Any]) -> DetectionResult:
    """
    Format the raw API response into a user-friendly result

    Args:
        response: Raw API response

    Returns:
        Simplified detection result
    """

    # Handle regular API responses
    request_id: str = response.get("requestId", "UNKNOWN")

    if response.get("resultsSummary") is not None:
        results_summary = response.get("resultsSummary", {})
        status = results_summary.get("status", "UNKNOWN")

        # Replace FAKE with MANIPULATED
        if status == "FAKE":
            status = "MANIPULATED"

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

            # Replace FAKE with MANIPULATED in model status
            model_status = model.get("status", "UNKNOWN")
            if model_status == "FAKE":
                model_status = "MANIPULATED"

            models.append(
                {
                    "name": model.get("name", "Unknown"),
                    "status": model_status,
                    "score": model_score,
                }
            )

        return {
            "request_id": request_id,
            "status": status,
            "score": score,
            "models": models,
        }

    # Return a default empty result if we couldn't parse the response
    return {"request_id": request_id, "status": "UNKNOWN", "score": None, "models": []}


def format_result_list(response: Dict[str, Any]) -> DetectionResultList:
    """
    Format the list all media API response into a user-friendly result

    Args:
        response: Raw API response

    Returns:
        DetectionResultList: Simplified detection result list
    Raises:
    Exception
        Reraises any exceptions encountered during formatting.
    """
    # Handle regular API responses
    if response is None or any(
        [
            response.get(x) is None
            for x in [
                "totalItems",
                "totalPages",
                "currentPage",
                "currentPageItemsCount",
                "mediaList",
            ]
        ]
    ):
        raise RealityDefenderError("Invalid response from server", "server_error")

    result = DetectionResultList(
        total_items=response.get("totalItems", 0),
        total_pages=response.get("totalPages", 0),
        current_page=response.get("currentPage", 0),
        current_page_items_count=response.get("currentPageItemsCount", 0),
        items=[],
    )

    for item in response.get("mediaList", []):
        result.setdefault("items", []).append(format_result(item))

    return result


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
            if result["status"] not in ["ANALYZING", "UNKNOWN"]:
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


async def get_detection_results(
    client: ClientType,
    page_number: int = 0,
    size: int = 10,
    name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    polling_interval: int = DEFAULT_POLLING_INTERVAL,
) -> DetectionResultList:
    """
    Retrieves detection results asynchronously based on specified criteria. This function
    communicates with the client to fetch paginated detection results. Optionally, filters
    like name, start_date, and end_date can be applied. It also retries fetching in case
    of failures up to the specified maximum attempts, with a defined polling interval
    between retries.

    Parameters:
    client: ClientType
        The client instance used for communication.
    page_number: int
        The page index to retrieve. Defaults to 0.
    size: int
        The number of results per page. Defaults to 10.
    name: str | None
        An optional filter to retrieve results by a specific name. Defaults to None.
    start_date: Optional[datetime.date]
        An optional filter to specify the earliest date for detection results. Defaults to None.
    end_date: Optional[datetime.date]
        An optional filter to specify the latest date for detection results. Defaults to None.
    max_attempts: int
        The maximum number of attempts to fetch the results in case of intermittent issues.
         Defaults to the value of DEFAULT_MAX_ATTEMPTS.
    polling_interval: int
        The interval in seconds between retries when fetching results.
        Defaults to the value of DEFAULT_POLLING_INTERVAL.

    Returns:
    DetectionResultList
        A list containing detection results that match the specified criteria.

    Raises:
    Exception
        Reraises any exceptions encountered during the fetching or retry operations.
    """
    attempts = 0

    while attempts < max_attempts:
        try:
            # Get the current media result
            media_results = await get_media_results(
                client, page_number, size, name, start_date, end_date
            )

            # Format and return the result
            return format_result_list(media_results)

        except RealityDefenderError as e:
            # Don't retry authentication errors - they won't resolve with retries
            if e.code == "unauthorized":
                raise
            if attempts < max_attempts - 1:
                attempts += 1
                await sleep(polling_interval)
                continue
            raise

        except Exception as e:
            # Convert other errors to SDK errors
            raise RealityDefenderError(
                f"Failed to get detection result list: {str(e)}", "server_error"
            )

    raise RealityDefenderError(
        f"Failed to get detection result list after {attempts} attempts", "timeout"
    )
