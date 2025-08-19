"""
Constants used across the Reality Defender SDK
"""

# Default API endpoint
DEFAULT_API_ENDPOINT = "https://api.prd.realitydefender.xyz"

# API paths
API_PATHS = {
    "SIGNED_URL": "/api/files/aws-presigned",
    "MEDIA_RESULT": "/api/media/users",
    "ALL_MEDIA_RESULTS": "/api/v2/media/users/pages",
    "SOCIAL_MEDIA": "/api/files/social",
}

# Default polling interval in milliseconds
DEFAULT_POLLING_INTERVAL = 2000

# Default timeout in milliseconds (1 minute)
DEFAULT_TIMEOUT = 60000

# Default maximum polling attempts
DEFAULT_MAX_ATTEMPTS = 30

# Supported file types and maximum sizes for each one of them.
SUPPORTED_FILE_TYPES: list[dict] = [
    {"extensions": [".mp4", ".mov"], "size_limit": 262144000},
    {"extensions": [".jpg", ".png", ".jpeg", ".gif", ".webp"], "size_limit": 52428800},
    {
        "extensions": [".flac", ".wav", ".mp3", ".m4a", ".aac", ".alac", ".ogg"],
        "size_limit": 20971520,
    },
    {"extensions": [".txt"], "size_limit": 5242880},
]
