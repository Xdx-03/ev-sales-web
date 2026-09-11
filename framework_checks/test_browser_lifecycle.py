"""Real pytest fixtures with controlled contexts; no browser is installed or launched."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("fixture", ["ui_page", "mobile_page"])
@pytest.mark.parametrize(
    "mode",
    [
        "pass",
        "timeout-error",
        "navigation-error",
        "page-error",
        "directory-error",
        "screenshot-error",
        "allure-error",
        "capture-error",
    ],
)
def test_context_is_closed_when_setup_or_failure_evidence_breaks(
    tmp_path: Path,
    fixture: str,
    mode: str,
) -> None:
    source = (PROJECT / "tests" / "conftest.py").read_text(encoding="utf-8")
    substitute = f"""
from pathlib import Path
from types import SimpleNamespace

MODE = {mode!r}
PROJECT_ROOT = Path.cwd()
def fail(): raise RuntimeError("private-sentinel-do-not-log")
def event(value):
    with Path("events.txt").open("a", encoding="utf-8") as stream:
        stream.write(value + "\\n")
class FakePage:
    def locator(self, selector): return self
    def evaluate_all(self, script): pass
    def screenshot(self, **kwargs):
        if MODE == "screenshot-error": fail()
        Path(kwargs["path"]).write_bytes(b"synthetic image")
    def content(self): return "<html>synthetic</html>"
class FakeContext:
    def set_default_timeout(self, value):
        if MODE == "timeout-error": raise RuntimeError("synthetic setup failure")
    def set_default_navigation_timeout(self, value):
        if MODE == "navigation-error": raise RuntimeError("synthetic setup failure")
    def new_page(self):
        if MODE == "page-error": raise RuntimeError("synthetic setup failure")
        return FakePage()
    def close(self): event("closed")
class FakeBrowser:
    def new_context(self, **kwargs):
        event("created")
        return FakeContext()
@pytest.fixture
def browser(): return FakeBrowser()
@pytest.fixture
def browser_context_args(): return {{}}
@pytest.fixture
def settings(): return SimpleNamespace(action_timeout_ms=100, navigation_timeout_ms=100)
@pytest.fixture
def playwright(): return SimpleNamespace(devices={{"synthetic": {{}}}})
@pytest.fixture
def mobile_device_name(): return "synthetic"
if MODE == "directory-error":
    (PROJECT_ROOT / "artifacts").write_text("blocking file", encoding="utf-8")
if MODE == "allure-error":
    allure.attach.file = lambda *args, **kwargs: fail()
if MODE == "capture-error":
    def _capture_failure_evidence(*args): raise RuntimeError("synthetic capture failure")
"""
    (tmp_path / "conftest.py").write_text(source + substitute, encoding="utf-8")
    assertion = "assert True" if mode == "pass" else "assert False, 'original synthetic failure'"
    (tmp_path / "test_browser.py").write_text(
        f"def test_example({fixture}): {assertion}\n",
        encoding="utf-8",
    )
    environment = {key: value for key, value in os.environ.items() if not key.startswith("EV_")}
    environment.update(
        PYTHONPATH=str(PROJECT), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONIOENCODING="utf-8"
    )
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short"],
        cwd=tmp_path,
        env=environment,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert (completed.returncode == 0) == (mode == "pass"), completed.stdout + completed.stderr
    assert (tmp_path / "events.txt").read_text(encoding="utf-8").splitlines() == [
        "created",
        "closed",
    ]
    if mode in {"directory-error", "screenshot-error", "allure-error"}:
        assert "original synthetic failure" in completed.stdout
        assert "private-sentinel-do-not-log" not in completed.stdout + completed.stderr
        assert "1 failed" in completed.stdout
        assert "1 error" not in completed.stdout
