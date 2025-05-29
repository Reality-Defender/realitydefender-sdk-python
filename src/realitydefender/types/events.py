"""
Event-related type definitions
"""

from typing import Dict, Literal, Protocol, Union, Any

from ..errors import RealityDefenderError


# Protocol for event handlers
class ResultHandler(Protocol):
    """Event handler for detection results"""

    def __call__(self, result: Any) -> None: ...  # Use Any instead of DetectionResult to avoid type errors


class ErrorHandler(Protocol):
    """Event handler for errors"""

    def __call__(self, error: RealityDefenderError) -> None: ...


# Type for event names
EventName = Literal["result", "error"]

# Map of event names to handler types
EventHandlers = Dict[EventName, Union[ResultHandler, ErrorHandler]]
