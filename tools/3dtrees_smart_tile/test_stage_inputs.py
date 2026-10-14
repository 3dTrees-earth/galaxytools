"""Offline tests for the Galaxy input staging boundary."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from stage_inputs import stage_inputs, staged_name


@pytest.fixture
def inputs(tmp_path):
    source = tmp_path / "source with ' quotes.laz"
    source.write_bytes(b"unchanged point cloud content")
    job = tmp_path / "job"
    job.mkdir()
    return source, job


def group(source, *names, directory="input_dir", ext="laz"):
    return {"directory": directory, "files": [
        {"path": str(source), "name": name, "ext": ext} for name in names
    ]}


@pytest.mark.parametrize("name,ext,expected", [
    ("tile", "laz", "tile.laz"),
    ("tile.laz", "laz", "tile.laz"),
    ("tile.LAS", "laz", "tile.laz"),
    ("tile.copc.laz", "laz", "tile.copc.laz"),
    ("tile.copc", "laz", "tile.copc.laz"),
    ("tile_trees.txt", "txt", "tile_trees.txt"),
    ("tile_trees_info", "txt", "tile_trees_info.txt"),
    ("tile_trees_mesh.ply", "plybinary", "tile_trees_mesh.ply"),
    ("tile.laz.laz", "laz", "tile.laz.laz"),
])
def test_physical_suffix_is_normalized_once(name, ext, expected):
    assert staged_name(name, ext) == expected


def test_cli_stages_literal_names_and_preserves_inputs(inputs):
    source, job = inputs
    before = (hashlib.sha256(source.read_bytes()).hexdigest(), source.stat().st_mtime_ns)
    names = ["with spaces", "single' and double\"quotes", "$(touch OWNED)", "`touch OWNED`", "a;touch OWNED"]
    manifest = job / "inputs.json"
    manifest.write_text(json.dumps([group(source, *names)]))
    subprocess.run([sys.executable, str(Path(__file__).with_name("stage_inputs.py")), str(manifest)],
                   cwd=job, check=True, capture_output=True, text=True)
    for name in names:
        staged = job / "input_dir" / f"{name}.laz"
        assert staged.is_symlink()
        assert os.readlink(staged) == str(source)
        assert staged.read_bytes() == source.read_bytes()
    assert not (job / "OWNED").exists()
    assert before == (hashlib.sha256(source.read_bytes()).hexdigest(), source.stat().st_mtime_ns)


def test_nested_groups_keep_rct_pairs_and_copc_twins(inputs):
    source, job = inputs
    directory = "input_prediction_collections/collection_0"
    stage_inputs([
        group(source, "tile.laz", "tile.copc.laz", directory=directory),
        group(source, "tile_trees.txt", "tile_trees_info.txt", directory=directory, ext="txt"),
        group(source, "tile_trees_mesh.ply", directory=directory, ext="plybinary"),
    ], job)
    assert {path.name for path in (job / directory).iterdir()} == {
        "tile.laz", "tile.copc.laz", "tile_trees.txt", "tile_trees_info.txt", "tile_trees_mesh.ply"
    }


@pytest.mark.parametrize("name", ["", " ", ".", "..", "../escape", "a/b", "a\\b", "a\n", "a\0b", "a\x85b", ".laz", "..laz"])
def test_unsafe_names_fail_before_any_links(inputs, name):
    source, job = inputs
    with pytest.raises(ValueError):
        stage_inputs([group(source, "valid", name)], job)
    assert list(job.iterdir()) == []


@pytest.mark.parametrize("directory", ["", ".", "..", "/absolute", "a/../b", "a//b", "a\\b", "a\nb"])
def test_unsafe_directories_are_rejected(inputs, directory):
    source, job = inputs
    with pytest.raises(ValueError):
        stage_inputs([group(source, "tile", directory=directory)], job)
    assert list(job.iterdir()) == []


@pytest.mark.parametrize("names", [("tile", "tile.laz"), ("Tile", "tile.LAZ")])
def test_duplicate_normalized_names_fail_before_any_links(inputs, names):
    source, job = inputs
    with pytest.raises(ValueError, match="Duplicate"):
        stage_inputs([group(source, names[0]), group(source, names[1])], job)
    assert list(job.iterdir()) == []


@pytest.mark.parametrize("existing_kind", ["file", "broken_link", "source_link"])
def test_existing_destination_is_never_overwritten(inputs, existing_kind):
    source, job = inputs
    directory = job / "input_dir"
    directory.mkdir()
    existing = directory / "tile.laz"
    if existing_kind == "file":
        existing.write_bytes(b"previous content")
    else:
        existing.symlink_to(source if existing_kind == "source_link" else job / "missing")
    before = existing.lstat()
    with pytest.raises(ValueError, match="existing"):
        stage_inputs([group(source, "valid", "tile")], job)
    assert existing.lstat().st_ino == before.st_ino
    assert not (directory / "valid.laz").exists()


def test_symlink_directory_cannot_escape_job(inputs):
    source, job = inputs
    (job / "input_dir").symlink_to(source.parent, target_is_directory=True)
    with pytest.raises(ValueError, match="regular directory"):
        stage_inputs([group(source, "escaped")], job)
    assert not (source.parent / "escaped.laz").exists()


def test_existing_case_variant_is_a_collision(inputs):
    source, job = inputs
    (job / "input_dir").mkdir()
    existing = job / "input_dir" / "Tile.LAZ"
    existing.write_bytes(b"previous content")
    with pytest.raises(ValueError, match="existing"):
        stage_inputs([group(source, "tile")], job)
    assert existing.read_bytes() == b"previous content"
    assert not (job / "input_dir" / "tile.laz").exists()


def test_link_failure_removes_only_links_created_by_this_call(inputs, monkeypatch):
    source, job = inputs
    symlink = os.symlink

    def fail_second_link(target, destination):
        if destination.name == "second.laz":
            raise OSError("simulated filesystem failure")
        symlink(target, destination)

    monkeypatch.setattr(os, "symlink", fail_second_link)
    with pytest.raises(OSError, match="simulated"):
        stage_inputs([group(source, "first", "second")], job)
    assert list((job / "input_dir").iterdir()) == []
    assert source.read_bytes() == b"unchanged point cloud content"


def test_filename_directory_conflict_is_preflighted(inputs):
    source, job = inputs
    with pytest.raises(ValueError, match="conflicts"):
        stage_inputs([group(source, "tile"), group(source, "child", directory="input_dir/tile.laz")], job)
    assert list(job.iterdir()) == []


@pytest.mark.parametrize("source_kind", ["relative", "missing", "directory"])
def test_invalid_sources_fail_before_links(inputs, source_kind):
    source, job = inputs
    invalid = {"relative": Path("relative.laz"), "missing": job / "missing.laz", "directory": job}[source_kind]
    with pytest.raises(ValueError, match="existing absolute file"):
        stage_inputs([group(source, "valid"), group(invalid, "invalid")], job)
    assert list(job.iterdir()) == []


def test_unsupported_datatype_is_rejected(inputs):
    source, job = inputs
    with pytest.raises(ValueError, match="datatype"):
        stage_inputs([group(source, "tile", ext="../../laz")], job)
    assert list(job.iterdir()) == []
