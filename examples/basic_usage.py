"""
Basic usage example for the Reality Defender SDK
"""

import asyncio
import os
import sys
from typing import Optional

# Add the parent directory to the Python path so we can import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from realitydefender import RealityDefender, RealityDefenderError


def format_score(score: Optional[float]) -> str:
    """Helper function to format scores for display"""
    if score is None:
        return "None"
    return f"{score:.4f} ({score*100:.1f}%)"


async def basic_example() -> None:
    """
    Basic example of uploading a file and getting results
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

        # Poll for results
        print("\nPolling for results...")
        result = await client.get_result(upload_result["request_id"])

        print("\nDetection Results:")
        print(f"Status: {result['status']}")

        # Format score as a percentage if it exists
        if result["score"] is not None:
            print(f"Score: {result['score']:.4f} ({result['score']*100:.1f}%)")
        else:
            print(f"Score: None")

        print("\nModel Results:")
        for model in result["models"]:
            score_display = "None"
            if model["score"] is not None:
                score_display = f"{model['score']:.4f} ({model['score']*100:.1f}%)"
            print(f"  - {model['name']}: {model['status']} (Score: {score_display})")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client to avoid unclosed session warnings
        if client:
            await client.cleanup()


async def event_based_example() -> None:
    """
    Example using event-based approach
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

        # Set up event handlers
        client.on(
            "result",
            lambda result: print(
                f"\nResult: {result['status']} (Score: {format_score(result['score'])})"
            ),
        )
        client.on(
            "error",
            lambda error: print(f"\nError: {error.message} (Code: {error.code})"),
        )

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

        print(f"Upload successful! Request ID: {upload_result['request_id']}")

        # Start polling using the event-based approach
        print("\nStarting event-based polling...")
        polling_task = client.poll_for_results(
            upload_result["request_id"],
            polling_interval=2000,  # 2 seconds between polls
            timeout=60000,  # 60 second timeout
        )

        # Wait for polling to complete
        await polling_task
        print("\nPolling complete!")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client to avoid unclosed session warnings
        if client:
            await client.cleanup()


if __name__ == "__main__":
    print("Reality Defender SDK Basic Example\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--events":
        print("Running event-based example...\n")
        asyncio.run(event_based_example())
    else:
        print("Running basic example...\n")
        asyncio.run(basic_example())

    print("\nExample complete!")
