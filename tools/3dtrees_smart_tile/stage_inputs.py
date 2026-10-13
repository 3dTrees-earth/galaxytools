#!/usr/bin/env python3
"""Stage Galaxy datasets as named symlinks: python stage_inputs.py MANIFEST.json.

The manifest is a list of {"directory": relative_path, "files": [{"path":
absolute_source_path, "name": element_identifier, "ext": galaxy_datatype}]}.
All destination directories are relative to the current job directory.
"""

import argparse
import json
import os
from pathlib import Path
import unicodedata


PHYSICAL_EXTENSIONS = {
    "las": "las", "laz": "laz", "txt": "txt", "ply": "ply", "plybinary": "ply",
}


def _component(value):
    if (not isinstance(value, str) or not value.strip() or value in {".", ".."}
            or "/" in value or "\\" in value
            or any(unicodedata.category(char) == "Cc" for char in value)):
        raise ValueError(f"Unsafe path component: {value!r}")
    return value


def staged_name(name, ext):
    """Replace one physical suffix with the datatype's authoritative suffix."""
    name = _component(name)
    if not isinstance(ext, str) or ext.lower() not in PHYSICAL_EXTENSIONS:
        raise ValueError(f"Unsupported input datatype: {ext!r}")
    if name.lower().endswith((".las", ".laz", ".txt", ".ply")):
        name = _component(name[:-4])
    return f"{name}.{PHYSICAL_EXTENSIONS[ext.lower()]}"


def stage_inputs(groups, root=None):
    """Preflight the complete manifest, then create links without overwrites."""
    root = Path.cwd() if root is None else Path(root)
    root = root.resolve(strict=True)
    if not isinstance(groups, list):
        raise ValueError("Input manifest must be a list of directory groups")
    links = []
    destinations = set()
    directories = set()
    existing_names = {}
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("directory"), str):
            raise ValueError("Each input group needs a relative directory")
        parts = [_component(part) for part in group["directory"].split("/")]
        directory = root.joinpath(*parts)
        parent = directory
        while parent != root:
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f"Staging directory is not a regular directory: {parent}")
            directories.add(parent)
            parent = parent.parent
        if directory not in existing_names:
            existing_names[directory] = (
                {child.name.casefold() for child in directory.iterdir()}
                if directory.exists() else set()
            )
        files = group.get("files")
        if not isinstance(files, list):
            raise ValueError("Each input group needs a list of files")
        for entry in files:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise ValueError("Each input file needs an absolute source path")
            source = Path(entry["path"])
            if not source.is_absolute() or not source.is_file():
                raise ValueError(f"Input is not an existing absolute file: {source}")
            destination = directory / staged_name(entry.get("name"), entry.get("ext"))
            key = str(destination.relative_to(root)).casefold()
            if key in destinations or destination.name.casefold() in existing_names[directory]:
                raise ValueError(f"Duplicate or existing staged filename: {destination}")
            destinations.add(key)
            links.append((source, destination))
    directory_keys = {str(path.relative_to(root)).casefold() for path in directories}
    if destinations & directory_keys:
        raise ValueError("A staged filename conflicts with a staging directory")
    created = []
    try:
        for directory in sorted(directories, key=lambda path: len(path.parts)):
            directory.mkdir(exist_ok=True)
        for source, destination in links:
            os.symlink(source, destination)
            created.append(destination)
    except OSError:
        for destination in reversed(created):
            destination.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSON input staging manifest")
    args = parser.parse_args()
    try:
        stage_inputs(json.loads(args.manifest.read_text()))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot stage inputs: {exc}\n")


if __name__ == "__main__":
    main()
