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
    # Read translations dictionary
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations_dict = json.load(f)

    # Read clinical catalogs
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols_json = f.read()

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
            getWindows: async () => [],
            getMeasurements: async () => [],
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

            if (!window.__moduleStatus.i18n || !window.__moduleStatus.search || !window.__moduleStatus.router) {
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

    html_content = html_content.replace("//TRANSLATIONS_DICT//", json.dumps(translations_dict["translations"]))
    html_content = html_content.replace("//PROTOCOLS_JSON//", protocols_json)
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


def test_five_translations_exact():
    trans_path = "data/translations.json"
    assert os.path.exists(trans_path)
    with open(trans_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", {})

    assert "label.protocol_quick_tab" in translations
    assert translations["label.protocol_quick_tab"]["es"] == "Resumen rápido"
    assert translations["label.protocol_quick_tab"]["en"] == "Quick reference"

    assert "label.protocol_quick_title" in translations
    assert translations["label.protocol_quick_title"]["es"] == "Exploración y hallazgos"
    assert translations["label.protocol_quick_title"]["en"] == "Examination and findings"

    assert "label.protocol_quick_description" in translations
    assert translations["label.protocol_quick_description"]["es"] == "Vista compacta de la secuencia, los objetivos de evaluación y los hallazgos posibles."
    assert translations["label.protocol_quick_description"]["en"] == "Compact view of the sequence, evaluation targets, and possible findings."

    assert "label.protocol_quick_sequence" in translations
    assert translations["label.protocol_quick_sequence"]["es"] == "Secuencia de exploración"
    assert translations["label.protocol_quick_sequence"]["en"] == "Examination sequence"

    assert "label.protocol_quick_expand_hint" in translations
    assert translations["label.protocol_quick_expand_hint"]["es"] == "Consulte la guía interactiva o el contenido completo para revisar preguntas clínicas, mediciones, límites y referencias."
    assert translations["label.protocol_quick_expand_hint"]["en"] == "Use the interactive guide or full content to review clinical questions, measurements, limitations, and references."


def test_quick_tab_elements_and_rendering():
    router_path = "assets/js/router.js"
    assert os.path.exists(router_path)
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar el orden de las pestañas en el HTML de renderProtocolDetail
    tab_list_match = re.search(r'class="protocol-tab-list"[\s\S]*?(<button[\s\S]*?</button>\s*){4}', content)
    assert tab_list_match is not None
    tabs_html = tab_list_match.group(0)

    # Posición exacta de quick entre guide and content
    idx_guide = tabs_html.find('data-protocol-tab="guide"')
    idx_quick = tabs_html.find('data-protocol-tab="quick"')
    idx_content = tabs_html.find('data-protocol-tab="content"')
    idx_references = tabs_html.find('data-protocol-tab="references"')

    assert idx_guide != -1
    assert idx_quick != -1
    assert idx_content != -1
    assert idx_references != -1
    assert idx_guide < idx_quick < idx_content < idx_references

    # Comprobar que el tablist contiene exactamente cuatro botones con data-protocol-tab
    assert tabs_html.count('data-protocol-tab=') == 4

    # Extraer específicamente la etiqueta de apertura del botón con id="protocol-quick-tab"
    quick_btn_match = re.search(r'<button[^>]*id="protocol-quick-tab"[^>]*>', tabs_html)
    assert quick_btn_match is not None
    quick_btn_tag = quick_btn_match.group(0)

    # Verificar dentro de esa etiqueta exacta
    assert 'role="tab"' in quick_btn_tag
    assert 'aria-selected="false"' in quick_btn_tag
    assert 'aria-controls="protocol-quick-panel"' in quick_btn_tag
    assert 'tabindex="-1"' in quick_btn_tag
    assert 'data-protocol-tab="quick"' in quick_btn_tag

    # Comprobar que protocol-guide-tab tiene aria-selected="true" y tabindex="0"
    guide_btn_match = re.search(r'<button[^>]*id="protocol-guide-tab"[^>]*>', tabs_html)
    assert guide_btn_match is not None
    guide_btn_tag = guide_btn_match.group(0)
    assert 'aria-selected="true"' in guide_btn_tag
    assert 'tabindex="0"' in guide_btn_tag

    # Comprobar que los paneles guide, quick, full y references son hermanos y que quick no está contenido dentro de guide
    idx_guide_panel = content.find('id="protocol-guide-panel"')
    idx_quick_panel = content.find('id="protocol-quick-panel"')
    idx_full_panel = content.find('id="protocol-full-panel"')
    idx_refs_panel = content.find('id="protocol-references-panel"')

    assert idx_guide_panel != -1
    assert idx_quick_panel != -1
    assert idx_full_panel != -1
    assert idx_refs_panel != -1
    assert idx_guide_panel < idx_quick_panel < idx_full_panel < idx_refs_panel

    # Verificar la secuencia estructural exacta de cierre y apertura mediante regex
    pattern = r"</div>\s*</div>\s*</div>\s*<!-- PESTAÑA: RESUMEN RÁPIDO -->\s*<div id=\"protocol-quick-panel\""
    assert re.search(pattern, content) is not None


def test_quick_reference_method_and_contents():
    router_path = "assets/js/router.js"
    assert os.path.exists(router_path)
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extracción robusta del método
    start_idx = content.find("renderProtocolQuickReference(protocol, escapeHTML) {")
    end_idx = content.find("// DETALLE DE PROTOCOLO", start_idx)
    assert start_idx != -1
    assert end_idx != -1
    method_code = content[start_idx:end_idx]

    # Exactamente una ficha <article>
    assert method_code.count("<article") == 1
    assert method_code.count("</article>") == 1

    # Ausencia de <details> y <summary> en el resumen
    assert "<details" not in method_code
    assert "<summary" not in method_code

    # Generación dinámica
    assert ".components.forEach" in method_code or ".components.map" in method_code

    # Campos requeridos y ausencias
    assert "suggested_views" in method_code
    assert "targets" in method_code
    assert "possible_findings" in method_code

    # Ausencia de campos de detalle ampliado
    assert "clinical_questions" not in method_code
    assert "interpretation_limits" not in method_code
    assert "linked_measurement_ids" not in method_code
    assert "linked_window_ids" not in method_code
    assert "integration" not in method_code

    # Ausencia de slice y truncamiento
    assert ".slice" not in method_code
    assert "[:" not in method_code

    # Escape específico
    assert "escapeHTML" in method_code

    # Ausencia de nombres específicos de RUSH en el método
    prohibited = ["rush", "pump", "tank", "pipes", "Bomba", "Tanque", "Tuberías"]
    for word in prohibited:
        assert word not in method_code, f"Palabra prohibida encontrada en renderProtocolQuickReference: {word}"

    # Ausencia de estilos inline dentro del método
    assert "style=" not in method_code


def test_quick_tab_styles():
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        styles = f.read()

    # Extraer sección de estilos
    css_start = styles.find("/* --- PROTOCOL QUICK REFERENCE (UI2B) --- */")
    assert css_start != -1
    ui2b_css = styles[css_start:]

    required_classes = [
        ".protocol-quick-card",
        ".protocol-quick-header",
        ".protocol-quick-sequence",
        ".protocol-quick-sequence-item",
        ".protocol-quick-components",
        ".protocol-quick-component",
        ".protocol-quick-grid",
        ".protocol-quick-section",
        ".protocol-quick-reminder",
        ".protocol-quick-expand-hint"
    ]
    for cls in required_classes:
        assert cls in ui2b_css

    # Variables CSS inexistentes
    prohibited_vars = [
        "--primary-bg-dark",
        "--card-bg-dark",
        "--text-main-dark",
        "--text-muted-dark",
        "--bg-light",
        "--bg-dark",
        "--text-main"
    ]
    for p_var in prohibited_vars:
        pattern = r"var\(\s*" + re.escape(p_var) + r"\s*\)"
        assert re.search(pattern, ui2b_css) is None, f"Variable CSS prohibida detectada en el bloque UI2B: {p_var}"

    # Conectores decorativos en CSS
    assert "::before" in ui2b_css
    assert "::after" in ui2b_css

    # Verificaciones expresas en ui2b_css
    assert "min-width: 0" in ui2b_css
    assert "overflow-wrap: anywhere" in ui2b_css
    assert "overflow-x: auto" not in ui2b_css
    assert "overflow-x: scroll" not in ui2b_css
    assert "@media (min-width: 768px)" in ui2b_css
    assert "grid-template-columns" in ui2b_css
    assert "@media (prefers-reduced-motion: reduce)" in ui2b_css
    assert ".protocol-quick-component h4" in ui2b_css
    assert ".protocol-quick-component h5" not in ui2b_css


def test_cache_name_and_precache_entries():
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1) == "pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final-logo2-pwa1-flow1-quick1"

    assets_block_match = re.search(r"const ASSETS_TO_CACHE = \[(.*?)\];", content, re.DOTALL)
    assert assets_block_match is not None
    assets_text = assets_block_match.group(1)
    assets = [a.strip().strip("'\",") for a in assets_text.split("\n") if a.strip()]
    assert len(assets) == 36


def test_clinical_data_intact():
    files = [
        "data/protocols.json",
        "data/measurements.json",
        "data/windows.json",
        "data/glossary.json",
        "data/references.json",
        "data/classifications.json",
        "data/minimum_pocus_set.json"
    ]
    for path in files:
        assert os.path.exists(path)

    with open("data/protocols.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    protocols = data.get("protocols", [])
    rush = next((p for p in protocols if p["id"] == "rush"), None)
    assert rush is not None
    assert len(rush["components"]) == 3
    assert rush["components"][0]["id"] == "pump"
    assert rush["components"][1]["id"] == "tank"
    assert rush["components"][2]["id"] == "pipes"

    assert len(rush["components"][0]["possible_findings"]) > 0
    assert len(rush["components"][0]["targets"]) > 0
    assert len(rush["components"][0]["suggested_views"]) > 0

    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101


def test_real_headless_rendering_and_bad_render_strings():
    js_payload = """
        const container = document.getElementById("app");

        // 1. Renderizar en español
        Storage.setLanguage("es");
        await Router.renderProtocolDetail(container, "rush");

        const quickTab = document.getElementById("protocol-quick-tab");
        const guideTab = document.getElementById("protocol-guide-tab");
        const guidePanel = document.getElementById("protocol-guide-panel");
        const quickPanel = document.getElementById("protocol-quick-panel");
        const fullPanel = document.getElementById("protocol-full-panel");
        const referencesPanel = document.getElementById("protocol-references-panel");

        // Registrar estados antes del clic
        const hiddenQuickBeforeClickES = quickPanel.hasAttribute("hidden");
        const hiddenGuideBeforeClickES = guidePanel.hasAttribute("hidden");

        // Click en la pestaña
        quickTab.click();

        // Registrar estados después del clic
        const hiddenQuickAfterClickES = quickPanel.hasAttribute("hidden");
        const hiddenGuideAfterClickES = guidePanel.hasAttribute("hidden");
        const ariaSelectedQuickES = quickTab.getAttribute("aria-selected");
        const ariaSelectedGuideES = guideTab.getAttribute("aria-selected");

        // Hermandad y jerarquía
        const closestGuidePanelES = quickPanel.closest("#protocol-guide-panel") === null;
        const sameParentGuideES = quickPanel.parentElement === guidePanel.parentElement;
        const sameParentFullES = quickPanel.parentElement === fullPanel.parentElement;
        const sameParentRefsES = quickPanel.parentElement === referencesPanel.parentElement;

        // Conteos del DOM
        const articleCountES = quickPanel.querySelectorAll("article.protocol-quick-card").length;
        const componentCountES = quickPanel.querySelectorAll(".protocol-quick-component").length;

        // codificación UTF-8 segura
        const encodeBase64 = (value) => btoa(unescape(encodeURIComponent(value)));

        const htmlBase64ES = encodeBase64(quickPanel.innerHTML);
        const textBase64ES = encodeBase64(quickPanel.textContent);

        // 2. Renderizar en inglés (restaura de la sesión)
        Storage.setLanguage("en");
        await I18n.init();
        await Router.renderProtocolDetail(container, "rush");

        const quickTabEN = document.getElementById("protocol-quick-tab");
        const guideTabEN = document.getElementById("protocol-guide-tab");
        const guidePanelEN = document.getElementById("protocol-guide-panel");
        const quickPanelEN = document.getElementById("protocol-quick-panel");

        const restoredQuickVisibleEN = !quickPanelEN.hasAttribute("hidden");
        const restoredGuideHiddenEN = guidePanelEN.hasAttribute("hidden");
        const restoredQuickSelectedEN = quickTabEN.getAttribute("aria-selected");
        const restoredGuideSelectedEN = guideTabEN.getAttribute("aria-selected");

        // Luego pulsa Guía y registra
        guideTabEN.click();

        const guideVisibleAfterGuideClickEN = !guidePanelEN.hasAttribute("hidden");
        const quickHiddenAfterGuideClickEN = quickPanelEN.hasAttribute("hidden");
        const guideSelectedAfterGuideClickEN = guideTabEN.getAttribute("aria-selected");
        const quickSelectedAfterGuideClickEN = quickTabEN.getAttribute("aria-selected");

        // Luego vuelve a Resumen rápido y registra
        quickTabEN.click();

        const quickVisibleAfterQuickClickEN = !quickPanelEN.hasAttribute("hidden");
        const guideHiddenAfterQuickClickEN = guidePanelEN.hasAttribute("hidden");
        const quickSelectedAfterQuickClickEN = quickTabEN.getAttribute("aria-selected");
        const guideSelectedAfterQuickClickEN = guideTabEN.getAttribute("aria-selected");

        const articleCountEN = quickPanelEN.querySelectorAll("article.protocol-quick-card").length;
        const componentCountEN = quickPanelEN.querySelectorAll(".protocol-quick-component").length;

        const htmlBase64EN = encodeBase64(quickPanelEN.innerHTML);
        const textBase64EN = encodeBase64(quickPanelEN.textContent);

        return {
            hiddenQuickBeforeClickES,
            hiddenGuideBeforeClickES,
            hiddenQuickAfterClickES,
            hiddenGuideAfterClickES,
            ariaSelectedQuickES,
            ariaSelectedGuideES,
            closestGuidePanelES,
            sameParentGuideES,
            sameParentFullES,
            sameParentRefsES,
            articleCountES,
            componentCountES,
            htmlBase64ES,
            textBase64ES,
            restoredQuickVisibleEN,
            restoredGuideHiddenEN,
            restoredQuickSelectedEN,
            restoredGuideSelectedEN,
            guideVisibleAfterGuideClickEN,
            quickHiddenAfterGuideClickEN,
            guideSelectedAfterGuideClickEN,
            quickSelectedAfterGuideClickEN,
            quickVisibleAfterQuickClickEN,
            guideHiddenAfterQuickClickEN,
            quickSelectedAfterQuickClickEN,
            guideSelectedAfterQuickClickEN,
            articleCountEN,
            componentCountEN,
            htmlBase64EN,
            textBase64EN
        };
    """

    res = run_js_in_chrome(js_payload)
    data = res["data"]

    # Antes de pulsar en español
    assert data["hiddenQuickBeforeClickES"] is True
    assert data["hiddenGuideBeforeClickES"] is False

    # Después de pulsar en español
    assert data["hiddenQuickAfterClickES"] is False
    assert data["hiddenGuideAfterClickES"] is True
    assert data["ariaSelectedQuickES"] == "true"
    assert data["ariaSelectedGuideES"] == "false"

    # Hermandad y jerarquía
    assert data["closestGuidePanelES"] is True
    assert data["sameParentGuideES"] is True
    assert data["sameParentFullES"] is True
    assert data["sameParentRefsES"] is True

    # Conteos en español
    assert data["articleCountES"] == 1
    assert data["componentCountES"] == 3

    # Decodificar español
    html_es = base64.b64decode(data["htmlBase64ES"]).decode("utf-8")
    text_es = base64.b64decode(data["textBase64ES"]).decode("utf-8")

    assert "<article" in html_es
    assert 'class="protocol-quick-card"' in html_es

    # Confirmar Bomba, Tanque y Tuberías en español
    assert "Bomba" in text_es
    assert "Tanque" in text_es
    assert "Tuberías" in text_es

    # Asersiones de inglés sobre restauración de sesión e interacción de pestañas
    assert data["restoredQuickVisibleEN"] is True
    assert data["restoredGuideHiddenEN"] is True
    assert data["restoredQuickSelectedEN"] == "true"
    assert data["restoredGuideSelectedEN"] == "false"

    assert data["guideVisibleAfterGuideClickEN"] is True
    assert data["quickHiddenAfterGuideClickEN"] is True
    assert data["guideSelectedAfterGuideClickEN"] == "true"
    assert data["quickSelectedAfterGuideClickEN"] == "false"

    assert data["quickVisibleAfterQuickClickEN"] is True
    assert data["guideHiddenAfterQuickClickEN"] is True
    assert data["quickSelectedAfterQuickClickEN"] == "true"
    assert data["guideSelectedAfterQuickClickEN"] == "false"

    # Conteos en inglés
    assert data["articleCountEN"] == 1
    assert data["componentCountEN"] == 3

    # Decodificar inglés
    html_en = base64.b64decode(data["htmlBase64EN"]).decode("utf-8")
    text_en = base64.b64decode(data["textBase64EN"]).decode("utf-8")

    assert "<article" in html_en
    assert 'class="protocol-quick-card"' in html_en

    assert "Pump" in text_en
    assert "Tank" in text_en
    assert "Pipes" in text_en

    # Evitar strings erróneas
    for html in [html_es, html_en]:
        assert "undefined" not in html, "Se detectó string 'undefined' renderizada en el HTML"
        assert "null" not in html, "Se detectó string 'null' renderizada en el HTML"
        assert "[object Object]" not in html, "Se detectó string '[object Object]' renderizada en el HTML"

    # Cargar datos clínicos reales para contraste dinámico
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols_data = json.load(f)

    rush_proto = next((p for p in protocols_data["protocols"] if p["id"] == "rush"), None)
    assert rush_proto is not None

    def localize(item, lang):
        if isinstance(item, dict):
            return item.get(lang, "")
        return item

    # Comprobar todos los views, targets y findings dinámicamente en ambos idiomas
    for comp in rush_proto["components"]:
        for view in (comp.get("suggested_views") or []):
            val_es = localize(view, "es")
            val_en = localize(view, "en")
            assert val_es in text_es, f"Falta la vista sugerida '{val_es}' en español"
            assert val_en in text_en, f"Falta la vista sugerida '{val_en}' en inglés"

        for target in (comp.get("targets") or []):
            val_es = localize(target, "es")
            val_en = localize(target, "en")
            assert val_es in text_es, f"Falta el objetivo '{val_es}' en español"
            assert val_en in text_en, f"Falta el objetivo '{val_en}' en inglés"

        for finding in (comp.get("possible_findings") or []):
            val_es = localize(finding, "es")
            val_en = localize(finding, "en")
            assert val_es in text_es, f"Falta el hallazgo '{val_es}' en español"
            assert val_en in text_en, f"Falta el hallazgo '{val_en}' en inglés"

        # Comprobar especialmente que no se pierda ningún hallazgo del componente Tanque
        if comp["id"] == "tank":
            for finding in comp["possible_findings"]:
                val_es = localize(finding, "es")
                val_en = localize(finding, "en")
                assert val_es in text_es
                assert val_en in text_en


def test_four_tabs_keyboard_and_storage():
    router_path = "assets/js/router.js"
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscamos initializeProtocolTabs
    start_tabs_idx = content.find("initializeProtocolTabs(protocolId) {")
    end_tabs_idx = content.find("initializeProtocolStepper", start_tabs_idx)
    assert start_tabs_idx != -1
    assert end_tabs_idx != -1
    tabs_code = content[start_tabs_idx:end_tabs_idx]

    assert "Storage.setSessionState" in tabs_code
    assert "Storage.getSessionState" in tabs_code
    assert "pocus-protocol-tab-" in tabs_code

    assert "keydown" in tabs_code
    assert "ArrowRight" in tabs_code
    assert "ArrowLeft" in tabs_code
    assert "Home" in tabs_code
    assert "End" in tabs_code
