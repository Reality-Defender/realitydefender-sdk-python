"""
Test script to verify the wait-until-complete behavior for results.
"""

import asyncio
import os
import sys
import time
from typing import Optional

# Add the parent directory to the Python path so we can import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from realitydefender import RealityDefender, RealityDefenderError


async def test_wait_for_result() -> None:
    """Test waiting for complete results"""
    print("Testing wait-until-complete behavior...")

    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    client: Optional[RealityDefender] = None

    try:
        # Initialize the SDK
        client = RealityDefender({"api_key": api_key})

        # Upload a file for analysis
        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "images", "test_image.jpg")
        )

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            print(
                "Please add a test image named 'test_image.jpg' to the examples/images directory"
            )
            return

        print(f"Uploading file: {file_path}")
        upload_result = await client.upload({"file_path": file_path})

        print(f"Upload successful!")
        print(f"Request ID: {upload_result['request_id']}")
        print(f"Media ID: {upload_result['media_id']}")

        # Poll for results with increased polling time (wait until fully complete)
        print("\nPolling for results (will wait until complete)...")
        start_time = time.time()

        # Set a relatively short polling interval but a large max attempts
        # to ensure we wait until the result is complete
        result = await client.get_result(
            upload_result["request_id"],
            {
                "polling_interval": 3000,  # 3 seconds between polls
                "max_attempts": 100,  # Up to 5 minutes total wait time
            },
        )

        elapsed_time = time.time() - start_time
        print(f"Result obtained after {elapsed_time:.2f} seconds")

        print("\nDetection Results:")
        print(f"Status: {result['status']}")

        # Format score as a percentage if it exists
        if result["score"] is not None:
            print(f"Score: {result['score']:.4f} ({result['score']*100:.1f}%)")
        else:
            print(f"Score: None")

        # Print model results, filtering out NOT_APPLICABLE ones
        print("\nModel Results (only applicable models):")
        applicable_models = [
            m for m in result["models"] if m["status"] != "NOT_APPLICABLE"
        ]

        for model in applicable_models:
            score_display = "None"
            if model["score"] is not None:
                score_display = f"{model['score']:.4f} ({model['score']*100:.1f}%)"
            print(f"  - {model['name']}: {model['status']} (Score: {score_display})")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client
        if client:
            await client.cleanup()


if __name__ == "__main__":
    print("Reality Defender SDK - Wait Until Complete Test\n")
    asyncio.run(test_wait_for_result())
    print("\nTest complete!")
