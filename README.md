# Reality Defender SDK for Python

[![codecov](https://codecov.io/gh/Reality-Defender/realitydefender-sdk-python/graph/badge.svg?token=S64OCTEW6B)](https://codecov.io/gh/Reality-Defender/realitydefender-sdk-python)

A Python SDK for the Reality Defender API to detect deepfakes and manipulated media.

## Installation

```bash
# Using pip
pip install realitydefender

# Using poetry
poetry add realitydefender
```

## Getting Started

First, you need to obtain an API key from the [Reality Defender Platform](https://app.realitydefender.ai).

### Asynchronous Approach

This approach uses direct polling to wait for the analysis results.

```python
import asyncio
from realitydefender import RealityDefender


async def main():
    # Initialize the SDK with your API key
    print("Initializing Reality Defender SDK...")
    rd = RealityDefender(api_key="your-api-key")

    # Upload a file for analysis
    print("Uploading file for analysis...")
    response = await rd.upload(file_path="/path/to/your/file.jpg")
    request_id = response["request_id"]
    print(f"File uploaded successfully. Request ID: {request_id}")

    # Get results by polling until completion
    print("Waiting for analysis results...")
    result = await rd.get_result(request_id)
    print("Analysis complete!")

    # Process the results
    print("\nResults:")
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}")

    # List model results
    print("\nModel details:")
    for model in result["models"]:
        print(f"{model['name']}: {model['status']} (Score: {model['score']})")


# Run the async function
asyncio.run(main())
```

### Event-Based Approach

This approach uses event handlers to process results when they become available.

```python
import asyncio
from realitydefender import RealityDefender


async def main():
    # Initialize the SDK
    print("Initializing Reality Defender SDK...")
    rd = RealityDefender(api_key="your-api-key")

    # Set up event handlers
    print("Setting up event handlers...")
    rd.on("result", lambda result: print(f"Result received: {result['status']} (Score: {result['score']})"))
    rd.on("error", lambda error: print(f"Error occurred: {error.message}"))

    # Upload and start polling
    print("Uploading file for analysis...")
    response = await rd.upload(file_path="/path/to/your/file.jpg")
    request_id = response["request_id"]
    print(f"File uploaded successfully. Request ID: {request_id}")

    print("Starting to poll for results...")
    await rd.poll_for_results(response["request_id"])
    print("Polling complete!")


# Run the async function
asyncio.run(main())
```

## Architecture

The SDK is designed with a modular architecture for better maintainability and testability:

- **Client**: HTTP communication with the Reality Defender API
- **Core**: Configuration, constants, and callbacks
- **Detection**: Media upload and results processing
- **Models**: Data classes for API responses and SDK interfaces
- **Utils**: File operations and helper functions

## API Reference

The Reality Defender SDK uses asynchronous operations throughout.

### Initialize the SDK

```python
rd = RealityDefender(
    api_key="your-api-key",  # Required: Your API key
)
```

### Upload Media for Analysis

```python
# Must be called from within an async function
response = await rd.upload(file_path="/path/to/file.jpg")  # Required: Path to the file to analyze
)
```

Returns: `{"request_id": str, "media_id": str}`

### Get Results via Polling

```python
# Must be called from within an async function
# This will poll until the analysis is complete
result = await rd.get_result(request_id)
```

Returns a dictionary with detection results:

```python
{
    "status": str,  # Overall status (e.g., "MANIPULATED", "AUTHENTIC")
    "score": float,  # Overall confidence score (0-1)
    "models": [  # Array of model-specific results
        {
            "name": str,  # Model name
            "status": str,  # Model-specific status
            "score": float  # Model-specific score (0-1)
        }
    ]
}
```

### Event-Based Results

```python
# Set up event handlers before polling
rd.on("result", callback_function)  # Called when results are available
rd.on("error", error_callback_function)  # Called if an error occurs

# Start polling (must be called from within an async function)
await rd.poll_for_results(request_id)

# Clean up when done (must be called from within an async function)
await rd.cleanup()
```

## Error Handling

The SDK raises exceptions for various error scenarios:

```python
try:
    result = rd.upload(file_path="/path/to/file.jpg")
except RealityDefenderError as error:
    print(f"Error: {error.message} ({error.code})")
    # Error codes: 'unauthorized', 'server_error', 'timeout', 
    # 'invalid_file', 'upload_failed', 'not_found', 'unknown_error'
```

## Supported file types and size limits

There is a size limit for each of the supported file types.

| File Type | Extensions                                 | Size Limit (bytes) | Size Limit (MB) |
|-----------|--------------------------------------------|--------------------|-----------------|
| Video     | .mp4, .mov                                 | 262,144,000        | 250 MB          |
| Image     | .jpg, .png, .jpeg, .gif, .webp             | 52,428,800         | 50 MB           |
| Audio     | .flac, .wav, .mp3, .m4a, .aac, .alac, .ogg | 20,971,520         | 20 MB           |
| Text      | .txt                                       | 5,242,880          | 5 MB            |

## Supported social media platforms

The Reality Defender API supports analysis of media from the following social media platforms:
* Facebook
* Instagram
* Twitter
* YouTube
* TikTok

## Examples

See the `examples` directory for more detailed usage examples.

## Running Examples

To run the example code in this SDK, follow these steps:

```bash
# Navigate to the python directory
cd python

# Install the package in development mode
pip install -e .

# Set your API key
export REALITY_DEFENDER_API_KEY='<your-api-key>'

# Run the example
python examples/basic_usage.py
```

The example code demonstrates how to upload a sample image and process the detection results. 