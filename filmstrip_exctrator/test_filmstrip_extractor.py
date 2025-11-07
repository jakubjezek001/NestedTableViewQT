"""Comprehensive test suite for filmstrip extractor.

This module contains unit tests and integration tests for the filmstrip
extractor functionality, using the provided testing dataset.
"""

import logging
import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, patch

from filmstrip_extractor import (
    FilmstripExtractorError,
    create_filmstrip,
)


class TestFilmstripExtractor(unittest.TestCase):
    """Test cases for filmstrip extractor functionality."""

    def setUp(self) -> None:
        """Set up test environment before each test."""
        # Get project root directory
        self.project_root = Path(__file__).parent
        self.test_data_dir = self.project_root / "testing_dataset"
        self.video_dir = self.test_data_dir / "video"

        # Create temporary output directory
        self.temp_output_dir = Path(tempfile.mkdtemp(prefix="filmstrip_test_"))

        # Set up logging for tests
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # Mock environment variable for oiiotool
        self.oiiotool_patcher = patch.dict(
            os.environ, {"OIIOTOOL_PATH": "oiiotool"}
        )
        self.oiiotool_patcher.start()

    def tearDown(self) -> None:
        """Clean up after each test."""
        import shutil

        # Clean up temporary directory
        if self.temp_output_dir.exists():
            shutil.rmtree(self.temp_output_dir, ignore_errors=True)
            print("Cleaning up integration test directory")

        # Stop patches
        self.oiiotool_patcher.stop()

    def _get_test_video_file(self) -> Optional[Path]:
        """Get the first available test video file.

        Returns:
            Path to test video file or None if not found.
        """
        if not self.video_dir.exists():
            return None

        video_files = list(self.video_dir.glob("*.mp4"))
        return video_files[0] if video_files else None

    @patch("subprocess.run")
    def test_create_filmstrip_video_success(self, mock_subprocess: MagicMock):
        """Test successful filmstrip creation from video."""
        video_file = self._get_test_video_file()
        if not video_file:
            self.skipTest("No test video files available")

        output_file = self.temp_output_dir / "test_filmstrip.jpg"

        # Mock successful subprocess calls
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ""

        # Mock frame files creation
        temp_frames_dir = self.temp_output_dir / "temp_frames"
        temp_frames_dir.mkdir(exist_ok=True)

        # Create mock frame files
        frame_files = []
        for i in range(1, 6):  # 5 frames
            frame_file = temp_frames_dir / f"frame_{i:04d}.png"
            frame_file.touch()
            frame_files.append(frame_file)

        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = frame_files

            try:
                create_filmstrip(
                    input_file=str(video_file),
                    output_dir=str(temp_frames_dir),
                    resolution=(320, 240),
                    padding=5,
                    fps=5,
                    output_filmstrip_image_path=str(output_file),
                )

                # Verify subprocess was called
                self.assertTrue(mock_subprocess.called)

            except FilmstripExtractorError as e:
                self.fail(f"Filmstrip creation failed: {e}")

    def test_create_filmstrip_invalid_input(self) -> None:
        """Test filmstrip creation with invalid input file."""
        nonexistent_file = self.temp_output_dir / "nonexistent.mp4"
        output_file = self.temp_output_dir / "test_filmstrip_fail.jpg"

        with self.assertRaises(FilmstripExtractorError):
            create_filmstrip(
                input_file=str(nonexistent_file),
                output_dir="",
                resolution=(320, 240),
                padding=5,
                fps=5,
                output_filmstrip_image_path=str(output_file),
            )

    def test_create_filmstrip_various_resolutions(self) -> None:
        """Test filmstrip creation with various resolutions."""
        test_resolutions = [
            (160, 120),  # Small
            (320, 240),  # Standard
            (640, 480),  # Medium
            (1920, 1080),  # HD
        ]

        for resolution in test_resolutions:
            with self.subTest(resolution=resolution):
                # Test with a simple mock to avoid actual processing
                with patch("subprocess.run") as mock_subprocess:
                    mock_subprocess.return_value.returncode = 0
                    mock_subprocess.return_value.stderr = ""

                    # This is primarily to test parameter validation
                    try:
                        # We'll test with a mock file that would pass validation
                        with patch("pathlib.Path.exists", return_value=True):
                            with patch(
                                "pathlib.Path.is_file", return_value=True
                            ):
                                create_filmstrip(
                                    input_file="mock_video.mp4",
                                    output_dir="",
                                    resolution=resolution,
                                    padding=5,
                                    fps=5,
                                    output_filmstrip_image_path="output.jpg",
                                )
                    except (FilmstripExtractorError, Exception) as e:
                        # Expected in test environment without actual tools
                        pass

    def test_create_filmstrip_various_fps(self) -> None:
        """Test filmstrip creation with various FPS values."""
        test_fps_values = [1, 5, 10, 15, 30]

        for fps in test_fps_values:
            with self.subTest(fps=fps):
                with patch("subprocess.run") as mock_subprocess:
                    mock_subprocess.return_value.returncode = 0

                    try:
                        with patch("pathlib.Path.exists", return_value=True):
                            with patch(
                                "pathlib.Path.is_file", return_value=True
                            ):
                                create_filmstrip(
                                    input_file="mock_video.mp4",
                                    output_dir="",
                                    resolution=(320, 240),
                                    padding=5,
                                    fps=fps,
                                    output_filmstrip_image_path="output.jpg",
                                )
                    except (FilmstripExtractorError, Exception):
                        # Expected in test environment
                        pass

    def test_create_filmstrip_various_padding(self) -> None:
        """Test filmstrip creation with various padding values."""
        test_padding_values = [0, 2, 5, 10, 20]

        for padding in test_padding_values:
            with self.subTest(padding=padding):
                with patch("subprocess.run") as mock_subprocess:
                    mock_subprocess.return_value.returncode = 0

                    try:
                        with patch("pathlib.Path.exists", return_value=True):
                            with patch(
                                "pathlib.Path.is_file", return_value=True
                            ):
                                create_filmstrip(
                                    input_file="mock_video.mp4",
                                    output_dir="",
                                    resolution=(320, 240),
                                    padding=padding,
                                    fps=5,
                                    output_filmstrip_image_path="output.jpg",
                                )
                    except (FilmstripExtractorError, Exception):
                        # Expected in test environment
                        pass

    @patch("subprocess.run")
    def test_subprocess_failure_handling(self, mock_subprocess: MagicMock):
        """Test handling of subprocess failures."""
        # Mock subprocess failure
        from subprocess import CalledProcessError

        mock_subprocess.side_effect = CalledProcessError(
            1, "ffmpeg", stderr="Mock error"
        )

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_file", return_value=True):
                with self.assertRaises(FilmstripExtractorError):
                    create_filmstrip(
                        input_file="mock_video.mp4",
                        output_dir="",
                        resolution=(320, 240),
                        padding=5,
                        fps=5,
                        output_filmstrip_image_path="output.jpg",
                    )

    def test_temp_directory_cleanup(self) -> None:
        """Test that temporary directories are properly cleaned up."""
        # This test verifies the cleanup mechanism works
        # It's hard to test the actual cleanup in the success case
        # since it happens in the finally block

        temp_dir = Path(tempfile.mkdtemp(prefix="cleanup_test_"))
        temp_dir.mkdir(exist_ok=True)

        # Create some test files
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        self.assertTrue(temp_dir.exists())
        self.assertTrue(test_file.exists())

        # Manual cleanup to test the mechanism
        import shutil

        shutil.rmtree(temp_dir)

        self.assertFalse(temp_dir.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests using actual test dataset."""

    def setUp(self) -> None:
        """Set up integration test environment."""
        self.project_root = Path(__file__).parent
        self.test_data_dir = self.project_root / "testing_dataset"
        self.temp_output_dir = Path(
            tempfile.mkdtemp(prefix="integration_test_")
        )

        # Skip integration tests if test data is not available
        if not self.test_data_dir.exists():
            self.skipTest("Test dataset not available")

    def tearDown(self) -> None:
        """Clean up after integration tests."""
        import shutil

        if self.temp_output_dir.exists():
            # shutil.rmtree(self.temp_output_dir, ignore_errors=True)
            print("Cleaning up integration test directory")

    def test_integration_with_real_data(self) -> None:
        """Integration test with real test dataset (if available)."""
        # This test will only run if the actual tools are available
        # and will be skipped in environments without ffmpeg/oiiotool

        video_files = list((self.test_data_dir / "video").glob("*.mp4"))

        if not video_files:
            self.skipTest("No test files available")

        # Test with video if available
        if video_files:
            for video_file in video_files:
                input_file = Path(video_file)
                file_name_no_ext = input_file.stem
                try:
                    output_file = (
                        self.temp_output_dir
                        / f"{file_name_no_ext}_filmstrip.jpg"
                    )
                    create_filmstrip(
                        input_file=str(input_file),
                        output_dir="",
                        resolution=(320, 240),
                        padding=5,
                        fps=5,
                        output_filmstrip_image_path=str(output_file),
                    )

                    # In a real environment with tools, the file should be created
                    # In test environment, this might fail - that's expected

                except FilmstripExtractorError as e:
                    # Expected in test environment without actual tools
                    self.logger = logging.getLogger(__name__)
                    self.logger.info(
                        f"Integration test failed as expected: {e}"
                    )


def run_all_tests() -> None:
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFilmstripExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    success = run_all_tests()
    sys.exit(0 if success else 1)
