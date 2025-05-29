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

### Basic Usage

```python
from realitydefender import RealityDefender

# Initialize the SDK with your API key
reality_defender = RealityDefender(
    api_key="your-api-key",
    # Optional: custom base URL if needed
    # base_url="https://api.dev.realitydefender.xyz"
)

# Upload a file for analysis
response = reality_defender.upload(file_path="/path/to/your/file.jpg")
request_id = response["request_id"]

# Callback-based approach to get results
def on_result(result):
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}")
    
    # List model results
    for model in result["models"]:
        print(f"{model['name']}: {model['status']} ({model['score']})")

def on_error(error):
    print(f"Error: {error['message']} ({error['code']})")

reality_defender.get_result_async(request_id, on_result, on_error)

# Alternative: Poll for results synchronously
# result = reality_defender.get_result(request_id)
```

### Synchronous Approach

As an alternative to the callback-based approach, you can use synchronous polling:

```python
from realitydefender import RealityDefender

# Initialize the SDK with your API key
reality_defender = RealityDefender(
    api_key="your-api-key"
)

def detect_media():
    try:
        # Upload a file for analysis
        response = reality_defender.upload(file_path="/path/to/your/file.jpg")
        request_id = response["request_id"]
        
        # Get results using the requestId (polls until completion)
        result = reality_defender.get_result(request_id)
        
        # Process the results
        print(f"Status: {result['status']}")
        print(f"Score: {result['score']}")
        
        # List model results
        for model in result["models"]:
            print(f"{model['name']}: {model['status']} ({model['score']})")
        
        return result
    except Exception as error:
        print(f"Error: {str(error)}")
        raise

# Call the function
try:
    result = detect_media()
    print("Detection completed successfully")
except Exception:
    print("Detection failed")
```

## Architecture

The SDK is designed with a modular architecture for better maintainability and testability:

- **Client**: HTTP communication with the Reality Defender API
- **Core**: Configuration, constants, and callbacks
- **Detection**: Media upload and results processing
- **Models**: Data classes for API responses and SDK interfaces
- **Utils**: File operations and helper functions

## API Reference

### Initialize the SDK

```python
reality_defender = RealityDefender(
    api_key=str,               # Required: Your API key
    base_url=str,              # Optional: Custom API base URL
    timeout=int                # Optional: Default request timeout in seconds
)
```

### Upload Media for Analysis

```python
response = reality_defender.upload(
    file_path=str,             # Required: Path to the file to analyze
    polling_interval=int,      # Optional: Interval in seconds to poll for results (default: 5)
    timeout=int                # Optional: Timeout in seconds for polling (default: 300)
)
```

Returns: `{"request_id": str, "media_id": str}`

### Get Results for a Request

```python
result = reality_defender.get_result(request_id)
```

Returns a dictionary:

```python
{
    "status": str,       # Overall status (e.g., "ARTIFICIAL", "AUTHENTIC", etc.)
    "score": float,      # Overall confidence score (0-100)
    "models": [          # Array of model-specific results
        {
            "name": str,     # Model name
            "status": str,   # Model-specific status
            "score": float   # Model-specific score
        }
    ]
}
```

### Asynchronous Results

```python
reality_defender.get_result_async(
    request_id=str,              # Required: Request ID from upload
    on_result=callable,          # Required: Callback for results
    on_error=callable,           # Required: Callback for errors
    polling_interval=int,        # Optional: Polling interval in seconds
    timeout=int                  # Optional: Timeout in seconds
)
```

## Error Handling

The SDK raises exceptions for various error scenarios:

```python
try:
    result = reality_defender.upload(file_path="/path/to/file.jpg")
except RealityDefenderError as error:
    print(f"Error: {error.message} ({error.code})")
    # Error codes: 'unauthorized', 'server_error', 'timeout', 
    # 'invalid_file', 'upload_failed', 'not_found', 'unknown_error'
```

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