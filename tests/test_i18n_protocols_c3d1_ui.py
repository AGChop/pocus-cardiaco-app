import os
import json
import re
import tempfile
import subprocess
import urllib.request
import pytest
from pathlib import Path

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def run_js_in_chrome(js_payload):
    # Read translations dictionary
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations_dict = json.load(f)

    # Read clinical catalogs
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols_json = f.read()
    with open("data/windows.json", "r", encoding="utf-8") as f:
        windows_json = f.read()
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements_json = f.read()

    # Generate absolute file:// URLs for the modules
    i18n_src = Path("assets/js/i18n.js").resolve().as_uri()
    search_src = Path("assets/js/search.js").resolve().as_uri()
    router_src = Path("assets/js/router.js").resolve().as_uri()

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <div id="results">{"success": false, "error": "Harness initialized but payload did not complete"}</div>
    <div id="app"></div>

    <!-- 1. Initialization and error catching -->
    <script>
        window.__harnessErrors = [];
        window.__moduleStatus = {
            i18n: false,
            search: false,
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

    <!-- 2. Mocks -->
    <script>
        const _storage = { language: 'es' };
        const _sessionState = {};
        const Storage = {
            getLanguage: () => _storage.language,
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

    <!-- 3. i18n -->
    <script src="__I18N_SRC__"></script>
    <script>
        window.__moduleStatus.i18n = typeof I18n !== "undefined";
    </script>

    <!-- 4. search -->
    <script src="__SEARCH_SRC__"></script>
    <script>
        window.__moduleStatus.search = typeof Search !== "undefined";
    </script>

    <!-- 5. router -->
    <script src="__ROUTER_SRC__"></script>
    <script>
        window.__moduleStatus.router = typeof Router !== "undefined";
    </script>

    <!-- 6. Payload Runner -->
    <script>
        (async () => {
            const resultsEl = document.getElementById("results");

            // 6a. Si hay errores previos acumulados, no sobrescribir y abortar
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

            // 6b. Si algún módulo no se cargó correctamente
            if (!window.__moduleStatus.i18n || !window.__moduleStatus.search || !window.__moduleStatus.router) {
                resultsEl.textContent = JSON.stringify({
                    success: false,
                    error: "Module failed to load",
                    moduleStatus: window.__moduleStatus,
                    harnessErrors: window.__harnessErrors
                });
                return;
            }

            // 6c. Ejecutar el payload de forma segura
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

    html_content = html_content.replace("//TRANSLATIONS_DICT//", json.dumps(translations_dict["translations"]))
    html_content = html_content.replace("//PROTOCOLS_JSON//", protocols_json)
    html_content = html_content.replace("//WINDOWS_JSON//", windows_json)
    html_content = html_content.replace("//MEASUREMENTS_JSON//", measurements_json)
    html_content = html_content.replace("__I18N_SRC__", i18n_src)
    html_content = html_content.replace("__SEARCH_SRC__", search_src)
    html_content = html_content.replace("__ROUTER_SRC__", router_src)
    html_content = html_content.replace("//JS_PAYLOAD//", js_payload)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8", dir="./") as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    with tempfile.TemporaryDirectory(dir="./") as user_data_dir:
        try:
            cmd = [
                CHROME_PATH,
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
                "--virtual-time-budget=3000",
                f"--user-data-dir={os.path.abspath(user_data_dir)}",
                "--dump-dom",
                "file://" + urllib.request.pathname2url(os.path.abspath(tmp_path))
            ]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                stdin=subprocess.DEVNULL
            )

            if res.returncode != 0:
                pytest.fail(f"Chrome failed execution with code {res.returncode}.\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")

            match = re.search(r'<div id="results">(.*?)</div>', res.stdout)
            if match:
                content = match.group(1).strip()
                if not content:
                    pytest.fail(f"El contenedor de resultados quedó vacío.\nSTDERR:\n{res.stderr}")
                try:
                    parsed = json.loads(content)
                except json.JSONDecodeError:
                    pytest.fail(
                        f"El contenido del div de resultados no es un JSON válido.\n"
                        f"Contenido exacto:\n{content}\n"
                        f"STDERR:\n{res.stderr}"
                    )
                if not parsed.get("success", False):
                    pytest.fail(
                        f"JavaScript error during test execution:\n"
                        f"Error: {parsed.get('error')}\n"
                        f"Stack: {parsed.get('stack')}\n"
                        f"File: {parsed.get('filename')}:{parsed.get('lineno')}\n"
                        f"Module Status: {parsed.get('moduleStatus')}\n"
                        f"Harness Errors: {parsed.get('harnessErrors')}\n"
                        f"STDERR:\n{res.stderr}"
                    )
                return parsed
            else:
                pytest.fail(f"No results div found in stdout.\nSTDOUT:\n{res.stdout}")
        except subprocess.TimeoutExpired as e:
            out_decoded = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else str(e.stdout)
            err_decoded = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
            pytest.fail(f"Chrome timed out.\nSTDOUT:\n{out_decoded}\nSTDERR:\n{err_decoded}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

def test_translation_keys_structure():
    with open("data/translations.json", "r", encoding="utf-8") as f:
        t = json.load(f)["translations"]

    expected_keys = {
        "label.protocol_sections": {"es": "Secciones del protocolo", "en": "Protocol sections"},
        "label.go_to_step": {"es": "Ir al paso {step}: {title}", "en": "Go to step {step}: {title}"},
        "label.clinical_context": {"es": "Contexto clínico", "en": "Clinical context"},
        "label.target_population": {"es": "Población objetivo", "en": "Target population"},
        "label.acquisition_sequence": {"es": "Secuencia de adquisición", "en": "Acquisition sequence"},
        "label.component_with_name": {"es": "Componente: {name}", "en": "Component: {name}"},
        "label.reminder": {"es": "Recordatorio", "en": "Reminder"},
        "label.reminder_text": {
            "es": "Siempre integre los hallazgos con el contexto clínico del paciente.",
            "en": "Always integrate findings with the patient's clinical context."
        },
        "label.purpose_and_context": {"es": "Propósito y contexto", "en": "Purpose and context"}
    }

    for key, expected_val in expected_keys.items():
        assert key in t, f"Missing key: {key}"
        assert t[key]["es"] == expected_val["es"], f"Mismatch ES for {key}"
        assert t[key]["en"] == expected_val["en"], f"Mismatch EN for {key}"

def test_router_static_analysis():
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    banned_substrings = [
        "Secciones del protocolo",
        "Ir al paso",
        "Contexto clínico",
        "Población objetivo",
        "Secuencia de adquisición",
        "Componente:",
        "Recordatorio:",
        "Propósito y contexto",
        "isEn ? 'Component:'",
        "isEn ? 'Clinical context:'",
        "isEn ? 'Target population:'",
        "isEn ? 'Acquisition sequence:'"
    ]

    clean_content = re.sub(r"//.*", "", content)
    clean_content = re.sub(r"/\*.*?\*/", "", clean_content, flags=re.DOTALL)

    for term in banned_substrings:
        assert term not in clean_content, f"Banned string or ternary still found in router.js: {term}"

def test_d1a_unmodified():
    assert os.path.exists("data/protocols.json")
    assert os.path.exists("data/protocols.i18n.json")
    assert os.path.exists("data/protocols.draft.json")
    assert os.path.exists("scripts/promote_protocols.py")
    assert os.path.exists("tests/test_protocols_runtime.py")
    assert os.path.exists("tests/test_i18n_protocols_c3d1_data.py")

def test_ui_localization_and_elements_headless():
    payload = """
    const container = document.getElementById("app");

    // Resolve dynamic values from actual catalogs
    const windows = await DataLoader.getWindows();
    const plaxObj = windows.find(w => w.id === "plax");

    const measurements = await DataLoader.getMeasurements();
    const feviObj = measurements.find(m => m.id === "fevi");

    // Test 1: Render in Spanish
    I18n.setLanguage("es");
    await Router.renderProtocolDetail(container, "rush");
    const htmlES = container.innerHTML;

    // Check resolveWindowLink and resolveMeasurementLink in ES
    const plaxNameES = I18n.localize(plaxObj.window, "es");
    const feviNameES = I18n.localize(feviObj.measurement, "es");
    const plaxAbbreviationES = I18n.localize(plaxObj.abbreviation, "es");
    const feviAbbreviationES = I18n.localize(feviObj.abbreviation, "es");

    const hasWindowES = htmlES.includes(plaxNameES) && htmlES.includes(plaxAbbreviationES);
    const hasMeasurementES = htmlES.includes(feviNameES) && htmlES.includes(feviAbbreviationES);

    // Check labels in ES
    const hasClinicalContextLabelES = htmlES.includes("Contexto clínico");
    const hasAriaLabelES = htmlES.includes("Secciones del protocolo");
    const hasReminderES = htmlES.includes("Siempre integre los hallazgos con el contexto clínico del paciente.");

    // Check no [object Object], undefined, null
    const noObjectObjES = !htmlES.includes("[object Object]");
    const noUndefinedES = !htmlES.includes("undefined") && !htmlES.includes("null");

    // Test 2: Switch to English
    I18n.setLanguage("en");
    await Router.renderProtocolDetail(container, "rush");
    const htmlEN = container.innerHTML;

    // Check resolveWindowLink and resolveMeasurementLink in EN
    const plaxNameEN = I18n.localize(plaxObj.window, "en");
    const feviNameEN = I18n.localize(feviObj.measurement, "en");
    const plaxAbbreviationEN = I18n.localize(plaxObj.abbreviation, "en");
    const feviAbbreviationEN = I18n.localize(feviObj.abbreviation, "en");

    const hasWindowEN = htmlEN.includes(plaxNameEN) && htmlEN.includes(plaxAbbreviationEN);
    const hasMeasurementEN = htmlEN.includes(feviNameEN) && htmlEN.includes(feviAbbreviationEN);

    // Check labels in EN
    const hasClinicalContextLabelEN = htmlEN.includes("Clinical context");
    const hasAriaLabelEN = htmlEN.includes("Protocol sections");
    const hasReminderEN = htmlEN.includes("Always integrate findings with the patient's clinical context.");

    // Check component names (Pump / La Bomba)
    const hasPumpES = htmlES.includes("La Bomba (Evaluación cardíaca)");
    const hasPumpEN = htmlEN.includes("The Pump (Cardiac Evaluation)");

    const noObjectObjEN = !htmlEN.includes("[object Object]");
    const noUndefinedEN = !htmlEN.includes("undefined") && !htmlEN.includes("null");

    // Test 3: Switch back to Spanish (es -> en -> es sequence verification)
    I18n.setLanguage("es");
    await Router.renderProtocolDetail(container, "rush");
    const htmlESAfter = container.innerHTML;
    const hasPumpESAfter = htmlESAfter.includes("La Bomba (Evaluación cardíaca)");
    const noObjectObjESAfter = !htmlESAfter.includes("[object Object]");

    return {
        hasWindowES, hasMeasurementES, hasClinicalContextLabelES, hasAriaLabelES, hasReminderES, noObjectObjES, noUndefinedES,
        hasWindowEN, hasMeasurementEN, hasClinicalContextLabelEN, hasAriaLabelEN, hasReminderEN, hasPumpES, hasPumpEN, noObjectObjEN, noUndefinedEN,
        hasPumpESAfter, noObjectObjESAfter
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]

    assert data["hasWindowES"], "Window link was not resolved or localized in Spanish"
    assert data["hasMeasurementES"], "Measurement link was not resolved or localized in Spanish"
    assert data["hasClinicalContextLabelES"], "Clinical context label was not found in Spanish"
    assert data["hasAriaLabelES"], "ARIA label was not found or translated to Spanish"
    assert data["hasReminderES"], "Reminder text was not found or translated to Spanish"
    assert data["noObjectObjES"], "HTML in Spanish contains '[object Object]'"
    assert data["noUndefinedES"], "HTML in Spanish contains undefined or null"

    assert data["hasWindowEN"], "Window link was not resolved or localized in English"
    assert data["hasMeasurementEN"], "Measurement link was not resolved or localized in English"
    assert data["hasClinicalContextLabelEN"], "Clinical context label was not found in English"
    assert data["hasAriaLabelEN"], "ARIA label was not found or translated to English"
    assert data["hasReminderEN"], "Reminder text was not found or translated to English"
    assert data["hasPumpES"], "La Bomba not found in Spanish"
    assert data["hasPumpEN"], "The Pump not found in English"
    assert data["noObjectObjEN"], "HTML in English contains '[object Object]'"
    assert data["noUndefinedEN"], "HTML in English contains undefined or null"

    assert data["hasPumpESAfter"], "Interactive guide failed to update back to Spanish name 'La Bomba'"
    assert data["noObjectObjESAfter"], "HTML after switching back to Spanish contains '[object Object]'"

def test_search_localization_and_indexing_headless():
    payload = """
    // Spanish search
    I18n.setLanguage("es");
    const resultsES = await Search.searchGlobal("La Bomba");
    const resultsDeepES = await Search.searchGlobal("tuberías");

    // English search
    I18n.setLanguage("en");
    const resultsEN = await Search.searchGlobal("The Pump");
    const resultsDeepEN = await Search.searchGlobal("Pipes");

    // Check result items content
    const matchPumpES = resultsES.some(r => r.item.id === "rush");
    const matchPumpEN = resultsEN.some(r => r.item.id === "rush");
    const matchDeepES = resultsDeepES.some(r => r.item.id === "rush");
    const matchDeepEN = resultsDeepEN.some(r => r.item.id === "rush");

    // Localize result items
    I18n.setLanguage("es");
    const nameES = I18n.localize({ es: resultsES[0].item.name_es, en: resultsES[0].item.name_en });

    I18n.setLanguage("en");
    const nameEN = I18n.localize({ es: resultsEN[0].item.name_es, en: resultsEN[0].item.name_en });

    return {
        matchPumpES,
        matchPumpEN,
        matchDeepES,
        matchDeepEN,
        nameES,
        nameEN
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]
    assert data["matchPumpES"], "Search failed to match 'La Bomba' in Spanish"
    assert data["matchPumpEN"], "Search failed to match 'The Pump' in English"
    assert data["matchDeepES"], "Search failed to match deep clinical content 'tuberías' in Spanish"
    assert data["matchDeepEN"], "Search failed to match deep clinical content 'Pipes' in English"
    assert "RUSH" in data["nameES"], "Result name in Spanish is not matching RUSH"
    assert "RUSH" in data["nameEN"], "Result name in English is not matching RUSH"

def test_bilingual_assets_and_cache_revision():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v17-c3d1" in content
    assert "./assets/js/i18n.js" in content
    assert "./data/translations.json" in content
    assert "./assets/js/router.js" in content
    assert "./assets/js/search.js" in content
    assert "./data/protocols.json" in content
