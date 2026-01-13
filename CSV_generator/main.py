"""CSV Generator in compliance with AYON Tray-publisher CSV Ingestion

This script should do follings:
    1. use input folder path and os walk all files and folders inside.
        This step will build a library of `file_items` as objects with attributes like name, path, extension
    2. use `parse` python module to parse file path elements to tokens and store them in `file_items` objects as `tokens` attribute
    3. classify found file_items either as file sequence, single file,
        if it is sequence then get frame range and store it in `file_items` objects as `frame_start` and `frame_end` attributes
    4. each file item should also be compared by extension with REPRESENTATION_MAPPING constant mapping for checking whether it is video file, audio file, image file, geometry model file
    5. generate CSV file with row mapping defined in CSV_ROW_MAPPING constant.

User usage:
    1. double click at sh or ps1 script will open simple gui with drop off field for folder and button for generation of CSV
    2. once Generate CSV button is pressed after while the CSV will be created at the root folder which was dropped to the field

"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
from typing import Optional

import clique
from parse import parse

PATH_PARSER_TEMPLATE = "{root}/{package_name}/{product_name}/{project_name}_{sequence}_{shot}_{subset}<.{padding}>.{extension}"
CSV_COLUMN_MAPPING = {
    "file_path": "File Path",
    "folder_path": "Folder Path",
    "task_name": "Task Name",
    "product_type": "Product Type",
    "variant": "Variant",
    "version": "Version",
    "version_comment": "Version Comment",
    "version_thumbnail_path": "Version Thumbnail",
    "shot_width": "Shot Width",
    "shot_height": "Shot Height",
    "frame_start": "Frame Start",
    "frame_end": "Frame End",
    "handle_start": "Handle Start",
    "handle_end": "Handle End",
    "fps": "FPS",
    "slate_exists": "Slate Exists",
    "representation": "Representation",
    "representation_colorspace": "Representation Colorspace",
    "representation_tags": "Representation Tags",
}
CSV_ROW_MAPPING = {
    "file_path": {
        "type": str,
        "required": True,
        "value_template": "{file_path_absolute}",
        "default": None,
    },
    "folder_path": {
        "type": str,
        "required": True,
        "value_template": "{project}/{shot}/{task}/{version}",
        "default": None,
    },
    "frame_start": {
        "type": int,
        "required": False,
        "value_template": "{frame_start}",
        "default": 1,
    },
    "frame_end": {
        "type": int,
        "required": False,
        "value_template": "{frame_end}",
        "default": 1,
    },
    "handle_start": {
        "type": int,
        "required": False,
        "value_template": None,
        "default": 0,
    },
    "handle_end": {
        "type": int,
        "required": False,
        "value_template": None,
        "default": 0,
    },
    "fps": {
        "type": float,
        "required": False,
        "value_template": "{fps}",
        "default": 24.0,
    },
    "variant": {
        "type": str,
        "required": True,
        "value_template": "{product_variant}",
        "default": None,
    },
    "version": {
        "type": int,
        "required": True,
        "value_template": "{product_version}",
        "default": 1,
    },
}
REPRESENTATION_MAPPING = {
    "image_review": {
        "media_type": "image",
        "is_sequence": True,
        "search_pattern": ".*",
        "extensions": [".jpg"],
        "tags": ["review", "webreview"],
    },
    "camera_raw": {
        "media_type": "image",
        "is_sequence": True,
        "search_pattern": ".*",
        "extensions": [".cr2", ".arw"],
        "tags": [],
    },
    "hdri_stitched": {
        "media_type": "image",
        "is_sequence": False,
        "search_pattern": ".*",
        "extensions": [".exr"],
        "tags": [""],
    },
    "pano_review": {
        "media_type": "image",
        "is_sequence": False,
        "search_pattern": ".*",
        "extensions": [".jpg"],
        "tags": ["review", "webreview"],
    },
    "ptgui_stitch": {
        "media_type": "other",
        "is_sequence": False,
        "search_pattern": ".*",
        "extensions": [".pts"],
        "tags": [],
    },
    "geometry": {
        "media_type": "geometry",
        "is_sequence": False,
        "search_pattern": ".*",
        "extensions": [".obj", ".fbx", ".abc"],
        "tags": [],
    },
}
# mapping of product and requred representations
# key: product variant
PRODUCT_TYPE_MAPPING = {
    "hdri": {
        "product_type": "image",
        "required_representations": [
            "camera_raw",
            "pano_review",
            "pano_hdr",
            "ptgui_stitch",
        ],
        "search_pattern": ".*HDRI.*",
        "thumbnail": {"file_path": "{pano_review[__files__][0]}"},
    },
    "pano": {
        "product_type": "image",
        "required_representations": [
            "camera_raw",
            "pano_review",
            "pano_hdr",
            "ptgui_stitch",
        ],
        # regex pattern for matching product preset to correct file path
        "search_pattern": ".*Pano.*",
        # pythonic expression resolving
        "thumbnail": {"file_path": "{pano_review[__files__][-1]}"},
    },
}


@dataclass
class OptionalAttributes:
    """Optional attributes for file items including frame ranges and media properties."""

    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    shot_width: Optional[int] = None
    shot_height: Optional[int] = None
    colorspace: Optional[str] = None
    fps: Optional[float] = None
    aspect_ratio: Optional[float] = None
    slate_exists: Optional[bool] = None


@dataclass
class FileItem:
    """Represents a file item with parsed metadata and media type classification.

    This class stores file path information, parsed tokens from the path,
    optional attributes, and classification data for media type and representation.
    """

    file_path: Path
    _tokens: dict = field(default_factory=dict)
    file_ext: str = ""
    file_name: str = ""
    media_type: str = ""
    is_sequence: bool = False
    __files__: list = field(default_factory=list)
    _product_preset_name: str | None = None
    _representation_preset_name: str | None = None
    representation_name: str = ""
    representation_tags: list = field(default_factory=list)
    optional_attrs: OptionalAttributes = field(
        default_factory=OptionalAttributes
    )

    def parse_tokens(self) -> None:
        """Parse file path using PATH_PARSER_TEMPLATE to extract tokens."""
        # Convert PATH_PARSER_TEMPLATE string to Path and get its parts
        template_path = Path(PATH_PARSER_TEMPLATE)
        template_parts = list(template_path.parts)

        # Get parts from this file item's path
        path_parts = list(self.file_path.parts)

        # Reverse both lists to process from end (right to left)
        template_parts.reverse()
        path_parts.reverse()

        all_tokens = {}

        # Process from end (filename first, then directories)
        for i, template_part in enumerate(template_parts):
            if i >= len(path_parts):
                message = (
                    f"Error: No corresponding path part for template part "
                    f"'{template_part}'"
                )
                # Store empty tokens and return early
                self._tokens = {}
                return

            path_part = path_parts[i]

            # Try to parse path part using template part
            result = parse(template_part, path_part)

            if result is None:
                message = (
                    f"Error: Failed to match template '{template_part}' "
                    f"with path '{path_part}'"
                )
                # If first iteration (filename) fails, stop immediately
                if i == 0:
                    # Store empty tokens and return early
                    self._tokens = {}
                    return
                continue

            # Extract tokens from parse result
            # The parse function returns a Result object with .named
            # and .fixed attributes
            # Use safe attribute access to avoid type checker warnings
            named_tokens = getattr(result, "named", {})
            fixed_tokens = getattr(result, "fixed", ())

            if named_tokens:
                # Named tokens
                all_tokens.update(named_tokens)

            # If no tokens matched but parse succeeded, it's an exact match
            if not named_tokens and not fixed_tokens:
                continue

        # Store the parsed tokens in the instance variable
        self._tokens = all_tokens

    def tokens(self) -> dict:
        """Return the parsed tokens from the file path."""
        return self._tokens

    @property
    def product_preset_name(self) -> str | None:
        """Return the product preset name."""
        return self._product_preset_name

    @product_preset_name.setter
    def product_preset_name(self, value: str | None) -> None:
        self._product_preset_name = value

    @property
    def representation_preset_name(self) -> str | None:
        """Return the representation preset name."""
        return self._representation_preset_name

    @representation_preset_name.setter
    def representation_preset_name(self, value: str | None) -> None:
        self._representation_preset_name = value


def get_hashed_file_name_from_collection(collection: clique.Collection) -> str:
    """Return the hashed file name from a collection.

    Args:
        collection (clique.Collection): The collection to get the hashed file name from.

    Returns:
        str: The hashed file name.
    """
    padding = collection.padding
    hashed_padding = "#" * padding
    head = collection.head
    tail = collection.tail
    return f"{head}{hashed_padding}{tail}"


def detect_product_preset_name(file_path: str) -> str | None:
    """Detect the product preset name from the file path.

    Args:
        file_path (str): The file path to detect the product preset name from.

    Returns:
        str | None: The product preset name if found, otherwise None.
    """
    preset_name = None
    for name, data in PRODUCT_TYPE_MAPPING.items():
        search_pattern = data["search_pattern"]
        if re.search(search_pattern, file_path):
            preset_name = name
            break

    return preset_name


def detect_representation_preset_name(
    file_path: str,
    is_sequence: bool | None = False,
    file_extension: str | None = None,
) -> str | None:
    """Detect the representation preset name from the file path.

    Args:
        file_path (str): The file path to detect the representation
            preset name from.
        is_sequence (bool | None): Whether the file is a sequence or not.
        file_extension (str | None): The file extension.

    Returns:
        str | None: The representation preset name if found, otherwise None.
    """
    preset_name = None
    for name, data in REPRESENTATION_MAPPING.items():
        search_pattern = data["search_pattern"]
        is_sequence_ = data["is_sequence"]
        extensions = data["extensions"]
        if (
            re.search(search_pattern, file_path)
            and is_sequence == is_sequence_
            and file_extension in extensions
        ):
            preset_name = name
            break

    return preset_name


def main(input_directory: str):
    file_items = []
    # loop input directory and process each file item
    for root, dirs, _ in os.walk(input_directory):
        for dir_name in dirs:
            dir_path = Path(root, dir_name)
            # detect what product is matching
            product_preset_name = detect_product_preset_name(
                dir_path.as_posix()
            )
            # list all files in directory and exclude those starting with '.'
            dir_files = [
                file.as_posix()
                for file in list(dir_path.glob("*"))
                if not file.name.startswith(".")
            ]
            collections, reminders = clique.assemble(dir_files)

            if collections:
                for coll in collections:
                    # detect what matchig representation
                    file_name = get_hashed_file_name_from_collection(coll)
                    file_path = dir_path / file_name
                    file_item = FileItem(
                        file_path=file_path,
                        file_name=file_name,
                        file_ext=coll.tail,
                        is_sequence=True,
                        __files__=[
                            (dir_path / file).resolve().as_posix()
                            for file in coll
                        ],
                    )
                    file_item.product_preset_name = product_preset_name
                    file_item.representation_preset_name = (
                        detect_representation_preset_name(
                            file_name,
                            is_sequence=True,
                            file_extension=coll.tail,
                        )
                    )
                    file_item.parse_tokens()
                    file_items.append(file_item)

            if reminders:
                for reminder in reminders:
                    file_path = dir_path / reminder
                    file_name = file_path.stem
                    file_ext = file_path.suffix
                    file_item = FileItem(
                        file_path=file_path,
                        file_name=file_name,
                        file_ext=file_ext,
                        is_sequence=False,
                        __files__=[file_path.resolve().as_posix()],
                    )
                    file_item.product_preset_name = product_preset_name
                    file_item.representation_preset_name = (
                        detect_representation_preset_name(
                            file_name,
                            is_sequence=False,
                            file_extension=file_ext,
                        )
                    )
                    file_item.parse_tokens()
                    file_items.append(file_item)

    pprint(file_items)


if __name__ == "__main__":
    input_directory = r"I:\Shared drives\AYON test data\editorial_data\advanced_editorial_testing_data\inputs"
    main(input_directory)
