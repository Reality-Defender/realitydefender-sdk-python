"""
Detection functionality for the Reality Defender SDK
"""

from .results import get_detection_result
from .upload import upload_file

__all__ = ["upload_file", "get_detection_result"]
