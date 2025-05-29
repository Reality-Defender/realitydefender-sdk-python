"""
File utilities for the SDK
"""

import mimetypes
import os
from typing import Tuple

from ..errors import RealityDefenderError


def get_file_info(file_path: str) -> Tuple[str, bytes, str]:
    """
    Get file information needed for upload

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (filename, file_content, mime_type)

    Raises:
        RealityDefenderError: If file not found or cannot be read
    """
    if not os.path.isfile(file_path):
        raise RealityDefenderError(f"File not found: {file_path}", "invalid_file")

    try:
        filename = os.path.basename(file_path)

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            # Default to binary if we can't determine the type
            content_type = "application/octet-stream"

        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        return filename, content, content_type
    except Exception as e:
        raise RealityDefenderError(f"Error reading file: {str(e)}", "invalid_file")
