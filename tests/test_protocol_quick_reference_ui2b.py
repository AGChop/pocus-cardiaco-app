import os
import json
import re
import base64
import tempfile
import subprocess
import urllib.request
import pytest
from pathlib import Path
from tests.helpers.chrome_runner import run_js_in_chrome as _run_js_in_chrome

def run_js_in_chrome(js_payload):
    try:
        return _run_js_in_chrome(js_payload, timeout=45)
    except Exception as e:
        pytest.fail(str(e))


def test_translations_exact():
    # 1. translations exist & 2. exact texts
    trans_path = "data/translations.json"
    assert os.path.exists(trans_path)
    with open(trans_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", {})

    assert "label.protocol_quick_title" in translations
    assert translations["label.protocol_quick_title"]["es"] == "Resumen en una mirada"
    assert translations["label.protocol_quick_title"]["en"] == "At-a-glance summary"

    assert "label.protocol_quick_description" in translations
    assert translations["label.protocol_quick_description"]["es"] == "Evaluación esencial y alertas clave en una sola ficha."
    assert translations["label.protocol_quick_description"]["en"] == "Essential assessment and key alerts in a single card."

    assert "label.protocol_quick_sequence" in translations
    assert translations["label.protocol_quick_sequence"]["es"] == "Secuencia de exploración"
    assert translations["label.protocol_quick_sequence"]["en"] == "Examination sequence"

    assert "label.protocol_quick_expand_hint" in translations
    assert translations["label.protocol_quick_expand_hint"]["es"] == "Amplíe la información en la Guía interactiva o en Contenido completo."
    assert translations["label.protocol_quick_expand_hint"]["en"] == "Review the Interactive guide or Full content for additional detail."

    assert "label.protocol_quick_assess" in translations
    assert translations["label.protocol_quick_assess"]["es"] == "Evaluar"
    assert translations["label.protocol_quick_assess"]["en"] == "Assess"

    assert "label.protocol_quick_alerts" in translations
    assert translations["label.protocol_quick_alerts"]["es"] == "Alertas"
    assert translations["label.protocol_quick_alerts"]["en"] == "Red flags"


def test_clinical_data_specification():
    # 3. RUSH has exactly 3 components
    # 4. Each component contains quick_reference
    # 5. Each quick_reference contains only assess and alerts
    # 6. assess/alerts contain es and en
    # 7. Six texts match specification exactly
    # 8. targets, possible_findings, suggested_views intact
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    protocols = data.get("protocols", [])
    rush = next((p for p in protocols if p["id"] == "rush"), None)
    assert rush is not None
    assert len(rush["components"]) == 3

    components = rush["components"]
    assert components[0]["id"] == "pump"
    assert components[1]["id"] == "tank"
    assert components[2]["id"] == "pipes"

    # Targets / findings / suggested views intact
    for comp in components:
        assert "suggested_views" in comp and len(comp["suggested_views"]) > 0
        assert "targets" in comp and len(comp["targets"]) > 0
        assert "possible_findings" in comp and len(comp["possible_findings"]) > 0
        assert "quick_reference" in comp

        qr = comp["quick_reference"]
        assert list(qr.keys()) == ["assess", "alerts"]
        assert list(qr["assess"].keys()) == ["es", "en"]
        assert list(qr["alerts"].keys()) == ["es", "en"]

    # Verify exact texts
    pump_qr = components[0]["quick_reference"]
    assert pump_qr["assess"]["es"] == "Función global del VI, tamaño del VD y derrame pericárdico con colapso de cavidades derechas."
    assert pump_qr["assess"]["en"] == "Global LV function, RV size, and pericardial effusion with right-sided chamber collapse."
    assert pump_qr["alerts"]["es"] == "Taponamiento, VI hiperdinámico o severamente deprimido y dilatación aguda del VD."
    assert pump_qr["alerts"]["en"] == "Tamponade, a hyperdynamic or severely depressed LV, and acute RV dilation."

    tank_qr = components[1]["quick_reference"]
    assert tank_qr["assess"]["es"] == "VCI, patrón pulmonar y pleural, y líquido libre intraperitoneal."
    assert tank_qr["assess"]["en"] == "IVC, lung and pleural pattern, and free intraperitoneal fluid."
    assert tank_qr["alerts"]["es"] == "Depleción o congestión marcada, neumotórax, edema pulmonar o SDRA y líquido libre intraperitoneal."
    assert tank_qr["alerts"]["en"] == "Marked volume depletion or congestion, pneumothorax, pulmonary edema or ARDS, and free intraperitoneal fluid."

    pipes_qr = components[2]["quick_reference"]
    assert pipes_qr["assess"]["es"] == "Aorta abdominal y compresibilidad de las venas femoral común y poplítea."
    assert pipes_qr["assess"]["en"] == "Abdominal aorta and compressibility of the common femoral and popliteal veins."
    assert pipes_qr["alerts"]["es"] == "Aneurisma o disección aórtica y TVP proximal."
    assert pipes_qr["alerts"]["en"] == "Aortic aneurysm or dissection and proximal DVT."


def test_router_renderer_generic_constraints():
    # 9. renderProtocolQuickReference is generic
    # 10. No rush, pump, tank, pipes, Bomba, Tanque, Tuberías in method
    # 11. No read of suggested_views, targets, possible_findings, etc.
    # 12. Reads quick_reference, assess, alerts
    # 13. Exactly one <article>
    # 14. No <details> or <summary>
    # 15. No .slice
    # 16. No inline styles
    # 17. No card class on component/footer
    router_path = "assets/js/router.js"
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_idx = content.find("renderProtocolQuickReference(protocol, escapeHTML) {")
    end_idx = content.find("// DETALLE DE PROTOCOLO", start_idx)
    assert start_idx != -1
    assert end_idx != -1
    method_code = content[start_idx:end_idx]

    # Check for hardcoded clinical terms
    prohibited = ["rush", "pump", "tank", "pipes", "Bomba", "Tanque", "Tuberías"]
    for p in prohibited:
        assert p not in method_code, f"Found hardcoded term: {p}"

    # Check for reading full clinical data fields
    prohibited_fields = [
        "suggested_views", "targets", "possible_findings", "clinical_questions",
        "interpretation_limits", "linked_measurement_ids", "linked_window_ids", "integration"
    ]
    for pf in prohibited_fields:
        assert pf not in method_code, f"Read prohibited field: {pf}"

    # Check for reading correct fields
    assert "quick_reference" in method_code
    assert "assess" in method_code
    assert "alerts" in method_code

    # Structural constraints
    assert method_code.count("<article") == 1
    assert method_code.count("</article>") == 1
    assert "<details" not in method_code
    assert "<summary" not in method_code
    assert ".slice" not in method_code
    assert "style=" not in method_code

    # No generic card class inside components or footer loop
    assert 'class="protocol-quick-component card"' not in method_code
    assert 'class="protocol-quick-reminder card"' not in method_code


def test_quick_tab_styles_ui2c():
    # 27. CSS block UI2C
    # 28. CSS columns 1 mobile, 3 desktop
    # 29. CSS doesn't use overflow-x: auto/scroll, line-clamp, text-overflow: ellipsis
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        styles = f.read()

    css_start = styles.find("/* --- PROTOCOL QUICK REFERENCE COMPACT (UI2C) --- */")
    assert css_start != -1
    ui2c_css = styles[css_start:]

    required_classes = [
        ".protocol-quick-card",
        ".protocol-quick-header",
        ".protocol-quick-sequence",
        ".protocol-quick-sequence-item",
        ".protocol-quick-components",
        ".protocol-quick-component",
        ".protocol-quick-section",
        ".protocol-quick-expand-hint"
    ]
    for cls in required_classes:
        assert cls in ui2c_css

    # Check column responsive grids
    assert "grid-template-columns: 1fr" in ui2c_css or "grid-template-columns: 1fr" in styles
    assert "grid-template-columns: 1fr 1fr 1fr" in ui2c_css

    # Prohibited style rules
    assert "overflow-x: auto" not in ui2c_css
    assert "overflow-x: scroll" not in ui2c_css
    assert "line-clamp" not in ui2c_css
    assert "text-overflow: ellipsis" not in ui2c_css


def test_cache_name_and_precache_entries():
    # 30. Cache is quick2
    # 31. ASSETS_TO_CACHE has 36 entries
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1) == "pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final-logo2-pwa1-flow1-quick2-reader1"

    assets_block_match = re.search(r"const ASSETS_TO_CACHE = \[(.*?)\];", content, re.DOTALL)
    assert assets_block_match is not None
    assets_text = assets_block_match.group(1)
    assets = [a.strip().strip("'\",") for a in assets_text.split("\n") if a.strip()]
    assert len(assets) == 36


