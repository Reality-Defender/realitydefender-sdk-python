"""
Type definitions for the Reality Defender SDK
"""

from typing import List, Optional, TypedDict
from typing import Dict, Literal, Protocol, Union, Any

from realitydefender.errors import RealityDefenderError


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


# Protocol for event handlers
class ResultHandler(Protocol):
    """Event handler for detection results"""

    def __call__(
        self, result: Any
    ) -> None: ...  # Use Any instead of DetectionResult to avoid type errors


class ErrorHandler(Protocol):
    """Event handler for errors"""

    def __call__(self, error: RealityDefenderError) -> None: ...


# Type for event names
EventName = Literal["result", "error"]

# Map of event names to handler types
EventHandlers = Dict[EventName, Union[ResultHandler, ErrorHandler]]
