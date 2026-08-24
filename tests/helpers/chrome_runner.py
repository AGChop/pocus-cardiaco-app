"""Helper module for running JavaScript payloads in Headless Chrome for tests."""

import os
import json
import re
import shutil
import tempfile
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, Dict

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def resolve_chrome_path() -> str:
    """Resolves the path to the Chrome executable across platforms."""
    # 1. Environment variable
    env_path = os.environ.get("CHROME_PATH")
    if env_path:
        return env_path

    # For monkeypatch compatibility in tests
    if globals().get("CHROME_PATH") != "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome":
        return globals().get("CHROME_PATH")

    # 2. Check shutil.which for common command names
    for cmd in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(cmd)
        if path:
            return path

    # 3. Check common platform-specific locations
    common_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for path in common_paths:
        if os.path.exists(path) and os.path.isfile(path):
            return path

    raise FileNotFoundError("Chrome executable not found. Please set CHROME_PATH environment variable.")


def run_js_in_chrome(
    js_payload: str,
    harness_type: str = "app",
    inject_css: bool = False,
    load_windows: bool = False,
    load_measurements: bool = False,
    timeout: int = 20,
    virtual_time_budget: int = 3000,
) -> Dict[str, Any]:
    """Runs a given JavaScript payload in a headless Chrome browser and returns the result.

    Args:
        js_payload: The JavaScript string to execute.
        harness_type: The type of harness to use ('app' or 'quiz').
        inject_css: Whether to inject styles.css.
        load_windows: Whether to load and inject windows.json.
        load_measurements: Whether to load and inject measurements.json.
        timeout: Maximum duration in seconds for Chrome subprocess execution.
        virtual_time_budget: Chrome virtual time budget in milliseconds.

    Returns:
        The JSON-parsed dictionary containing the execution results.

    Raises:
        ValueError: If harness_type is not 'app' or 'quiz', if timeout <= 0,
            or if virtual_time_budget < 0.
        FileNotFoundError: If CHROME_PATH does not exist or is not a file.
        subprocess.SubprocessError: If Chrome execution fails with a non-zero exit code.
        RuntimeError: If a JavaScript error occurs during execution.
        TimeoutError: If Chrome execution times out.
    """
    if harness_type not in ("app", "quiz"):
        raise ValueError(f"Invalid harness_type: {harness_type!r}. Must be 'app' or 'quiz'.")

    if timeout <= 0:
        raise ValueError(f"timeout must be greater than 0, got {timeout}")

    if virtual_time_budget < 0:
        raise ValueError(f"virtual_time_budget must be greater than or equal to 0, got {virtual_time_budget}")

    chrome_path = CHROME_PATH
    if chrome_path == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome":
        chrome_path = resolve_chrome_path()

    if not os.path.exists(chrome_path) or not os.path.isfile(chrome_path):
        raise FileNotFoundError(f"Chrome executable not found at: {chrome_path}")

    if harness_type == "quiz":
        # Read quiz-engine.js code
        with open("assets/js/quiz-engine.js", "r", encoding="utf-8") as f:
            quiz_engine_code = f.read()

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <div id="results"></div>
    <script>
        // Mock Storage
        const _storage = {};
        const Storage = {
            getProgress: (type, id) => _storage[type + "_" + id] || null,
            saveProgress: (type, id, data) => { _storage[type + "_" + id] = data; },
            removeProgress: (type, id) => { delete _storage[type + "_" + id]; }
        };

        // Mock MediaViewer
        const MediaViewer = {
            renderMediaSection: (media) => "<div>MOCK_MEDIA</div>",
            initializeMediaInteractions: (container) => {}
        };

        // Mock DataLoader
        const DataLoader = {
            getQuizzes: async () => [],
            getMediaResources: async () => []
        };

        // Inject QuizEngine
        //QUIZ_ENGINE_CODE//

        // Run user payload synchronously
        try {
            const resultsEl = document.getElementById("results");
            const res = (() => {
                //JS_PAYLOAD//
            })();
            resultsEl.textContent = JSON.stringify({ success: true, data: res });
        } catch (e) {
            document.getElementById("results").textContent = JSON.stringify({ success: false, error: e.message });
        } finally {
            window.close();
        }
    </script>
