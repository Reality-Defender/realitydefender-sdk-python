#!/usr/bin/env python

"""
Example script showing how to retrieve detection results using the Reality Defender SDK
This example demonstrates both synchronous and asynchronous approaches to get results
"""

import asyncio
import os
import sys
from datetime import date, timedelta
from typing import Optional

from realitydefender import RealityDefender, RealityDefenderError
from realitydefender.model import DetectionResultList


def format_score(score: Optional[float]) -> str:
    """Helper function to format scores for display"""
    if score is None:
        return "None"
    return f"{score:.4f} ({score * 100:.1f}%)"


def print_results(results: DetectionResultList) -> None:
    """Helper function to print detection results"""
    print(f"Total Results: {results['total_items']}")
    print(f"Current Page: {results['current_page'] + 1} of {results['total_pages']}")
    print(f"Results on this page: {results['current_page_items_count']}")

    if results["items"]:
        print("\nDetection Results:")
        for i, result in enumerate(results["items"], 1):
            print(f"\n{i}. Status: {result['status']}")
            print(f"   Score: {format_score(result['score'])}")

            if result["models"]:
                print("   Models:")
                for model in result["models"]:
                    print(
                        f"     - {model['name']}: {model['status']} (Score: {format_score(model['score'])})"
                    )
    else:
        print("\nNo results found.")


def sync_example() -> None:
    """Example using synchronous get_results_sync method"""
    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    client: Optional[RealityDefender] = None

    try:
        # Initialize the SDK
        client = RealityDefender(api_key=api_key)

        print("Fetching results using synchronous method...")

        # Get first page of results
        results = client.get_results_sync(page_number=0, size=5)
        print_results(results)

        # Example with date filter (last 30 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        print(f"\n\nFetching results from {start_date} to {end_date}...")
        filtered_results = client.get_results_sync(
            page_number=0, size=10, start_date=start_date, end_date=end_date
        )
        print_results(filtered_results)

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        if client:
            client.cleanup_sync()


async def async_example() -> None:
    """Example using asynchronous get_results method"""
    # Get API key from environment variable
    api_key = os.environ.get("REALITY_DEFENDER_API_KEY")

    if not api_key:
        print("ERROR: Please set REALITY_DEFENDER_API_KEY environment variable")
        return

    client: Optional[RealityDefender] = None

    try:
        # Initialize the SDK
        client = RealityDefender(api_key=api_key)

        print("Fetching results using asynchronous method...")

        # Get first page of results
        results = await client.get_results(page_number=0, size=5)
        print_results(results)

        # Example with name filter
        print("\n\nFetching results filtered by name containing 'test'...")
        name_filtered_results = await client.get_results(
            page_number=0, size=10, name="test"
        )
        print_results(name_filtered_results)

        # Example showing pagination
        if results["total_pages"] > 1:
            print("\n\nFetching page 2 of results...")
            page2_results = await client.get_results(page_number=1, size=5)
            print_results(page2_results)

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        if client:
            await client.cleanup()


def combined_example() -> None:
    """Example showing both sync and async methods"""
    print("Reality Defender SDK - Results Retrieval Example\n")

    print("=" * 60)
    print("SYNCHRONOUS EXAMPLE")
    print("=" * 60)
    sync_example()

    print("\n" + "=" * 60)
    print("ASYNCHRONOUS EXAMPLE")
    print("=" * 60)
    asyncio.run(async_example())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sync":
            print("Running synchronous example only...\n")
            sync_example()
        elif sys.argv[1] == "--async":
            print("Running asynchronous example only...\n")
            asyncio.run(async_example())
        else:
            print("Usage: python results_example.py [--sync|--async]")
            sys.exit(1)
    else:
        combined_example()

    print("\nExample complete!")
