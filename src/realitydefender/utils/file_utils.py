"""
File utilities for the SDK
"""

import mimetypes
import os
from typing import Tuple

from realitydefender.core.constants import SUPPORTED_FILE_TYPES
from realitydefender.errors import RealityDefenderError


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

        file_size = os.path.getsize(file_path)
        file_extension: str = os.path.splitext(filename)[1].lower()
        file_extension_size_limit: int = next(
            (
                x.get("size_limit", 0)
                for x in SUPPORTED_FILE_TYPES
                if file_extension in x.get("extensions", [])
            ),
            0,
        )

        if file_extension_size_limit == 0:
            raise RealityDefenderError(
                f"Unsupported file type: {file_extension}", "invalid_file"
            )
        if file_size > file_extension_size_limit:
            raise RealityDefenderError(
                f"File too large to upload: {file_path}", "file_too_large"
            )

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            # Default to binary if we can't determine the type
            content_type = "application/octet-stream"

        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        return filename, content, content_type
    except RealityDefenderError:
        raise
    except Exception as e:
        raise RealityDefenderError(f"Error reading file: {str(e)}", "invalid_file")
