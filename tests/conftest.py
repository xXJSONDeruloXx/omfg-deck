"""
Shared fixtures for omfg-deck tests.
"""
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest


# ---------------------------------------------------------------------------
# Ensure py_modules is on the path so we can import omfg.*
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "py_modules"))


# ---------------------------------------------------------------------------
# Fake 'decky' module so imports don't explode outside the Deck
# ---------------------------------------------------------------------------
def _make_mock_decky() -> types.ModuleType:
    mod = types.ModuleType("decky")
    mod.logger = Mock()
    mod.DECKY_PLUGIN_DIR = "/homebrew/plugins/OMFG"
    mod.DECKY_USER_HOME = "/home/deck"
    mod.DECKY_HOME = "/homebrew"
    mod.DECKY_SETTINGS_DIR = "/homebrew/settings"
    mod.DECKY_LOG_DIR = "/homebrew/logs"
    mod.DECKY_RUNTIME_DIR = "/homebrew/runtime"
    mod.migrate_logs = Mock()
    mod.migrate_settings = Mock()
    mod.migrate_runtime = Mock()
    return mod


@pytest.fixture(autouse=True)
def mock_decky(monkeypatch):
    """Inject a fake 'decky' module for every test."""
    fake = _make_mock_decky()
    monkeypatch.setitem(sys.modules, "decky", fake)
    # Also patch the lazy `import decky` inside base_service.__init__
    import omfg.base_service as bs
    monkeypatch.setattr(bs, "decky", fake, raising=False)
    return fake


@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def tmp_home(tmp_path):
    """A temporary directory that stands in for Path.home()."""
    return tmp_path / "home" / "deck"


@pytest.fixture
def patched_home(tmp_home, monkeypatch):
    """Patch Path.home() to return tmp_home and create the directory."""
    tmp_home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_home))
    return tmp_home
