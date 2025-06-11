# Reality Defender SDK Examples

This directory contains example scripts demonstrating how to use the Reality Defender SDK.

## Prerequisites

Before running these examples, make sure to:

1. Set your API key as an environment variable:
   ```bash
   export REALITY_DEFENDER_API_KEY="your-api-key"
   ```

2. Install the SDK in development mode:
   ```bash
   uv venv && source .venv/bin/activate && uv pip install -e .
   ```

## Example Files

### `basic_usage.py`
Demonstrates basic asynchronous usage of the SDK, including:
- File upload
- Retrieving detection results
- Event-based approach for result notifications

**Required files:** `test_image.jpg` (place in the `images/` directory)

**Command-line options:**
```bash
python basic_usage.py             # Process file in an asynchronous manner.
python basic_usage.py --events    # Process file in an asynchronous manner using the event based client.
```

### `sync_usage.py`
Demonstrates synchronous usage of the SDK without dealing with asyncio:
- Synchronous upload and detection
- One-step file detection
- Synchronous callbacks for polling

**Required files:** `test_image.jpg` (place in the `images/` directory)

**Command-line options:**
```bash
python sync_usage.py               # Process file in a synchronous manner.
python sync_usage.py --one-step    # Process file in a synchronous manner, running one-step detection example.
python sync_usage.py --callbacks   # Process file in an synchronous manner, running synchronous callbacks example.
```

### `batch_processing.py`
Demonstrates how to process multiple files concurrently:
- Concurrent processing with configurable concurrency limits
- Handles both image and video files
- Detailed analytics including processing times and file sizes
- Performance measurement for batch operations
- Result aggregation and reporting

**Required files:** 
- Place image files in the `images/` directory
- Place video files in the `videos/` directory

**Command-line options:**
```bash
python batch_processing.py --images-only    # Process only image files
python batch_processing.py --videos-only    # Process only video files
python batch_processing.py --concurrent 5    # Set maximum concurrent files to process
```

### `video_detection.py`
Demonstrates how to analyze video files:
- Video file upload and analysis
- Handling longer processing times
- Event-based result notifications

**Required files:** `test_video.mp4` (place in the `images/` directory)
