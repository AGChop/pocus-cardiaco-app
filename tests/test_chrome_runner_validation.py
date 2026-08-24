import os
import shutil
import pytest
from tests.helpers.chrome_runner import run_js_in_chrome, resolve_chrome_path


def test_validation_invalid_harness_type():
    with pytest.raises(ValueError, match="Invalid harness_type: 'unknown'"):
        run_js_in_chrome("console.log('test');", harness_type="unknown")


def test_validation_timeout_zero():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        run_js_in_chrome("console.log('test');", timeout=0)


def test_validation_timeout_negative():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        run_js_in_chrome("console.log('test');", timeout=-5)


def test_validation_virtual_time_budget_negative():
    with pytest.raises(ValueError, match="virtual_time_budget must be greater than or equal to 0"):
        run_js_in_chrome("console.log('test');", virtual_time_budget=-1)


def test_validation_chrome_path_nonexistent(monkeypatch):
    monkeypatch.setattr("tests.helpers.chrome_runner.CHROME_PATH", "/path/to/nonexistent/chrome")
    with pytest.raises(FileNotFoundError, match="Chrome executable not found at:"):
        run_js_in_chrome("console.log('test');")


def test_resolve_chrome_path_env_priority(monkeypatch):
    monkeypatch.setenv("CHROME_PATH", "/custom/env/chrome")
    assert resolve_chrome_path() == "/custom/env/chrome"


def test_resolve_chrome_path_shutil_which(monkeypatch):
    monkeypatch.delenv("CHROME_PATH", raising=False)
    # Ensure CHROME_PATH variable is set to default
    monkeypatch.setattr("tests.helpers.chrome_runner.CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

    monkeypatch.setattr(shutil, "which", lambda cmd: "/mock/bin/google-chrome-stable" if cmd == "google-chrome-stable" else None)
    assert resolve_chrome_path() == "/mock/bin/google-chrome-stable"
