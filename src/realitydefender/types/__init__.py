"""
Type definitions for the Reality Defender SDK
"""

import importlib.util
import os.path

# Get the absolute path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import parent module's types.py directly
spec = importlib.util.spec_from_file_location(
    "parent_types", os.path.join(parent_dir, "types.py")
)
if spec is not None:
    parent_types = importlib.util.module_from_spec(spec)
    if spec.loader is not None:
        spec.loader.exec_module(parent_types)

        # Re-export parent module's types
        RealityDefenderConfig = parent_types.RealityDefenderConfig
        UploadOptions = parent_types.UploadOptions
        UploadResult = parent_types.UploadResult
        DetectionResult = parent_types.DetectionResult
        GetResultOptions = parent_types.GetResultOptions
        DetectionOptions = parent_types.DetectionOptions
        ModelResult = parent_types.ModelResult

# Re-export from the events module
from .events import ErrorHandler, EventHandlers, EventName, ResultHandler

__all__ = [
    "RealityDefenderConfig",
    "UploadOptions",
    "UploadResult",
    "DetectionResult",
    "GetResultOptions",
    "DetectionOptions",
    "ModelResult",
    "EventName",
    "ResultHandler",
    "ErrorHandler",
    "EventHandlers",
]

# Note: Other types are defined in the parent module's types.py file
# and should be imported directly from there to avoid circular imports:
# from realitydefender.types import RealityDefenderConfig, UploadOptions, etc.
