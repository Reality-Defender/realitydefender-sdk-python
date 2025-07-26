"""
Error types and classes for the Reality Defender SDK
"""

from typing import Literal

# Error codes returned by the SDK
ErrorCode = Literal[
    "unauthorized",  # Authorization related error
    "invalid_request",  # Request format error
    "server_error",  # Server-side error occurred
    "timeout",  # Operation timed out
    "invalid_file",  # File not found or invalid format
    "file_too_large",  # File too large to upload.
    "upload_failed",  # Failed to upload the file
    "not_found",  # Requested resource not found
    "unknown_error",  # Unexpected error
]


class RealityDefenderError(Exception):
    """
    Custom exception class for Reality Defender SDK errors
    """

    def __init__(self, message: str, code: ErrorCode):
        """
        Creates a new SDK error

        Args:
            message: Human-readable error message
            code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.message} (Code: {self.code})"
