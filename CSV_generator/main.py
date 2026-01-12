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
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
from typing import Optional

import clique
from parse import parse

PATH_PARSER_TEMPLATE = (
    "/{YY}{MM}{DD}_{set_name}_{product_variant}_{product_subvariant}/{file}"
)
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
    },
    "geometry": {
        "media_type": "geometry",
        "is_sequence": False,
        "extensions": [".obj", ".fbx", ".abc"],
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
    representation_name: str = ""
    representation_tags: list = field(default_factory=list)
    optional_attrs: OptionalAttributes = field(
        default_factory=OptionalAttributes
    )

    def parse_tokens(self) -> None:
        """Parse file path using PATH_PARSER_TEMPLATE to extract tokens."""
        tokens = {}
        parsed = parse(PATH_PARSER_TEMPLATE, self.file_path.as_posix())
        if parsed:
            tokens = getattr(parsed, "named", {})
        self._tokens.update(tokens)

    def tokens(self) -> dict:
        """Return the parsed tokens from the file path."""
        return self._tokens


def main(input_directory: str):
    file_items = []
    # loop input directory and process each file item
    for root, dirs, _ in os.walk(input_directory):
        for dir_name in dirs:
            dir_path = Path(root, dir_name)
            # list all files in directory and exclude those starting with '.'
            dir_files = [
                file.as_posix()
                for file in list(dir_path.glob("*"))
                if not file.name.startswith(".")
            ]
            pprint(dir_files)
            collections, reminders = clique.assemble(dir_files)

            if collections:
                for coll in collections:
                    # file path converted to padded hash version
                    file_name = coll.format("{head}{padding}{tail}")
                    file_path = dir_path / file_name
                    file_items.append(
                        FileItem(
                            file_path=file_path,
                            file_name=file_name,
                            file_ext=coll.tail,
                            is_sequence=True,
                            __files__=[
                                (dir_path / file).resolve().as_posix()
                                for file in coll
                            ],
                        )
                    )

            if reminders:
                for reminder in reminders:
                    file_path = dir_path / reminder
                    file_name = file_path.stem
                    file_ext = file_path.suffix
                    file_items.append(
                        FileItem(
                            file_path=file_path,
                            file_name=file_name,
                            file_ext=file_ext,
                            is_sequence=False,
                            __files__=[file_path.resolve().as_posix()],
                        )
                    )

    pprint(file_items)


if __name__ == "__main__":
    input_directory = r"I:\Shared drives\AYON test data\editorial_data\advanced_editorial_testing_data\inputs"
    main(input_directory)
