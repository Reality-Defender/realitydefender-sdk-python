#!/usr/bin/env python

"""
Social media detection example for the Reality Defender SDK
This example shows how to analyze social media links for AI-generated content.
"""

import os
from typing import Optional

from realitydefender import RealityDefender, RealityDefenderError


def format_score(score: Optional[float]) -> str:
    """Helper function to format scores for display"""
    if score is None:
        return "None"
    return f"{score:.4f} ({score * 100:.1f}%)"


def sync_social_media_example() -> None:
    """
    Synchronous example of analyzing social media links
    """
    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    try:
        # Initialize the SDK
        client = RealityDefender(api_key=api_key)

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
        return
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return

    # Example social media URLs to analyze
    social_media_links = [
        "https://www.youtube.com/watch?v=6O0fySNw-Lw",
        "https://youtube.com/watch?v=ABC123",
    ]

    print("Analyzing multiple social media links synchronously...\n")

    for i, link in enumerate(social_media_links, 1):
        print(f"[{i}/{len(social_media_links)}] Analyzing: {link}")

        try:
            # Upload the social media link using the synchronous method
            upload_result = client.upload_social_media_sync(social_media_link=link)

            print(f"  ✓ Upload successful! Request ID: {upload_result['request_id']}")

            # Get results using the synchronous method
            result = client.get_result_sync(upload_result["request_id"])

            print(f"  ✓ Analysis complete - Status: {result['status']}")
            print(f"  ✓ Overall Score: {format_score(result['score'])}")

            # Show top model result
            if result["models"]:
                top_model = result["models"][0]
                print(
                    f"  ✓ Top Model ({top_model['name']}): {format_score(top_model['score'])}"
                )

        except RealityDefenderError as e:
            print(f"  ✗ Error: {e.message} (Code: {e.code})")
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)}")

        print()  # Add spacing between results


if __name__ == "__main__":
    print("Reality Defender SDK - Social Media Detection Example\n")
    sync_social_media_example()
    print("\nExample complete!")
