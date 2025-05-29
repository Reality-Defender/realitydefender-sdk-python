"""
Batch processing example for the Reality Defender SDK
This example shows how to process multiple files concurrently.
"""

import argparse
import asyncio
import glob
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Add the parent directory to the Python path so we can import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from realitydefender import RealityDefender, RealityDefenderError
from realitydefender.types import GetResultOptions


def format_score(score: Optional[float]) -> str:
    """Helper function to format scores for display"""
    if score is None:
        return "None"
    return f"{score:.4f} ({score*100:.1f}%)"


def format_file_size(size_bytes: float) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0 or unit == "GB":
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} GB"  # Fallback


async def process_file(
    client: RealityDefender, file_path: str, polling_opts: Optional[GetResultOptions] = None
) -> Dict[str, Any]:
    """
    Process a single file and return results

    Args:
        client: RealityDefender client
        file_path: Path to file for analysis
        polling_opts: Options for result polling

    Returns:
        Dictionary with file path, request ID, and detection results
    """
    file_size = os.path.getsize(file_path)
    file_type = (
        "video"
        if file_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
        else "image"
    )

    try:
        print(
            f"Uploading: {os.path.basename(file_path)} ({format_file_size(file_size)}, {file_type})"
        )
        start_time = time.time()

        # Upload file for analysis
        upload_result = await client.upload({"file_path": file_path})

        upload_time = time.time() - start_time
        request_id = upload_result["request_id"]
        print(f"  Request ID: {request_id} (uploaded in {upload_time:.2f}s)")

        # Get results with polling
        # Videos need longer polling times
        if polling_opts is None:
            polling_opts = {}

        # For videos, use longer polling times if not specified
        if file_type == "video" and "max_attempts" not in polling_opts:
            polling_opts["max_attempts"] = 60  # More attempts for videos

        result_start_time = time.time()
        result = await client.get_result(request_id, polling_opts)
        result_time = time.time() - result_start_time

        print(
            f"  Result: {result['status']} (Score: {format_score(result['score'])}, analyzed in {result_time:.2f}s)"
        )

        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": file_type,
            "file_size": file_size,
            "upload_time": upload_time,
            "analysis_time": result_time,
            "request_id": request_id,
            "result": result,
        }
    except Exception as e:
        print(f"  Error processing {os.path.basename(file_path)}: {str(e)}")
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": file_type,
            "file_size": file_size,
            "error": str(e),
        }


async def batch_process_directories(
    process_images: bool = True,
    process_videos: bool = True,
    max_concurrent: int = 3
) -> None:
    """
    Process media files in directories concurrently

    Args:
        process_images: Whether to process image files
        process_videos: Whether to process video files
        max_concurrent: Maximum number of concurrent files to process
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

        media_files: List[str] = []

        # Process images if requested
        if process_images:
            # Directory containing images to process
            images_dir = os.path.join(os.path.dirname(__file__), "images")

            if not os.path.exists(images_dir):
                print(f"Images directory not found: {images_dir}")
            else:
                # Find all image files
                image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]
                image_files: List[str] = []

                for ext in image_extensions:
                    image_files.extend(glob.glob(os.path.join(images_dir, ext)))
                    image_files.extend(glob.glob(os.path.join(images_dir, ext.upper())))

                # Skip .gitkeep and other hidden files
                image_files = [
                    f for f in image_files if not os.path.basename(f).startswith(".")
                ]

                if not image_files:
                    print("No image files found in the images directory")
                else:
                    print(f"Found {len(image_files)} image files to process")
                    media_files.extend(image_files)

        # Process videos if requested
        if process_videos:
            # Directory containing videos to process
            videos_dir = os.path.join(os.path.dirname(__file__), "videos")

            if not os.path.exists(videos_dir):
                print(f"Videos directory not found: {videos_dir}")
            else:
                # Find all video files
                video_extensions = ["*.mp4", "*.mov", "*.avi", "*.mkv"]
                video_files: List[str] = []

                for ext in video_extensions:
                    video_files.extend(glob.glob(os.path.join(videos_dir, ext)))
                    video_files.extend(glob.glob(os.path.join(videos_dir, ext.upper())))

                # Skip .gitkeep and other hidden files
                video_files = [
                    f for f in video_files if not os.path.basename(f).startswith(".")
                ]

                if not video_files:
                    print("No video files found in the videos directory")
                else:
                    print(f"Found {len(video_files)} video files to process")
                    media_files.extend(video_files)

        if not media_files:
            print("No media files found to process")
            return

        # Sort files by size (process smaller files first)
        media_files.sort(key=os.path.getsize)

        # Process all files with limited concurrency
        print(
            f"\nStarting batch processing with max {max_concurrent} concurrent files..."
        )
        start_time = time.time()

        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(file_path: str) -> Dict[str, Any]:
            async with semaphore:
                return await process_file(
                    client,
                    file_path,
                    {"polling_interval": 3000},  # 3 seconds between polls
                )

        # Create tasks for all files
        tasks = [process_with_semaphore(file_path) for file_path in media_files]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # Calculate processing time
        total_time = time.time() - start_time

        # Summarize results
        print("\nBatch processing complete!")
        print(f"Processed {len(media_files)} files in {total_time:.2f} seconds")
        print(
            f"Average processing time: {total_time / len(media_files):.2f} seconds per file"
        )

        # Count files by type and detection status
        status_counts: Dict[str, int] = {}
        type_counts: Dict[str, int] = {"image": 0, "video": 0}
        errors = 0

        for res in results:
            if "file_type" in res:
                type_counts[res["file_type"]] = type_counts.get(res["file_type"], 0) + 1

            if "error" in res:
                errors += 1
            elif "result" in res:
                status = res["result"]["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

        print("\nResults by file type:")
        for file_type, count in type_counts.items():
            print(f"  {file_type}: {count} files")

        print("\nResults by detection status:")
        for status, count in status_counts.items():
            print(f"  {status}: {count} files")

        if errors > 0:
            print(f"\n{errors} files had errors during processing")

    except RealityDefenderError as e:
        print(f"Error: {e.message} (Code: {e.code})")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        # Properly close the client session
        if client:
            await client.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch processing example for Reality Defender SDK"
    )
    parser.add_argument(
        "--images-only", action="store_true", help="Process only image files"
    )
    parser.add_argument(
        "--videos-only", action="store_true", help="Process only video files"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent files to process",
    )
    args = parser.parse_args()

    process_images = not args.videos_only
    process_videos = not args.images_only

    print("Reality Defender SDK - Batch Processing Example\n")
    asyncio.run(
        batch_process_directories(
            process_images=process_images,
            process_videos=process_videos,
            max_concurrent=args.concurrent,
        )
    )
    print("\nExample complete!")
