import os
import json
import re
import base64
import tempfile
import subprocess
import urllib.request
import pytest
from pathlib import Path

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def run_js_in_chrome(js_payload):
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations_dict = json.load(f)

    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols_json = f.read()

    css_src = Path("assets/css/styles.css").resolve().as_uri()
    i18n_src = Path("assets/js/i18n.js").resolve().as_uri()
    search_src = Path("assets/js/search.js").resolve().as_uri()
    router_src = Path("assets/js/router.js").resolve().as_uri()

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="__CSS_SRC__">
</head>
<body>
    <div id="results">{"success": false, "error": "Harness initialized but payload did not complete"}</div>
    <div id="app" class="app-container"></div>

    <script>
        window.__harnessErrors = [];
        window.__moduleStatus = {
            i18n: false,
            search: false,
            router: false
        };

        window.addEventListener("error", (e) => {
            window.__harnessErrors.push({
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                stack: e.error ? e.error.stack : null
            });
            document.getElementById("results").textContent = JSON.stringify({
                success: false,
                error: "Global error: " + e.message,
                filename: e.filename,
                lineno: e.lineno
            });
        });
    </script>

    <script>
        const _storage = {
            pocus_reader_theme: 'warm',
            pocus_reader_font_size: '18',
            pocus_reader_line_height: 'normal',
            pocus_reader_width: 'medium',
            pocus_reader_distraction_free: 'false'
        };
        const _sessionState = {};
        const Storage = {
            getLanguage: () => 'es',
            setLanguage: (lang) => {},
            getProgress: (type, id) => null,
            saveProgress: (type, id, data) => {},
            removeProgress: (type, id) => {},
            getSessionState: (key) => _sessionState[key] || null,
            setSessionState: (key, value) => { _sessionState[key] = value; },
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
            getWindows: async () => [],
            getMeasurements: async () => [],
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
                    stack: firstErr.stack
                });
                return;
            }

            if (!window.__moduleStatus.i18n || !window.__moduleStatus.search || !window.__moduleStatus.router) {
                resultsEl.textContent = JSON.stringify({
                    success: false,
                    error: "Module failed to load",
                    moduleStatus: window.__moduleStatus
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

    html_content = html_content.replace("//TRANSLATIONS_DICT//", json.dumps(translations_dict["translations"]))
    html_content = html_content.replace("//PROTOCOLS_JSON//", protocols_json)
    html_content = html_content.replace("__CSS_SRC__", css_src)
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
                timeout=45,
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
                    pytest.fail(f"El contenido del div de resultados no es un JSON válido.\nContenido:\n{content}")
                if not parsed.get("success", False):
                    pytest.fail(f"JS Error: {parsed.get('error')}\nStack: {parsed.get('stack')}")
                return parsed
            else:
                pytest.fail(f"No results div found.\nSTDOUT:\n{res.stdout}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def test_reader_translations_integrity():
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", {})
    keys = [
        "label.reader_mode", "label.reader_exit", "label.reader_controls", "label.reader_theme",
        "label.reader_theme_warm", "label.reader_theme_sepia", "label.reader_theme_white",
        "label.reader_theme_night", "label.reader_font_decrease", "label.reader_font_increase",
        "label.reader_line_height", "label.reader_line_compact", "label.reader_line_normal",
        "label.reader_line_relaxed", "label.reader_width", "label.reader_width_narrow",
        "label.reader_width_medium", "label.reader_width_wide", "label.reader_distraction_free",
        "label.reader_progress", "label.reader_reset"
    ]

    for k in keys:
        assert k in translations, f"Translation key {k} missing"
        assert "es" in translations[k]
        assert "en" in translations[k]
        assert len(translations[k]["es"].strip()) > 0
        assert len(translations[k]["en"].strip()) > 0


def test_reader_css_integrity():
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert "/* --- PROTOCOL READER MODE (READER1) --- */" in css
    assert "data-reader-theme=\"warm\"" in css
    assert "data-reader-theme=\"sepia\"" in css
    assert "data-reader-theme=\"white\"" in css
    assert "data-reader-theme=\"night\"" in css
    assert "data-reader-width=\"narrow\"" in css
    assert "data-reader-width=\"medium\"" in css
    assert "data-reader-width=\"wide\"" in css
    assert "data-reader-line-height=\"compact\"" in css
    assert "data-reader-line-height=\"normal\"" in css
    assert "data-reader-line-height=\"relaxed\"" in css
    assert "Georgia" in css or "Times New Roman" in css
    assert "overflow-x: auto" not in css
    assert "overflow-x: scroll" not in css
    assert "line-clamp" not in css
    assert "text-overflow: ellipsis" not in css
    assert "background-image" in css


def test_reader_js_logic_real_headless():
    payload = """
        const app = document.getElementById("app");
        await Router.renderProtocolDetail(app, "rush");

        const openBtn = document.getElementById("protocol-reader-open");
        const launchContainer = document.querySelector(".protocol-reader-launch");
        const fullPanel = document.getElementById("protocol-full-panel");
        const controls = document.getElementById("protocol-reader-controls");
        const progress = fullPanel.querySelector(".protocol-reader-progress");
        const page = document.getElementById("protocol-reader-page");
        const grid = page.querySelector(".content-accordion-grid");

        // Verify elements existence
        if (!openBtn || !fullPanel || !controls || !progress || !page) {
            throw new Error("Reader elements missing from DOM");
        }

        // Verify initialize method
        if (typeof Router.initializeProtocolReader !== "function") {
            throw new Error("Router.initializeProtocolReader is not a function");
        }

        // Initial state validation
        const isActiveInitially = fullPanel.classList.contains("reader-active");
        const isControlsHidden = controls.hasAttribute("hidden");
        const isProgressHidden = progress.hasAttribute("hidden");

        // Visual checks initially (inactive state)
        const computedControlsInit = window.getComputedStyle(controls);
        const computedProgressInit = window.getComputedStyle(progress);
        const computedLaunchInit = window.getComputedStyle(launchContainer);
        const computedPageInit = window.getComputedStyle(page);
        const computedGridInit = grid ? window.getComputedStyle(grid) : null;

        const isControlsVisibleInit = computedControlsInit.display !== "none";
        const isProgressVisibleInit = computedProgressInit.display !== "none";
        const isLaunchVisibleInit = computedLaunchInit.display !== "none";
        const pageBgInit = computedPageInit.backgroundColor;
        const pageFontInit = computedPageInit.fontFamily;
        const gridDisplayInit = computedGridInit ? computedGridInit.display : "";

        // Open Reader Mode
        openBtn.click();

        const isActiveActive = fullPanel.classList.contains("reader-active");
        const isLayoutActive = document.querySelector(".app-container").classList.contains("reader-layout-active");
        const isControlsShown = !controls.hasAttribute("hidden");
        const isProgressShown = !progress.hasAttribute("hidden");
        const openPressed = openBtn.getAttribute("aria-pressed") === "true";

        // Visual checks when active
        const computedControlsActive = window.getComputedStyle(controls);
        const computedProgressActive = window.getComputedStyle(progress);
        const computedLaunchActive = window.getComputedStyle(launchContainer);
        const computedPageActive = window.getComputedStyle(page);
        const computedGridActive = grid ? window.getComputedStyle(grid) : null;

        const isControlsVisibleActive = computedControlsActive.display === "flex";
        const isProgressVisibleActive = computedProgressActive.display === "flex";
        const isLaunchVisibleActive = computedLaunchActive.display !== "none";
        const pageBgActive = computedPageActive.backgroundColor;
        const pageFontActive = computedPageActive.fontFamily;
        const gridDisplayActive = computedGridActive ? computedGridActive.display : "";

        // Accordion checks (should all be open)
        const accordions = Array.from(page.querySelectorAll("details.content-accordion"));
        const allOpen = accordions.every(acc => acc.open);

        // Click summary to see if toggle is blocked
        const firstSummary = accordions[0].querySelector("summary");
        if (firstSummary) {
            firstSummary.click();
        }
        const stillOpenAfterClick = accordions[0].open;

        // Verify theme buttons pressed state
        const themeWarmBtn = controls.querySelector(".theme-btn-warm");
        const themeNightBtn = controls.querySelector(".theme-btn-night");
        const initiallyWarmPressed = themeWarmBtn.getAttribute("aria-pressed") === "true";

        // Click night theme
        themeNightBtn.click();
        const nightPressed = themeNightBtn.getAttribute("aria-pressed") === "true";
        const pageNightTheme = page.getAttribute("data-reader-theme") === "night";

        // Font decrease and increase checks
        const fontDecBtn = document.getElementById("protocol-reader-font-dec");
        const fontIncBtn = document.getElementById("protocol-reader-font-inc");

        // Initial default size: 18px
        fontDecBtn.click(); // -> 16px
        const size16 = page.style.getPropertyValue("--reader-font-size");
        const decDisabled = fontDecBtn.disabled || fontDecBtn.getAttribute("aria-disabled") === "true";

        fontIncBtn.click(); // -> 18px
        fontIncBtn.click(); // -> 20px
        fontIncBtn.click(); // -> 22px
        fontIncBtn.click(); // -> 24px
        const size24 = page.style.getPropertyValue("--reader-font-size");
        const incDisabled = fontIncBtn.disabled || fontIncBtn.getAttribute("aria-disabled") === "true";

        // Reset check
        const resetBtn = document.getElementById("protocol-reader-reset-btn");
        resetBtn.click();
        const themeAfterReset = page.getAttribute("data-reader-theme") === "warm";
        const sizeAfterReset = page.style.getPropertyValue("--reader-font-size") === "18px";
        const lineAfterReset = page.getAttribute("data-reader-line-height") === "normal";
        const widthAfterReset = page.getAttribute("data-reader-width") === "medium";

        // Exit Reader Mode
        const closeBtn = document.getElementById("protocol-reader-close");
        closeBtn.click();

        const isActiveAfterExit = fullPanel.classList.contains("reader-active");
        const isLayoutActiveAfterExit = document.querySelector(".app-container").classList.contains("reader-layout-active");

        // Visual checks after exit
        const computedControlsExit = window.getComputedStyle(controls);
        const computedProgressExit = window.getComputedStyle(progress);
        const computedLaunchExit = window.getComputedStyle(launchContainer);
        const computedPageExit = window.getComputedStyle(page);
        const computedGridExit = grid ? window.getComputedStyle(grid) : null;

        const isControlsVisibleExit = computedControlsExit.display !== "none";
        const isProgressVisibleExit = computedProgressExit.display !== "none";
        const isLaunchVisibleExit = computedLaunchExit.display !== "none";
        const pageBgExit = computedPageExit.backgroundColor;
        const pageFontExit = computedPageExit.fontFamily;
        const gridDisplayExit = computedGridExit ? computedGridExit.display : "";

        return {
            isActiveInitially,
            isControlsHidden,
            isProgressHidden,
            isControlsVisibleInit,
            isProgressVisibleInit,
            isLaunchVisibleInit,
            pageBgInit,
            pageFontInit,
            gridDisplayInit,
            isActiveActive,
            isLayoutActive,
            isControlsShown,
            isProgressShown,
            isControlsVisibleActive,
            isProgressVisibleActive,
            isLaunchVisibleActive,
            pageBgActive,
            pageFontActive,
            gridDisplayActive,
            openPressed,
            allOpen,
            stillOpenAfterClick,
            initiallyWarmPressed,
            nightPressed,
            pageNightTheme,
            size16,
            decDisabled,
            size24,
            incDisabled,
            themeAfterReset,
            sizeAfterReset,
            lineAfterReset,
            widthAfterReset,
            isActiveAfterExit,
            isLayoutActiveAfterExit,
            isControlsVisibleExit,
            isProgressVisibleExit,
            isLaunchVisibleExit,
            pageBgExit,
            pageFontExit,
            gridDisplayExit
        };
    """

    res = run_js_in_chrome(payload)
    data = res["data"]

    assert not data["isActiveInitially"]
    assert data["isControlsHidden"]
    assert data["isProgressHidden"]
    
    # 3. Controles no son visibles inicialmente.
    assert not data["isControlsVisibleInit"], "Los controles no deben ser visibles inicialmente"
    # 4. Progreso no es visible inicialmente.
    assert not data["isProgressVisibleInit"], "El progreso no debe ser visible inicialmente"
    # 5. Solo se ve el botón Modo lectura inicialmente.
    assert data["isLaunchVisibleInit"], "El botón de Modo lectura debe ser visible inicialmente"
    
    # 7. Sin reader-active, la página no usa fondo de papel.
    assert "250, 246, 238" not in data["pageBgInit"], "Sin reader-active no debe aplicarse fondo de papel warm"
    # 8. Sin reader-active, conserva fuente normal.
    assert "Georgia" not in data["pageFontInit"], "Sin reader-active no debe aplicarse fuente Georgia"
    # 9. Sin reader-active, conserva cuadrícula normal de dos columnas
    assert data["gridDisplayInit"] == "grid", "Sin reader-active debe conservar grid normal"

    # 10. Al pulsar Modo lectura:
    assert data["isActiveActive"]
    assert data["isLayoutActive"]
    assert data["isControlsShown"]
    assert data["isProgressShown"]
    assert data["isControlsVisibleActive"], "Controles deben ser visibles cuando activo"
    assert data["isProgressVisibleActive"], "Progreso debe ser visible cuando activo"
    assert not data["isLaunchVisibleActive"], "Launch debe estar oculto cuando activo"
    assert "250, 246, 238" in data["pageBgActive"], "Papel aplicado cuando activo"
    assert "Georgia" in data["pageFontActive"], "Una sola columna y fuente aplicada cuando activo"
    assert data["gridDisplayActive"] == "flex", "Grid display debe ser flex (una sola columna) cuando activo"
    
    assert data["openPressed"]
    assert data["allOpen"]
    assert data["stillOpenAfterClick"]
    assert data["initiallyWarmPressed"]
    assert data["nightPressed"]
    assert data["pageNightTheme"]
    assert data["size16"] == "16px"
    assert data["decDisabled"]
    assert data["size24"] == "24px"
    assert data["incDisabled"]
    assert data["themeAfterReset"]
    assert data["sizeAfterReset"]
    assert data["lineAfterReset"]
    assert data["widthAfterReset"]
    
    # 11. Al salir:
    assert not data["isActiveAfterExit"]
    assert not data["isLayoutActiveAfterExit"]
    assert not data["isControlsVisibleExit"], "Controles ocultos al salir"
    assert not data["isProgressVisibleExit"], "Progreso oculto al salir"
    assert data["isLaunchVisibleExit"], "Launch visible al salir"
    assert "250, 246, 238" not in data["pageBgExit"], "Papel no aplicado al salir"
    assert "Georgia" not in data["pageFontExit"], "Fuente normal restaurada al salir"
    assert data["gridDisplayExit"] == "grid", "Grid normal restaurado al salir"


def test_reader_escape_key_real_headless():
    payload = """
        const app = document.getElementById("app");
        await Router.renderProtocolDetail(app, "rush");

        const openBtn = document.getElementById("protocol-reader-open");
        const fullPanel = document.getElementById("protocol-full-panel");

        openBtn.click();
        const activeBeforeEsc = fullPanel.classList.contains("reader-active");

        // Dispatch Escape keydown event
        const escEvent = new KeyboardEvent("keydown", { key: "Escape", bubbles: true });
        window.dispatchEvent(escEvent);

        const activeAfterEsc = fullPanel.classList.contains("reader-active");

        return {
            activeBeforeEsc,
            activeAfterEsc
        };
    """

    res = run_js_in_chrome(payload)
    data = res["data"]
    assert data["activeBeforeEsc"]
    assert not data["activeAfterEsc"]


def test_reader_distraction_free_real_headless():
    payload = """
        const app = document.getElementById("app");
        await Router.renderProtocolDetail(app, "rush");

        const openBtn = document.getElementById("protocol-reader-open");
        const distractionToggle = document.getElementById("protocol-reader-distraction-toggle");
        const appContainer = document.querySelector(".app-container");

        openBtn.click();
        distractionToggle.click();

        const isDistractionFreeActive = appContainer.classList.contains("reader-distraction-free");

        // Exit reader
        const closeBtn = document.getElementById("protocol-reader-close");
        closeBtn.click();

        const isDistractionFreeCleaned = !appContainer.classList.contains("reader-distraction-free");

        return {
            isDistractionFreeActive,
            isDistractionFreeCleaned
        };
    """

    res = run_js_in_chrome(payload)
    data = res["data"]
    assert data["isDistractionFreeActive"]
    assert data["isDistractionFreeCleaned"]


def test_reader_unmodified_files():
    # Verify protocols.json is intact
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        proto_data = json.load(f)
    assert len(proto_data["protocols"]) == 1
    assert proto_data["protocols"][0]["id"] == "rush"

    # Verify measurements.json is intact
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        meas_data = json.load(f)
    assert len(meas_data) == 101


def test_reader_cleanup_and_details_real_headless():
    payload = """
        const app = document.getElementById("app");
        await Router.renderProtocolDetail(app, "rush");

        const progressHtml = document.getElementById("protocol-full-panel").innerHTML;
        const hasInlineStyle = progressHtml.includes('style="width: 0%"') || progressHtml.includes('style="width:0%"') || progressHtml.includes('style="width: 0%;"');

        // Check CSS contains width: 0; inside .protocol-reader-progress-bar
        const stylesText = await (await fetch("assets/css/styles.css")).text();
        const progressBarSelectorMatch = stylesText.includes(".protocol-reader-progress-bar") && stylesText.includes("width: 0;");

        // Record initial accordion states
        const accordions = Array.from(document.querySelectorAll("details.content-accordion"));
        const initialOpenStates = accordions.map(acc => acc.open);

        // Open reader mode
        const openBtn = document.getElementById("protocol-reader-open");
        openBtn.click();

        // Active classes check
        const hasReaderActive = document.getElementById("protocol-full-panel").classList.contains("reader-active");
        const hasLayoutActive = app.classList.contains("reader-layout-active");

        // Turn on distraction free
        const distractionToggle = document.getElementById("protocol-reader-distraction-toggle");
        distractionToggle.click();
        const hasDistractionFree = app.classList.contains("reader-distraction-free");

        // Spy on Router._readerCleanup sequence and execution
        let cleanupExecuted = false;
        const originalCleanup = Router._readerCleanup;

        Router._readerCleanup = () => {
            cleanupExecuted = true;
            originalCleanup();
        };

        const originalAddEventListener = window.addEventListener;
        let addListenerOrderCorrect = true;
        window.addEventListener = function(type, listener, options) {
            if (["keydown", "scroll", "resize"].includes(type)) {
                if (!cleanupExecuted) {
                    addListenerOrderCorrect = false;
                }
            }
            return originalAddEventListener.apply(this, arguments);
        };

        // Call initialize again to trigger the flow and verify Router._readerCleanup runs BEFORE new listeners are registered
        Router.initializeProtocolReader("rush");

        // Restore addEventListener
        window.addEventListener = originalAddEventListener;

        // Verify cleanup removed active classes and restored state
        Router._readerCleanup();

        const cleanedReaderActive = document.getElementById("protocol-full-panel").classList.contains("reader-active");
        const cleanedLayoutActive = app.classList.contains("reader-layout-active");
        const cleanedDistractionFree = app.classList.contains("reader-distraction-free");

        const restoredOpenStates = accordions.map(acc => acc.open);
        const accordionsRestored = initialOpenStates.every((state, i) => state === restoredOpenStates[i]);

        // Test if cleanup does not attempt to focus when not needed (e.g. during route changes)
        let focusCalled = false;
        const origFocus = openBtn.focus;
        openBtn.focus = () => {
            focusCalled = true;
        };
        
        Router._readerCleanup();
        openBtn.focus = origFocus;

        // Clean up any pre-existing listeners first
        if (Router._readerCleanup) {
            Router._readerCleanup();
            Router._readerCleanup = null;
        }

        // Test duplicate listeners: count add/remove events to make sure net added is zero after final cleanup
        let adds = 0;
        let removes = 0;
        const origAdd = window.addEventListener;
        const origRemove = window.removeEventListener;
        
        window.addEventListener = function(type, listener, options) {
            if (["keydown", "scroll", "resize"].includes(type)) {
                adds++;
            }
            return origAdd.apply(this, arguments);
        };
        
        window.removeEventListener = function(type, listener, options) {
            if (["keydown", "scroll", "resize"].includes(type)) {
                removes++;
            }
            return origRemove.apply(this, arguments);
        };
        
        Router.initializeProtocolReader("rush");
        Router.initializeProtocolReader("rush");
        Router._readerCleanup();
        
        window.addEventListener = origAdd;
        window.removeEventListener = origRemove;
        const netListenersCount = adds - removes;

        return {
            hasInlineStyle,
            progressBarSelectorMatch,
            hasReaderActive,
            hasLayoutActive,
            hasDistractionFree,
            cleanupExecuted,
            addListenerOrderCorrect,
            cleanedReaderActive,
            cleanedLayoutActive,
            cleanedDistractionFree,
            accordionsRestored,
            focusCalledDuringCleanup: focusCalled,
            netListenersCount
        };
    """

    res = run_js_in_chrome(payload)
    data = res["data"]
    assert not data["hasInlineStyle"], "Debe eliminarse el estilo inline de width: 0%"
    assert data["progressBarSelectorMatch"], "El CSS debe definir width: 0; para la barra de progreso"
    assert data["hasReaderActive"]
    assert data["hasLayoutActive"]
    assert data["hasDistractionFree"]
    assert data["cleanedReaderActive"] == False, "La limpieza debe quitar reader-active"
    assert data["cleanedLayoutActive"] == False, "La limpieza debe quitar reader-layout-active"
    assert data["cleanedDistractionFree"] == False, "La limpieza debe quitar reader-distraction-free"
    assert data["accordionsRestored"], "La limpieza debe restaurar los acordeones a su estado original"
    assert data["addListenerOrderCorrect"], "Router._readerCleanup debe ejecutarse antes de registrar nuevos listeners"
    assert not data["focusCalledDuringCleanup"], "La limpieza no debe intentar enfocar el botón durante el cambio de ruta (idempotente sin foco)"
    assert data["netListenersCount"] == 0, "No debe haber listeners duplicados o fugas de eventos"


def test_reader_contrast_and_layout_rules():
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # 1. reader-active forces a single column with !important
    assert "#protocol-full-panel.reader-active .content-accordion-grid {" in css
    assert "display: flex !important;" in css
    assert "flex-direction: column !important;" in css
    assert "grid-template-columns: 1fr !important;" in css

    # 2. reader-active anula background de .clinical-card
    assert "#protocol-full-panel.reader-active details.content-accordion.clinical-card" in css
    assert "background: transparent !important;" in css
    assert "background-color: transparent !important;" in css

    # 3. Overrides específicos para body.dark-mode
    assert "body.dark-mode #protocol-full-panel.reader-active" in css

    # 4. summary y body heredan el color del tema
    assert "#protocol-full-panel.reader-active .content-accordion-summary" in css
    assert "#protocol-full-panel.reader-active .content-accordion-body" in css
    assert "color: inherit !important;" in css

    # 5. subtitle-en tiene contraste corregido
    assert "#protocol-full-panel.reader-active .protocol-reader-page .subtitle-en {" in css
    assert "opacity: 0.78;" in css

    # 6. Colores de enlace para warm, sepia, white, night
    assert '#protocol-full-panel.reader-active .protocol-reader-page[data-reader-theme="warm"] a' in css
    assert '#protocol-full-panel.reader-active .protocol-reader-page[data-reader-theme="sepia"] a' in css
    assert '#protocol-full-panel.reader-active .protocol-reader-page[data-reader-theme="white"] a' in css
    assert '#protocol-full-panel.reader-active .protocol-reader-page[data-reader-theme="night"] a' in css

    # 7. Los enlaces tienen text-decoration visible
    assert "text-decoration: underline !important;" in css

    # 8. Selector nocturno de .protocol-linked-items usa correcto
    assert '#protocol-full-panel.reader-active .protocol-reader-page[data-reader-theme="night"] .protocol-linked-items' in css

    # 9. Las flechas se ocultan
    assert "#protocol-full-panel.reader-active .content-accordion-arrow {" in css
    assert "display: none !important;" in css

    # 10. La interfaz normal conserva dos columnas desde 768 px
    assert "@media (min-width: 768px) {" in css
    assert "grid-template-columns: repeat(" in css or "grid-template-columns: 1fr 1fr" in css or "grid-template-columns: repeat(2" in css

    # 11. Explicit hidden rules
    assert ".protocol-reader-controls[hidden]," in css
    assert ".protocol-reader-progress[hidden] {" in css
    assert "display: none !important;" in css


def test_reader_contrast_and_layout_headless():
    payload = """
        const app = document.getElementById("app");
        // Put app in dark mode to simulate dark mode
        document.body.classList.add("dark-mode");
        
        await Router.renderProtocolDetail(app, "rush");
        const openBtn = document.getElementById("protocol-reader-open");
        openBtn.click();

        const grid = document.querySelector("#protocol-full-panel.reader-active .content-accordion-grid");
        const computedGrid = window.getComputedStyle(grid);
        const gridDisplay = computedGrid.display;
        const gridFlexDir = computedGrid.flexDirection;

        const accordion = document.querySelector("#protocol-full-panel.reader-active details.content-accordion");
        const computedAcc = window.getComputedStyle(accordion);
        const accBg = computedAcc.backgroundColor;

        const arrow = document.querySelector("#protocol-full-panel.reader-active .content-accordion-arrow");
        const computedArrow = window.getComputedStyle(arrow);
        const arrowDisplay = computedArrow.display;

        // Verify colors are inherited
        const p = document.querySelector("#protocol-reader-page p");
        const pColor = window.getComputedStyle(p).color;

        // Verify subtitle opacity
        const sub = document.querySelector(".protocol-reader-page .subtitle-en");
        let subOpacity = "1";
        if (sub) {
            subOpacity = window.getComputedStyle(sub).opacity;
        }

        // Clean up dark mode class
        document.body.classList.remove("dark-mode");

        return {
            gridDisplay,
            gridFlexDir,
            accBg,
            arrowDisplay,
            subOpacity
        };
    """
    res = run_js_in_chrome(payload)
    data = res["data"]
    assert data["gridDisplay"] == "flex"
    assert data["gridFlexDir"] == "column"
    assert data["accBg"] in ["transparent", "rgba(0, 0, 0, 0)", "initial", "none"]
    assert data["arrowDisplay"] == "none"
    assert float(data["subOpacity"]) == pytest.approx(0.78, abs=0.02)