def test_non_modified_catalogs():
    # 32. protocols.json integral
    # 33. measurements.json has 101 records
    # 34. Other clinical data not modified
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101

    for path in ["data/windows.json", "data/glossary.json", "data/references.json", "data/classifications.json"]:
        assert os.path.exists(path)


def test_real_headless_rendering_and_bad_render_strings():
    # 18. ES HTML contains: La Bomba, El Tanque, Las Tuberías, Evaluar, Alertas, 6 ES texts
    # 19. EN HTML contains: The Pump, The Tank, The Pipes, Assess, Red flags, 6 EN texts
    # 20. Panel: 1 article.protocol-quick-card, 3 .protocol-quick-component, 3 .protocol-quick-assess, 3 .protocol-quick-alerts
    # 21. Summary does not contain complete clinical lists.
    # 22. Text size notably smaller
    # 23. No undefined, null, [object Object]
    # 24. Four tabs work
    # 25. Selected tab persists
    # 26. Keyboard navigation works
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

        // Conteos del DOM
        const articleCountES = quickPanel.querySelectorAll("article.protocol-quick-card").length;
        const componentCountES = quickPanel.querySelectorAll(".protocol-quick-component").length;
        const assessCountES = quickPanel.querySelectorAll(".protocol-quick-assess").length;
        const alertsCountES = quickPanel.querySelectorAll(".protocol-quick-alerts").length;

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

        // Luego vuelve a Resumen rápido y registra
        quickTabEN.click();

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
            articleCountES,
            componentCountES,
            assessCountES,
            alertsCountES,
            htmlBase64ES,
            textBase64ES,
            restoredQuickVisibleEN,
            restoredGuideHiddenEN,
            restoredQuickSelectedEN,
            restoredGuideSelectedEN,
            guideVisibleAfterGuideClickEN,
            quickHiddenAfterGuideClickEN,
            articleCountEN,
            componentCountEN,
            htmlBase64EN,
            textBase64EN
        };
    """

    res = run_js_in_chrome(js_payload)
    data = res["data"]

    # Tab visibility and selected attributes
    assert data["hiddenQuickBeforeClickES"] is True
    assert data["hiddenGuideBeforeClickES"] is False
    assert data["hiddenQuickAfterClickES"] is False
    assert data["hiddenGuideAfterClickES"] is True
    assert data["ariaSelectedQuickES"] == "true"
    assert data["ariaSelectedGuideES"] == "false"

    # Panel structural element counts
    assert data["articleCountES"] == 1
    assert data["componentCountES"] == 3
    assert data["assessCountES"] == 3
    assert data["alertsCountES"] == 3

    # Decoded texts
    html_es = base64.b64decode(data["htmlBase64ES"]).decode("utf-8")
    text_es = base64.b64decode(data["textBase64ES"]).decode("utf-8")
    html_en = base64.b64decode(data["htmlBase64EN"]).decode("utf-8")
    text_en = base64.b64decode(data["textBase64EN"]).decode("utf-8")

    # Confirm correct translations in ES
    assert "Bomba" in text_es
    assert "Tanque" in text_es
    assert "Tuberías" in text_es
    assert "Evaluar" in text_es
    assert "Alertas" in text_es

    # Confirm exact clinical ES texts
    assert "Función global del VI, tamaño del VD y derrame pericárdico" in text_es
    assert "Taponamiento, VI hiperdinámico o severamente deprimido" in text_es
    assert "VCI, patrón pulmonar y pleural, y líquido libre" in text_es
    assert "Depleción o congestión marcada, neumotórax" in text_es
    assert "Aorta abdominal y compresibilidad de las venas" in text_es
    assert "Aneurisma o disección aórtica y TVP proximal." in text_es

    # Confirm English texts
    assert "Pump" in text_en
    assert "Tank" in text_en
    assert "Pipes" in text_en
    assert "Assess" in text_en
    assert "Red flags" in text_en

    # Confirm exact clinical EN texts
    assert "Global LV function, RV size, and pericardial effusion" in text_en
    assert "Tamponade, a hyperdynamic or severely depressed LV" in text_en
    assert "IVC, lung and pleural pattern, and free" in text_en
    assert "Marked volume depletion or congestion, pneumothorax" in text_en
    assert "Abdominal aorta and compressibility of the common" in text_en
    assert "Aortic aneurysm or dissection and proximal DVT." in text_en

    # Validate absence of complete clinical detail lists (like targets or possible findings details)
    # E.g. "Kissing papillary muscles" or "Derrame pericárdico significativo con colapso diastólico del VD" should not be in the quick reference view
    assert "kissing papillary muscles" not in text_en.lower()
    assert "colapso diastólico del vd" not in text_es.lower()

    # Validate character length is notably smaller (e.g. less than 1500 chars when whitespace is normalized)
    assert len(re.sub(r'\s+', ' ', text_es).strip()) < 1500

    # Avoid bad render strings
    for html in [html_es, html_en]:
        assert "undefined" not in html
        assert "null" not in html
        assert "[object Object]" not in html


def test_four_tabs_keyboard_and_storage():
    # 24, 25, 26 keyboard navigation and session storage
    router_path = "assets/js/router.js"
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

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
