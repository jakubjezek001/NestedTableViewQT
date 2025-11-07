"""Main entry point for the filmstrip extractor package.

This module provides a command-line interface for creating filmstrips
from videos or image sequences.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Tuple

from filmstrip_extractor import FilmstripExtractorError, create_filmstrip


def parse_resolution(resolution_str: str) -> Tuple[int, int]:
    """Parse resolution string into tuple.

    Args:
        resolution_str: Resolution string in format "WIDTHxHEIGHT".

    Returns:
        tuple: (width, height) as integers.

    Raises:
        argparse.ArgumentTypeError: If format is invalid.
    """
    try:
        width_str, height_str = resolution_str.lower().split("x")
        width = int(width_str)
        height = int(height_str)
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")
        return (width, height)
    except (ValueError, TypeError) as e:
        raise argparse.ArgumentTypeError(
            f"Invalid resolution format '{resolution_str}'. "
            f"Use format WIDTHxHEIGHT (e.g., '1920x1080')"
        ) from e


def setup_logging(verbose: bool) -> None:
    """Set up logging configuration.

    Args:
        verbose: If True, enable debug logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser.
    """
    parser = argparse.ArgumentParser(
        description="Create filmstrips from videos or image sequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create filmstrip from video
  python -m filmstrip_exctrator video.mp4 output.jpg

  # Create filmstrip from image sequence
  python -m filmstrip_exctrator sequence.0001.exr output.jpg

  # Custom resolution and settings
  python -m filmstrip_exctrator video.mp4 output.jpg \\
    --resolution 1920x1080 --fps 10 --padding 10

  # Use custom temporary directory
  python -m filmstrip_exctrator video.mp4 output.jpg \\
    --temp-dir /tmp/frames --verbose
        """,
    )

    # Required arguments
    parser.add_argument(
        "input", type=str, help="Input video file or first image in sequence"
    )

    parser.add_argument(
        "output", type=str, help="Output filmstrip image path (JPG format)"
    )

    # Optional arguments
    parser.add_argument(
        "--resolution",
        "-r",
        type=parse_resolution,
        default=(320, 240),
        help="Output resolution in WIDTHxHEIGHT format (default: 320x240)",
    )

    parser.add_argument(
        "--fps",
        "-f",
        type=int,
        default=5,
        help="Frames per second for extraction (default: 5)",
    )

    parser.add_argument(
        "--padding",
        "-p",
        type=int,
        default=5,
        help="Padding between images in pixels (default: 5)",
    )

    parser.add_argument(
        "--temp-dir",
        "-t",
        type=str,
        default="",
        help="Temporary directory for intermediate files "
        "(default: system temp)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate parsed arguments.

    Args:
        args: Parsed command-line arguments.

    Raises:
        SystemExit: If validation fails.
    """
    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(
            f"Error: Input file does not exist: {input_path}", file=sys.stderr
        )
        sys.exit(1)

    # Check output directory is writable
    output_path = Path(args.output)
    output_dir = output_path.parent

    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(
                f"Error: Cannot create output directory {output_dir}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate numeric arguments
    if args.fps <= 0:
        print("Error: FPS must be positive", file=sys.stderr)
        sys.exit(1)

    if args.padding < 0:
        print("Error: Padding cannot be negative", file=sys.stderr)
        sys.exit(1)

    # Check temp directory if specified
    if args.temp_dir:
        temp_path = Path(args.temp_dir)
        if temp_path.exists() and not temp_path.is_dir():
            print(
                f"Error: Temp path exists but is not a directory: {temp_path}",
                file=sys.stderr,
            )
            sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validate arguments
    validate_arguments(args)

    # Log configuration
    logger.info("Starting filmstrip extraction")
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Resolution: {args.resolution[0]}x{args.resolution[1]}")
    logger.info(f"FPS: {args.fps}")
    logger.info(f"Padding: {args.padding}")

    if args.temp_dir:
        logger.info(f"Temp directory: {args.temp_dir}")

    try:
        # Create filmstrip
        create_filmstrip(
            input_file_or_sequence=args.input,
            output_dir=args.temp_dir,
            resolution=args.resolution,
            padding=args.padding,
            fps=args.fps,
            output_filmstrip_image_path=args.output,
        )

        logger.info("Filmstrip creation completed successfully")
        print(f"Filmstrip saved to: {args.output}")

    except FilmstripExtractorError as e:
        logger.error(f"Filmstrip extraction failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("Operation cancelled", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
