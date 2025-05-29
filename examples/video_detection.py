"""
Video detection example for the Reality Defender SDK
This example shows how to use the SDK for analyzing videos for deepfakes.
"""

import asyncio
import os
import sys
import time
from typing import Optional

# Add the parent directory to the Python path so we can import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from realitydefender import RealityDefender, RealityDefenderError
from realitydefender.types import DetectionResult


def format_score(score: Optional[float]) -> str:
    """Helper function to format scores for display"""
    if score is None:
        return "None"
    return f"{score:.4f} ({score*100:.1f}%)"


async def detect_video_deepfake() -> None:
    """
    Example of analyzing a video file for deepfakes
    """
    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    client: Optional[RealityDefender] = None

    try:
        # Initialize the SDK
        client = RealityDefender({"api_key": api_key})

        # Define the video file path - you'll need to provide your own video file
        video_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "videos", "test_video.mp4")
        )

        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            print(
                "Please add a test video named 'test_video.mp4' to the examples/videos directory"
            )
            return

        print(f"Video file size: {os.path.getsize(video_path) / (1024 * 1024):.2f} MB")

        # Upload video for analysis
        print(f"Uploading video: {video_path}")
        start_time = time.time()
        upload_result = await client.upload({"file_path": video_path})
        upload_duration = time.time() - start_time

        print(f"Upload successful in {upload_duration:.2f} seconds!")
        print(f"Request ID: {upload_result['request_id']}")
        print(f"Media ID: {upload_result['media_id']}")

        # Videos may take longer to analyze, so we'll use the event-based approach
        print("\nStarting event-based polling for video analysis...")

        # Track when we got the result
        result_received = False
        start_time = time.time()

        # Define event handlers
        def on_result(result: DetectionResult) -> None:
            nonlocal result_received
            result_received = True
            duration = time.time() - start_time

            print(f"\nResult received after {duration:.2f} seconds:")
            print(f"Status: {result['status']}")
            print(f"Score: {format_score(result['score'])}")

            print("\nModel Results:")
            for model in result["models"]:
                print(
                    f"  - {model['name']}: {model['status']} (Score: {format_score(model['score'])})"
                )

        def on_error(error: RealityDefenderError) -> None:
            print(f"\nError occurred: {error.message} (Code: {error.code})")

        # Register event handlers
        client.on("result", on_result)
        client.on("error", on_error)

        # Start polling with a longer timeout for videos (5 minutes)
        polling_task = client.poll_for_results(
            upload_result["request_id"],
            polling_interval=5000,  # 5 seconds between polls
            timeout=300000,  # 5 minute timeout
        )

        # Wait for the polling to complete
        await polling_task

        if not result_received:
            print("\nPolling completed but no result was received.")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client to avoid unclosed session warnings
        if client:
            await client.cleanup()


if __name__ == "__main__":
    print("Reality Defender SDK - Video Detection Example\n")
    asyncio.run(detect_video_deepfake())
    print("\nExample complete!")
