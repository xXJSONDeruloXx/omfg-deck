"""
Tests for omfg.base_service — BaseService helpers.
"""
import stat
import pytest
from pathlib import Path
from omfg.base_service import BaseService
from omfg.constants import LIB_DIR, VULKAN_LAYER_DIR, CONFIG_DIR


def make_service(tmp_home, mock_logger):
    svc = BaseService(logger=mock_logger)
    svc.home = tmp_home
    svc.lib_dir = tmp_home / LIB_DIR
    svc.vulkan_layer_dir = tmp_home / VULKAN_LAYER_DIR
    svc.config_dir = tmp_home / CONFIG_DIR
    svc.lib_file = svc.lib_dir / "libVkLayer_OMFG_rust.so"
    svc.json_file = svc.vulkan_layer_dir / "VkLayer_OMFG_rust.json"
    svc.config_file = svc.config_dir / "omfg-live.toml"
    return svc


class TestEnsureDirectories:
    def test_creates_all_dirs(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        assert svc.lib_dir.exists()
        assert svc.vulkan_layer_dir.exists()
        assert svc.config_dir.exists()

    def test_idempotent(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._ensure_directories()  # should not raise


class TestRemoveIfExists:
    def test_removes_existing_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        f = patched_home / "testfile.txt"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("hello")
        assert svc._remove_if_exists(f) is True
        assert not f.exists()

    def test_returns_false_when_missing(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        f = patched_home / "nonexistent.txt"
        assert svc._remove_if_exists(f) is False

    def test_removes_directory_recursively(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        d = patched_home / "testdir"
        d.mkdir()
        (d / "child.txt").write_text("x")
        assert svc._remove_if_exists(d) is True
        assert not d.exists()


class TestAtomicWrite:
    def test_writes_content(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        target = patched_home / "out.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        svc._atomic_write(target, "hello world", 0o644)
        assert target.read_text() == "hello world"

    def test_sets_permissions(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        target = patched_home / "script.sh"
        target.parent.mkdir(parents=True, exist_ok=True)
        svc._atomic_write(target, "#!/bin/bash", 0o755)
        mode = stat.S_IMODE(target.stat().st_mode)
        assert mode == 0o755

    def test_no_temp_file_left_on_success(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        target = patched_home / "clean.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        svc._atomic_write(target, "data")
        tmp_files = list(target.parent.glob(".clean.txt.*.tmp"))
        assert len(tmp_files) == 0

    def test_overwrites_existing_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        target = patched_home / "overwrite.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("old content")
        svc._atomic_write(target, "new content")
        assert target.read_text() == "new content"
