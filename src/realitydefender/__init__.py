"""
Reality Defender SDK
Client library for deepfake detection using the Reality Defender API
"""

from .detection.results import get_detection_result
from .detection.upload import upload_file
from .errors import ErrorCode, RealityDefenderError
from realitydefender.model import (
    DetectionResult,
    UploadResult,
)
from .reality_defender import RealityDefender

__all__ = [
    "RealityDefender",
    "upload_file",
    "get_detection_result",
    "RealityDefenderError",
    "ErrorCode",
    "UploadResult",
    "DetectionResult",
]