</body>
</html>
"""
        html_content = html_content.replace("//QUIZ_ENGINE_CODE//", quiz_engine_code)
        html_content = html_content.replace("//JS_PAYLOAD//", js_payload)

    else:
        # Default "app" harness
        with open("data/translations.json", "r", encoding="utf-8") as f:
            translations_dict = json.load(f)

        with open("data/protocols.json", "r", encoding="utf-8") as f:
            protocols_json = f.read()

        windows_data = "[]"
        if load_windows:
            with open("data/windows.json", "r", encoding="utf-8") as f:
                windows_data = f.read()

        measurements_data = "[]"
        if load_measurements:
            with open("data/measurements.json", "r", encoding="utf-8") as f:
                measurements_data = f.read()

        i18n_src = Path("assets/js/i18n.js").resolve().as_uri()
        search_src = Path("assets/js/search.js").resolve().as_uri()
        protocol_renderer_src = Path("assets/js/components/protocol-renderer.js").resolve().as_uri()
        router_src = Path("assets/js/router.js").resolve().as_uri()

        css_tag = ""
        if inject_css:
            css_src = Path("assets/css/styles.css").resolve().as_uri()
            css_tag = f'<link rel="stylesheet" href="{css_src}">'

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    __CSS_TAG__
</head>
<body>
    <div id="results">{"success": false, "error": "Harness initialized but payload did not complete"}</div>
    <div id="app" class="app-container"></div>

    <script>
        window.__harnessErrors = [];
        window.__moduleStatus = {
            i18n: false,
            search: false,
            protocolRenderer: false,
            router: false
        };

        window.addEventListener("error", (e) => {
            const errInfo = {
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                stack: e.error ? e.error.stack : null
            };
            window.__harnessErrors.push(errInfo);

            document.getElementById("results").textContent = JSON.stringify({
                success: false,
                error: "Global error: " + e.message,
                filename: e.filename,
                lineno: e.lineno,
                stack: errInfo.stack
            });
        });

        window.addEventListener("unhandledrejection", (e) => {
            const errInfo = {
                message: e.reason ? (e.reason.message || String(e.reason)) : "Unknown rejection",
                stack: e.reason ? e.reason.stack : null
            };
            window.__harnessErrors.push(errInfo);

            document.getElementById("results").textContent = JSON.stringify({
                success: false,
                error: "Unhandled rejection: " + errInfo.message,
                stack: errInfo.stack
            });
        });
    </script>

    <script>
        const _storage = {
            pocus_reader_theme: 'warm',
            pocus_reader_font_size: '18',
            pocus_reader_line_height: 'normal',
            pocus_reader_width: 'medium',
            pocus_reader_distraction_free: 'false',
            language: 'es'
        };
        const _sessionState = {};
        const Storage = {
            getLanguage: () => _storage.language || 'es',
            setLanguage: (lang) => { _storage.language = lang; },
            getProgress: (type, id) => null,
            saveProgress: (type, id, data) => {},
            removeProgress: (type, id) => {},
            getSessionState: (key) =>
                Object.prototype.hasOwnProperty.call(_sessionState, key)
                    ? _sessionState[key]
                    : null,
            setSessionState: (key, value) => {
                _sessionState[key] = value;
            },
            getPreference: (key, fallback = null) => {
                return _storage[key] !== undefined ? _storage[key] : fallback;
            },
            setPreference: (key, value) => {
                _storage[key] = String(value);
            },
            removePreference: (key) => {
                delete _storage[key];
            }
        };

        const MediaViewer = {
            renderMediaSection: (media) => "<div>MOCK_MEDIA</div>",
            getMediaForEntity: (resources, type, id) => [],
            initializeMediaInteractions: (container) => {}
        };

        const DataLoader = {
            getTranslations: async () => ({
                translations: //TRANSLATIONS_DICT//
            }),
            fetchResource: async (res) => {
                if (res === "protocols") {
                    return //PROTOCOLS_JSON//;
                }
                return {};
            },
            getWindows: async () => //WINDOWS_JSON//,
            getMeasurements: async () => //MEASUREMENTS_JSON//,
            getGlossary: async () => [],
            getAbbreviations: async () => [],
            getClassifications: async () => [],
            getMediaResources: async () => []
        };
    </script>

    <script src="__I18N_SRC__"></script>
    <script>window.__moduleStatus.i18n = typeof I18n !== "undefined";</script>
    <script src="__SEARCH_SRC__"></script>
    <script>window.__moduleStatus.search = typeof Search !== "undefined";</script>
    <script src="__PROTOCOL_RENDERER_SRC__"></script>
    <script>window.__moduleStatus.protocolRenderer = typeof ProtocolRenderer !== "undefined";</script>
    <script src="__ROUTER_SRC__"></script>
    <script>window.__moduleStatus.router = typeof Router !== "undefined";</script>

    <script>
        (async () => {
            const resultsEl = document.getElementById("results");

            if (window.__harnessErrors.length > 0) {
                const firstErr = window.__harnessErrors[0];
                resultsEl.textContent = JSON.stringify({
                    success: false,
                    error: "Pre-execution error: " + firstErr.message,
                    stack: firstErr.stack,
                    filename: firstErr.filename,
                    lineno: firstErr.lineno
                });
                return;
            }

            if (!window.__moduleStatus.i18n || !window.__moduleStatus.search || !window.__moduleStatus.protocolRenderer || !window.__moduleStatus.router) {
                resultsEl.textContent = JSON.stringify({
                    success: false,
                    error: "Module failed to load",
                    moduleStatus: window.__moduleStatus,
                    harnessErrors: window.__harnessErrors
                });
                return;
            }

            try {
                await I18n.init();
                const res = await (async () => {
                    //JS_PAYLOAD//
                })();
                resultsEl.textContent = JSON.stringify({ success: true, data: res });
            } catch (e) {
                resultsEl.textContent = JSON.stringify({
                    success: false,
                    error: e.message || String(e),
                    stack: e.stack || null
                });
            }
        })();
    </script>
</body>
</html>
"""

        html_content = html_content.replace("__CSS_TAG__", css_tag)
        html_content = html_content.replace("//TRANSLATIONS_DICT//", json.dumps(translations_dict["translations"]))
        html_content = html_content.replace("//PROTOCOLS_JSON//", protocols_json)
        html_content = html_content.replace("//WINDOWS_JSON//", windows_data)
        html_content = html_content.replace("//MEASUREMENTS_JSON//", measurements_data)
        html_content = html_content.replace("__I18N_SRC__", i18n_src)
        html_content = html_content.replace("__SEARCH_SRC__", search_src)
        html_content = html_content.replace("__PROTOCOL_RENDERER_SRC__", protocol_renderer_src)
        html_content = html_content.replace("__ROUTER_SRC__", router_src)
        html_content = html_content.replace("//JS_PAYLOAD//", js_payload)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8", dir="./") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    with tempfile.TemporaryDirectory(dir="./") as user_data_dir:
        try:
            cmd = [
                chrome_path,
                "--headless",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--no-sandbox",
                "--incognito",
                "--allow-file-access-from-files",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-background-networking",
                "--disable-component-update",
                "--password-store=basic",
                "--use-mock-keychain",
                f"--user-data-dir={os.path.abspath(user_data_dir)}",
                "--dump-dom",
                "file://" + urllib.request.pathname2url(os.path.abspath(tmp_path))
            ]
            if harness_type == "app" and virtual_time_budget > 0:
                cmd.append(f"--virtual-time-budget={virtual_time_budget}")

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                stdin=subprocess.DEVNULL
            )

            if res.returncode != 0:
                raise subprocess.SubprocessError(
                    f"Chrome execution failed with returncode {res.returncode}.\n"
                    f"STDOUT:\n{res.stdout}\n"
                    f"STDERR:\n{res.stderr}"
                )

            match = re.search(r'<div id="results">(.*?)</div>', res.stdout)
            if match:
                content = match.group(1).strip()
                if not content:
                    raise ValueError(f"El contenedor de resultados quedó vacío.\nSTDERR:\n{res.stderr}")
                parsed = json.loads(content)
                if not parsed.get("success", False):
                    err_msg = (
                        f"JavaScript error during test execution:\n"
                        f"Error: {parsed.get('error')}\n"
                        f"Stack: {parsed.get('stack')}\n"
                    )
                    if parsed.get("filename"):
                        err_msg += f"File: {parsed.get('filename')}:{parsed.get('lineno')}\n"
                    if parsed.get("moduleStatus"):
                        err_msg += f"Module Status: {parsed.get('moduleStatus')}\n"
                    if parsed.get("harnessErrors"):
                        err_msg += f"Harness Errors: {parsed.get('harnessErrors')}\n"
                    err_msg += f"STDERR:\n{res.stderr}"
                    raise RuntimeError(err_msg)
                return parsed
            else:
                raise ValueError(f"No results div found in stdout.\nSTDOUT:\n{res.stdout}")
        except subprocess.TimeoutExpired as e:
            out_decoded = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else str(e.stdout)
            err_decoded = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
            raise TimeoutError(
                f"Chrome headless excedió el tiempo máximo de {timeout} segundos.\n"
                f"STDOUT parcial:\n{out_decoded}\n"
                f"STDERR parcial:\n{err_decoded}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
