import os
import tempfile

import pytest

from realitydefender.utils.file_utils import get_file_info
from realitydefender.errors import RealityDefenderError


def test_get_file_info_success() -> None:
    """Test successful file info extraction"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello, world!")
        temp_path = f.name

    try:
        filename, content, mime_type = get_file_info(temp_path)

        assert filename == os.path.basename(temp_path)
        assert content == b"Hello, world!"
        assert mime_type == "text/plain"
    finally:
        os.unlink(temp_path)


def test_get_file_info_binary_content() -> None:
    """Test file with binary content"""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        binary_data = b"\x89PNG\r\n\x1a\n"
        f.write(binary_data)
        temp_path = f.name

    try:
        filename, content, mime_type = get_file_info(temp_path)

        assert filename == os.path.basename(temp_path)
        assert content == binary_data
        assert mime_type == "image/jpeg"
    finally:
        os.unlink(temp_path)


def test_get_file_info_unknown_mime_type() -> None:
    """Test file with unknown extension defaults to octet-stream"""
    with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
        f.write(b"test")
        temp_path = f.name

    with pytest.raises(RealityDefenderError) as exc_info:
        try:
            _, _, mime_type = get_file_info(temp_path)
        finally:
            os.unlink(temp_path)

    assert exc_info.value.code == "invalid_file"


def test_get_file_info_file_not_found() -> None:
    """Test error when file doesn't exist"""
    with pytest.raises(RealityDefenderError) as exc_info:
        get_file_info("/nonexistent/file.txt")

    assert exc_info.value.code == "invalid_file"
    assert "File not found" in str(exc_info.value)


def test_get_file_info_file_too_large() -> None:
    """Test error when file exceeds size limit"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        # Write content larger than txt limit (5MB)
        f.write(b"x" * (5242880 + 1))
        temp_path = f.name

    try:
        with pytest.raises(RealityDefenderError) as exc_info:
            get_file_info(temp_path)

        assert exc_info.value.code == "file_too_large"
        assert "File too large" in str(exc_info.value)
    finally:
        os.unlink(temp_path)


def test_get_file_info_supported_extensions() -> None:
    """Test various supported file extensions return correct info"""
    test_cases = [
        (".mp4", "video/mp4"),
        (".jpg", "image/jpeg"),
        (".png", "image/png"),
        (".mp3", "audio/mpeg"),
        (".txt", "text/plain"),
    ]

    for ext, expected_mime in test_cases:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            filename, content, mime_type = get_file_info(temp_path)
            assert filename.endswith(ext)
            assert content == b"test"
            assert mime_type == expected_mime
        finally:
            os.unlink(temp_path)
