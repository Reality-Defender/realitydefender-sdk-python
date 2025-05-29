"""
Synchronous usage example for the Reality Defender SDK
This example shows how to use the SDK without dealing with asyncio.
"""

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


def basic_sync_example() -> None:
    """
    Basic example using synchronous methods
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

        # Upload a file for analysis using the synchronous method
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
        upload_result = client.upload_sync({"file_path": file_path})

        print(f"Upload successful!")
        print(f"Request ID: {upload_result['request_id']}")
        print(f"Media ID: {upload_result['media_id']}")

        # Get results using the synchronous method
        print("\nGetting results...")
        result = client.get_result_sync(upload_result["request_id"])

        print("\nDetection Results:")
        print(f"Status: {result['status']}")
        print(f"Score: {format_score(result['score'])}")

        print("\nModel Results:")
        for model in result["models"]:
            print(
                f"  - {model['name']}: {model['status']} (Score: {format_score(model['score'])})"
            )

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client session
        if client:
            client.cleanup_sync()


def one_step_detection_example() -> None:
    """
    Example using the simplified one-step detect_file method
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

        # Define the path to the file
        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "images", "test_image.jpg")
        )

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            print(
                "Please add a test image named 'test_image.jpg' to the examples/images directory"
            )
            return

        print(f"Analyzing file in one step: {file_path}")
        start_time = time.time()

        # Analyze the file in one step (uploads and gets results automatically)
        result = client.detect_file(file_path)

        total_time = time.time() - start_time
        print(f"Analysis completed in {total_time:.2f} seconds!")

        print("\nDetection Results:")
        print(f"Status: {result['status']}")
        print(f"Score: {format_score(result['score'])}")

        print("\nModel Results:")
        for model in result["models"]:
            print(
                f"  - {model['name']}: {model['status']} (Score: {format_score(model['score'])})"
            )

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client session
        if client:
            client.cleanup_sync()


def sync_callback_example() -> None:
    """
    Example using synchronous callbacks for polling
    """
    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    # Define callback functions
    def on_result(result: DetectionResult) -> None:
        print("\nResult received:")
        print(f"Status: {result['status']}")
        print(f"Score: {format_score(result['score'])}")

        print("\nModel Results:")
        for model in result["models"]:
            print(
                f"  - {model['name']}: {model['status']} (Score: {format_score(model['score'])})"
            )

    def on_error(error: RealityDefenderError) -> None:
        print(f"\nError occurred: {error.message} (Code: {error.code})")

    client: Optional[RealityDefender] = None

    try:
        # Initialize the SDK
        client = RealityDefender({"api_key": api_key})

        # Upload a file for analysis using the synchronous method
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
        upload_result = client.upload_sync({"file_path": file_path})

        print(f"Upload successful! Request ID: {upload_result['request_id']}")

        # Start polling with callbacks using the synchronous method
        print("\nStarting polling with callbacks...")
        client.poll_for_results_sync(
            upload_result["request_id"],
            polling_interval=2000,  # 2 seconds
            timeout=60000,  # 60 seconds
            on_result=on_result,
            on_error=on_error,
        )

        print("\nPolling complete!")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client session
        if client:
            client.cleanup_sync()


if __name__ == "__main__":
    print("Reality Defender SDK - Synchronous Usage Examples\n")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--one-step":
            print("Running one-step detection example...\n")
            one_step_detection_example()
        elif sys.argv[1] == "--callbacks":
            print("Running synchronous callbacks example...\n")
            sync_callback_example()
    else:
        print("Running basic synchronous example...\n")
        basic_sync_example()

    print("\nExample complete!")
