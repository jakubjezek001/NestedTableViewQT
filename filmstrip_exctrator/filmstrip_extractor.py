"""Filmstrip Extractor Module.

This module provides functionality to extract frames from videos or image
sequences and create filmstrip images using oiiotool and ffmpeg.
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


def _get_oiiotool_path() -> str:
    """Get oiiotool executable path from environment variables.

    Returns:
        str: Path to oiiotool executable.

    Raises:
        FilmstripExtractorError: If OIIOTOOL_PATH is not set.
    """
    oiiotool_path = os.getenv("OIIOTOOL_PATH")
    if not oiiotool_path:
        raise FilmstripExtractorError(
            "OIIOTOOL_PATH environment variable is not set"
        )
    return oiiotool_path


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


def _is_video_file(file_path: Union[str, Path]) -> bool:
    """Check if the given file is a video file.

    Args:
        file_path: Path to the file to check.

    Returns:
        bool: True if file is a video, False otherwise.
    """
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    return Path(file_path).suffix.lower() in video_extensions


def _get_image_sequence_info(
    input_path: Union[str, Path],
) -> Tuple[str, int, int]:
    """Get information about an image sequence.

    Args:
        input_path: Path to first image or sequence pattern.

    Returns:
        tuple: (sequence_pattern, start_frame, end_frame)

    Raises:
        FilmstripExtractorError: If sequence info cannot be determined.
    """
    input_path = Path(input_path)

    if input_path.is_file():
        # Single file - find sequence pattern
        parent = input_path.parent
        name_parts = input_path.stem.split(".")

        if len(name_parts) < 2:
            raise FilmstripExtractorError(
                f"Cannot determine sequence pattern from {input_path}"
            )

        base_name = name_parts[0]
        frame_num = name_parts[1]
        extension = input_path.suffix

        # Find all matching files
        pattern = f"{base_name}.*{extension}"
        matching_files = list(parent.glob(pattern))

        if not matching_files:
            raise FilmstripExtractorError(
                f"No sequence files found matching pattern {pattern}"
            )

        # Extract frame numbers
        frame_numbers = []
        for file in matching_files:
            parts = file.stem.split(".")
            if len(parts) >= 2:
                try:
                    frame_numbers.append(int(parts[1]))
                except ValueError:
                    continue

        if not frame_numbers:
            raise FilmstripExtractorError("No valid frame numbers found")

        start_frame = min(frame_numbers)
        end_frame = max(frame_numbers)

        # Create oiiotool sequence pattern
        padding = len(frame_num)
        sequence_pattern = str(parent / f"{base_name}.%0{padding}d{extension}")

        return sequence_pattern, start_frame, end_frame
    else:
        raise FilmstripExtractorError(f"Input path {input_path} is not a file")


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
        f"fps={fps},scale={resolution[0]}:{resolution[1]}",
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


def _extract_frames_from_sequence(
    input_sequence: Union[str, Path],
    output_dir: Union[str, Path],
    resolution: Tuple[int, int],
    fps: int,
) -> List[Path]:
    """Extract frames from an image sequence using oiiotool.

    Args:
        input_sequence: Path to first image in sequence.
        output_dir: Directory to save extracted frames.
        resolution: Target resolution (width, height).
        fps: Frames per second to extract (used for frame selection).

    Returns:
        list: List of extracted frame paths.

    Raises:
        FilmstripExtractorError: If frame extraction fails.
    """
    oiiotool_path = _get_oiiotool_path()
    output_dir = Path(output_dir)

    # Get sequence information
    sequence_pattern, start_frame, end_frame = _get_image_sequence_info(
        input_sequence
    )

    total_frames = end_frame - start_frame + 1

    # Calculate frame step based on fps (assuming 24fps original)
    original_fps = 24  # Default assumption
    frame_step = max(1, original_fps // fps)

    # Select frames to extract
    selected_frames = []
    for i in range(start_frame, end_frame + 1, frame_step):
        selected_frames.append(i)

    extracted_files = []

    for i, frame_num in enumerate(selected_frames):
        input_file = sequence_pattern % frame_num
        output_file = output_dir / f"frame_{i + 1:04d}.png"

        # Build oiiotool command
        cmd = [
            oiiotool_path,
            input_file,
            "--resize",
            f"{resolution[0]}x{resolution[1]}",
            "-o",
            str(output_file),
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            extracted_files.append(output_file)
            logger.debug(f"Processed frame {frame_num} -> {output_file}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to process frame {frame_num}: {e}")
            continue

    if not extracted_files:
        raise FilmstripExtractorError("No frames were successfully extracted")

    logger.info(f"Extracted {len(extracted_files)} frames from sequence")
    return extracted_files


def _create_filmstrip_with_oiiotool(
    frame_files: List[Path], output_path: Union[str, Path], padding: int
) -> None:
    """Create a filmstrip from frame files using oiiotool.

    Args:
        frame_files: List of frame file paths.
        output_path: Path for output filmstrip image.
        padding: Padding between images in pixels.

    Raises:
        FilmstripExtractorError: If filmstrip creation fails.
    """
    oiiotool_path = _get_oiiotool_path()
    output_path = Path(output_path)

    if not frame_files:
        raise FilmstripExtractorError("No frame files provided")

    # Build oiiotool command for horizontal filmstrip
    cmd = [oiiotool_path]

    # Add all input files
    for frame_file in frame_files:
        cmd.append(str(frame_file))

    # Add mosaic command with padding
    cmd.extend(
        [
            "--mosaic",
            f"{len(frame_files)}x1",
            # "--fill",
            # f"{padding}",
            "-o",
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
    input_file_or_sequence: str,
    output_dir: str,
    resolution: Tuple[int, int],
    padding: int,
    fps: int,
    output_filmstrip_image_path: str,
) -> None:
    """Create a filmstrip from video or image sequence.

    This function extracts frames from a video file or image sequence,
    creates a horizontal filmstrip with padding, and cleans up
    intermediate files.

    Args:
        input_file_or_sequence: Path to input video file or image sequence.
        output_dir: Directory for temporary intermediate images.
        resolution: Target resolution as (width, height) tuple.
        padding: Padding between images in the filmstrip (pixels).
        fps: Frames per second for frame extraction.
        output_filmstrip_image_path: Path for output filmstrip image.

    Raises:
        FilmstripExtractorError: If any step in the process fails.
    """
    input_path = Path(input_file_or_sequence)
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
        if _is_video_file(input_path):
            logger.info("Processing video file")
            frame_files = _extract_frames_from_video(
                input_path, temp_dir, resolution, fps
            )
        else:
            logger.info("Processing image sequence")
            frame_files = _extract_frames_from_sequence(
                input_path, temp_dir, resolution, fps
            )

        # Create filmstrip
        logger.info("Creating filmstrip")
        _create_filmstrip_with_oiiotool(
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
        input_file_or_sequence=input_file,
        output_dir="",  # Use temp directory
        resolution=(320, 240),
        padding=5,
        fps=5,
        output_filmstrip_image_path=output_file,
    )
