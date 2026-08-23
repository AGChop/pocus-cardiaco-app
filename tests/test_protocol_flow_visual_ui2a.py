import os
import json
import re

def test_four_translations_exact():
    # 1. Las cuatro traducciones exactas en español e inglés.
    trans_path = "data/translations.json"
    assert os.path.exists(trans_path)
    with open(trans_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", {})

    # label.protocol_flow_title
    assert "label.protocol_flow_title" in translations
    assert translations["label.protocol_flow_title"]["es"] == "Mapa del protocolo"
    assert translations["label.protocol_flow_title"]["en"] == "Protocol map"

    # label.protocol_flow_description
    assert "label.protocol_flow_description" in translations
    assert translations["label.protocol_flow_description"]["es"] == "Explore la secuencia general y despliegue cada etapa antes de avanzar por la guía."
    assert translations["label.protocol_flow_description"]["en"] == "Explore the overall sequence and expand each stage before moving through the guide."

    # label.protocol_flow_path_title
    assert "label.protocol_flow_path_title" in translations
    assert translations["label.protocol_flow_path_title"]["es"] == "Ruta de evaluación"
    assert translations["label.protocol_flow_path_title"]["en"] == "Evaluation pathway"

    # label.protocol_flow_go_to_step
    assert "label.protocol_flow_go_to_step" in translations
    assert translations["label.protocol_flow_go_to_step"]["es"] == "Ir a este paso"
    assert translations["label.protocol_flow_go_to_step"]["en"] == "Go to this step"


def test_protocol_flow_map_rendering_and_stepper_integration():
    # 2. Estructura semántica, clases CSS y extracción robusta
    router_path = "assets/js/router.js"
    assert os.path.exists(router_path)
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extracción robusta del método
    start_idx = content.find("renderProtocolFlowMap(steps, helpers) {")
    end_idx = content.find("// DETALLE DE PROTOCOLO", start_idx)
    assert start_idx != -1
    assert end_idx != -1
    map_code = content[start_idx:end_idx]

    # Verificar clases corregidas en JS
    assert "protocol-flow-shell" in map_code
    assert "protocol-flow-stage" in map_code
    assert "protocol-flow-actions" in map_code
    assert "protocol-flow-linked-items" in map_code
    assert "protocol-linked-items" not in map_code

    # Ausencia total de style= en renderProtocolFlowMap
    assert "style=" not in map_code

    # Estructura semántica requerida en el renderizador
    assert "<section" in map_code
    assert "aria-labelledby=" in map_code
    assert "<ol" in map_code
    assert "<li" in map_code
    assert "<details" in map_code
    assert "<summary" in map_code

    # escapeHTML assertions:
    assert "escapeHTML(stepTitle)" in map_code
    assert "escapeHTML(buttonLabel)" in map_code

    # presencia del aria-label localizado del botón:
    assert 'aria-label="${escapeHTML(buttonLabel)}"' in map_code or "aria-label='${escapeHTML(buttonLabel)}'" in map_code

    # protocol-flow-path-title-id and ol associated:
    assert "protocol-flow-path-title-id" in map_code
    assert 'aria-labelledby="protocol-flow-path-title-id"' in map_code or "aria-labelledby='protocol-flow-path-title-id'" in map_code

    # El <ol> tiene aria-labelledby
    assert re.search(r"<ol[^>]*aria-labelledby=", map_code) is not None

    # Generación dinámica
    assert ".forEach" in map_code

    # Primer details se abre inicialmente, otros no
    assert 'const isOpen = idx === 0 ? "open" : "";' in map_code
    assert 'details class="protocol-flow-card" ${isOpen}' in map_code or 'details class="protocol-flow-card" ${isOpen}' in map_code.replace("'", '"')

    # El botón tiene data-flow-step
    assert 'data-flow-step="${idx}"' in map_code

    # Ausencia de condiciones o nombres específicos de RUSH en renderProtocolFlowMap
    prohibited = ["rush", "pump", "tank", "pipes", "Bomba", "Tanque", "Tuberías"]
    for word in prohibited:
        assert word not in map_code, f"Palabra prohibida encontrada en renderProtocolFlowMap: {word}"

    # Presencia de subflujos para start, component, integration y summary
    assert 'step.type === "start"' in map_code
    assert 'step.type === "component"' in map_code
    assert 'step.type === "integration"' in map_code
    assert 'step.type === "summary"' in map_code

    # El contenido dinámico continúa usando escapeHTML
    assert "escapeHTML" in map_code

    # Buscamos la lógica de conexión en initializeProtocolStepper
    start_stepper_idx = content.find("initializeProtocolStepper(protocolId, steps) {")
    end_stepper_idx = content.find("// ABREVIATURAS", start_stepper_idx)
    assert start_stepper_idx != -1
    assert end_stepper_idx != -1
    stepper_code = content[start_stepper_idx:end_stepper_idx]

    # initializeProtocolStepper ejecuta exactamente showStep(stepIdx, true)
    assert "showStep(stepIdx, true)" in stepper_code

    # El índice se valida antes de usarlo
    assert "!isNaN(stepIdx)" in stepper_code
    assert "stepIdx >= 0" in stepper_code
    assert "stepIdx < steps.length" in stepper_code


def test_styles_flow_map_responsive():
    # 10. CSS, accesibilidad y conectores
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path)
    with open(css_path, "r", encoding="utf-8") as f:
        styles = f.read()

    # Extraer el bloque UI2A del CSS para inspeccionar solo esta sección
    css_start = styles.find("/* --- MAPA VISUAL DE PROTOCOLOS (UI2A) --- */")
    assert css_start != -1
    ui2a_css = styles[css_start:]

    # Clases requeridas en CSS
    required_classes = [
        ".protocol-flow-map",
        ".protocol-flow-list",
        ".protocol-flow-item",
        ".protocol-flow-card",
        ".protocol-flow-summary",
        ".protocol-flow-subflow",
        ".protocol-flow-stage",
        ".protocol-flow-jump",
        ".protocol-flow-shell",
        ".protocol-flow-actions",
        ".protocol-flow-linked-items"
    ]
    for cls in required_classes:
        assert cls in ui2a_css

    # Aserciones específicas solicitadas dentro del bloque de estilos
    assert ".protocol-flow-summary:focus-visible" in ui2a_css
    assert ".protocol-flow-jump:focus-visible" in ui2a_css
    assert "@media (prefers-reduced-motion: reduce)" in ui2a_css
    assert ".protocol-flow-subflow::before" in ui2a_css
    assert ".protocol-flow-stage::before" in ui2a_css
    assert "min-width: 0" in ui2a_css
    assert "overflow-wrap: anywhere" in ui2a_css
    assert "overflow-x: auto" not in ui2a_css
    assert "overflow-x: scroll" not in ui2a_css

    # Ausencia de las variables CSS inexistentes utilizando coincidencia exacta en var(...)
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
        assert re.search(pattern, ui2a_css) is None, f"Variable CSS prohibida detectada en el bloque UI2A: {p_var}"

    # Validar que existan conectores para .protocol-flow-stage
    assert ".protocol-flow-stage::before" in ui2a_css


def test_cache_name_and_precache_entries():
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1).startswith("pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final-logo2-pwa1-flow1")

    assets_block_match = re.search(r"const ASSETS_TO_CACHE = \[(.*?)\];", content, re.DOTALL)
    assert assets_block_match is not None
    assets_text = assets_block_match.group(1)
    assets = [a.strip().strip("'\",") for a in assets_text.split("\n") if a.strip()]
    assert len(assets) == 38


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

    assert rush["name_es"] == "Protocolo RUSH"
    assert rush["name_en"] == "RUSH Protocol"

    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101
