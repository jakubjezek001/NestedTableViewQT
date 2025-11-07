"""Filmstrip Extractor Module.

This module provides functionality to extract frames from videos
and create filmstrip images using oiiotool and ffmpeg.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Union

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FilmstripExtractorError(Exception):
    """Custom exception for filmstrip extractor errors."""

    pass


def _get_ffmpeg_path() -> str:
    """Get ffmpeg executable path from environment variables.

    Returns:
        str: Path to ffmpeg executable.

    Raises:
        FilmstripExtractorError: If FFMPEG_PATH is not set.
    """
    ffmpeg_path = os.getenv("FFMPEG_PATH")
    if not ffmpeg_path:
        raise FilmstripExtractorError(
            "FFMPEG_PATH environment variable is not set"
        )
    return ffmpeg_path


def _extract_frames_from_video(
    input_video: Union[str, Path],
    output_dir: Union[str, Path],
    resolution: Tuple[int, int],
    fps: int,
) -> List[Path]:
    """Extract frames from a video file using ffmpeg.

    Args:
        input_video: Path to input video file.
        output_dir: Directory to save extracted frames.
        resolution: Target resolution (width, height).
        fps: Frames per second to extract.

    Returns:
        list: List of extracted frame paths.

    Raises:
        FilmstripExtractorError: If frame extraction fails.
    """
    ffmpeg_path = _get_ffmpeg_path()
    input_video = Path(input_video)
    output_dir = Path(output_dir)

    # Create output pattern for ffmpeg
    output_pattern = output_dir / "frame_%04d.png"

    # Build ffmpeg command
    cmd = [
        ffmpeg_path,
        "-i",
        str(input_video),
        "-vf",
        f"fps={fps},scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease",
        "-y",  # Overwrite output files
        str(output_pattern),
    ]

    logger.info(f"Extracting frames with command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        logger.info("Frame extraction completed successfully")
    except subprocess.CalledProcessError as e:
        raise FilmstripExtractorError(f"FFmpeg extraction failed: {e.stderr}")

    # Get list of extracted frames
    frame_files = sorted(output_dir.glob("frame_*.png"))

    if not frame_files:
        raise FilmstripExtractorError("No frames were extracted")

    logger.info(f"Extracted {len(frame_files)} frames")
    return frame_files


def _create_filmstrip_with_ffmpeg(
    frame_files: List[Path], output_path: Union[str, Path], padding: int
) -> None:
    """Create a filmstrip from frame files using ffmpeg.

    Args:
        frame_files: List of frame file paths.
        output_path: Path for output filmstrip image.
        padding: Padding between images in pixels.

    Raises:
        FilmstripExtractorError: If filmstrip creation fails.
    """
    ffmpeg_path = _get_ffmpeg_path()
    output_path = Path(output_path)

    if not frame_files:
        raise FilmstripExtractorError("No frame files provided")

    num_frames = len(frame_files)

    # Build ffmpeg command
    cmd = [ffmpeg_path]

    # Add all input files
    for frame_file in frame_files:
        cmd.extend(["-i", str(frame_file)])

    if padding > 0:
        # For padding, we need to add padding to each image first, then hstack
        # This is more complex - let's pad each input individually
        pad_filters = []
        for i in range(num_frames):
            # Add padding to right side of each image except the last one
            if i < num_frames - 1:
                pad_filters.append(
                    f"[{i}:v]pad=iw+{padding}:ih:{padding // 2}:0[padded{i}]"
                )
            else:
                pad_filters.append(
                    f"[{i}:v]copy[padded{i}]"
                )  # No padding for last image

        padded_inputs = "".join([f"[padded{i}]" for i in range(num_frames)])
        filter_complex = f"{';'.join(pad_filters)};{padded_inputs}hstack=inputs={num_frames}[out]"

        cmd.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                "-y",
                str(output_path),
            ]
        )
    else:
        # Simple hstack without padding
        input_labels = "".join([f"[{i}:v]" for i in range(num_frames)])
        filter_complex = f"{input_labels}hstack=inputs={num_frames}[out]"

        cmd.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                "-y",
                str(output_path),
            ]
        )

    logger.info(f"Creating filmstrip with command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        logger.info(f"Filmstrip created successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        raise FilmstripExtractorError(f"Filmstrip creation failed: {e.stderr}")


def create_filmstrip(
    input_file: str,
    output_dir: str,
    resolution: Tuple[int, int],
    padding: int,
    fps: int,
    output_filmstrip_image_path: str,
) -> None:
    """Create a filmstrip from a video.

    This function extracts frames from a video file,
    creates a horizontal filmstrip with padding, and cleans up
    intermediate files.

    Args:
        input_file: Path to input video file.
        output_dir: Directory for temporary intermediate images.
        resolution: Target resolution as (width, height) tuple.
        padding: Padding between images in the filmstrip (pixels).
        fps: Frames per second for frame extraction.
        output_filmstrip_image_path: Path for output filmstrip image.

    Raises:
        FilmstripExtractorError: If any step in the process fails.
    """
    input_path = Path(input_file)
    temp_dir = None

    try:
        # Create temporary directory for intermediate files
        if output_dir:
            temp_dir = Path(output_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            temp_dir = Path(tempfile.mkdtemp(prefix="filmstrip_"))

        logger.info(f"Using temporary directory: {temp_dir}")

        # Extract frames based on input type
        logger.info("Processing video file")
        frame_files = _extract_frames_from_video(
            input_path, temp_dir, resolution, fps
        )

        # Create filmstrip
        logger.info("Creating filmstrip")
        _create_filmstrip_with_ffmpeg(
            frame_files, output_filmstrip_image_path, padding
        )

        logger.info("Filmstrip creation completed successfully")

    except Exception as e:
        logger.error(f"Filmstrip creation failed: {e}")
        raise

    finally:
        # Clean up temporary files
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_dir}: {e}")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python filmstrip_extractor.py <input> <output>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # make sure output file dir exists
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    create_filmstrip(
        input_file=input_file,
        output_dir="",  # Use temp directory
        resolution=(320, 240),
        padding=5,
        fps=5,
        output_filmstrip_image_path=output_file,
    )
