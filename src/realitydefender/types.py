"""
Type definitions for the Reality Defender SDK
"""

from typing import List, Optional, TypedDict


class RealityDefenderConfig(TypedDict, total=False):
    """Configuration options for the Reality Defender SDK"""

    api_key: str
    """API key for authentication"""

    base_url: Optional[str]
    """Optional custom base URL for the API (defaults to production)"""


class UploadOptions(TypedDict):
    """Options for uploading media"""

    file_path: str
    """Path to the file to be analyzed"""


class GetResultOptions(TypedDict, total=False):
    """Options for retrieving results"""

    max_attempts: Optional[int]
    """Maximum number of polling attempts before returning even if still analyzing"""

    polling_interval: Optional[int]
    """Interval in milliseconds between polling attempts"""


class DetectionOptions(TypedDict):
    """Internal options for detection operations"""

    max_attempts: int
    """Maximum number of polling attempts before returning even if still analyzing"""

    polling_interval: int
    """Interval in milliseconds between polling attempts"""


class UploadResult(TypedDict):
    """Result of a successful upload"""

    request_id: str
    """Request ID used to retrieve results"""

    media_id: str
    """Media ID assigned by the system"""


class ModelResult(TypedDict):
    """Results from an individual detection model"""

    name: str
    """Model name"""

    status: str
    """Model status determination"""

    score: Optional[float]
    """Model confidence score (0-100, null if not available)"""


class DetectionResult(TypedDict):
    """Simplified detection result returned to the user"""

    status: str
    """Overall status determination (e.g., "ARTIFICIAL", "AUTHENTIC")"""

    score: Optional[float]
    """Confidence score (0-100, null if processing)"""

    models: List[ModelResult]
    """Results from individual detection models"""
