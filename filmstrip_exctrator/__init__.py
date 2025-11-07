"""Filmstrip Extractor Package.

A Python package for extracting frames from videos or image sequences
and creating filmstrip images using oiiotool and ffmpeg.
"""

from .filmstrip_extractor import create_filmstrip

__version__ = "1.0.0"
__author__ = "Filmstrip Extractor Team"

__all__ = ["create_filmstrip"]
