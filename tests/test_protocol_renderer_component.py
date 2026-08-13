import os
import json
import re
import base64
import pytest
from pathlib import Path
from tests.helpers.chrome_runner import run_js_in_chrome as _run_js_in_chrome

def run_js_in_chrome(js_payload):
    try:
        return _run_js_in_chrome(js_payload, timeout=45)
    except Exception as e:
        pytest.fail(str(e))

def test_component_existence_and_exposure():
    renderer_path = "assets/js/components/protocol-renderer.js"
    assert os.path.exists(renderer_path), "El archivo protocol-renderer.js no existe."
    
    with open(renderer_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "const ProtocolRenderer =" in content
    assert "renderQuickReference" in content

def test_pure_function_constraints():
    renderer_path = "assets/js/components/protocol-renderer.js"
    with open(renderer_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "document" not in content, "El componente no debe acceder a 'document'"
    assert "window" not in content, "El componente no debe acceder a 'window'"
    assert "Storage" not in content, "El componente no debe acceder a 'Storage'"
    assert "DataLoader" not in content, "El componente no debe acceder a 'DataLoader'"
    assert "Router" not in content, "El componente no debe acceder a 'Router'"

def test_router_adaptation_integrity():
    router_path = "assets/js/router.js"
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    start_idx = content.find("renderProtocolQuickReference(protocol, escapeHTML) {")
    assert start_idx != -1, "router.js debe conservar renderProtocolQuickReference"
    end_idx = content.find("}", start_idx)
    method_code = content[start_idx:end_idx+1]
    
    assert len(method_code.split("\n")) <= 10
    assert "ProtocolRenderer.renderQuickReference" in method_code

def test_index_html_order():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    idx_renderer = content.find("assets/js/components/protocol-renderer.js")
    idx_router = content.find("assets/js/router.js")
    assert idx_renderer != -1
    assert idx_router != -1
    assert idx_renderer < idx_router, "protocol-renderer.js debe cargarse antes de router.js en index.html"

def test_chrome_runner_loading():
    runner_path = "tests/helpers/chrome_runner.py"
    with open(runner_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    idx_renderer = content.find("protocol_renderer_src =")
    idx_router = content.find("router_src =")
    assert idx_renderer != -1
    assert idx_router != -1
    assert idx_renderer < idx_router, "chrome_runner.py debe definir protocol-renderer.js antes de router.js"
    
    assert "window.__moduleStatus.protocolRenderer = typeof ProtocolRenderer !== \"undefined\";" in content
    assert "!window.__moduleStatus.protocolRenderer" in content

def test_service_worker_integrity():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "./assets/js/components/protocol-renderer.js" in content
    
    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert "-prender1" in cache_match.group(1)

def test_renderer_via_chrome():
    js_payload = """
    const protocol = {
        id: "rush",
        components: [
            {
                id: "pump",
                name_es: "Bomba",
                name_en: "Pump",
                quick_reference: {
                    assess: { es: "Eval VI", en: "Assess LV" },
                    alerts: { es: "Alerta VI", en: "Alert LV" }
                }
            },
            {
                id: "tank",
                name_es: "Tanque",
                name_en: "Tank",
                quick_reference: {
                    assess: { es: "Eval Tanque", en: "Assess Tank" },
                    alerts: { es: "Alerta Tanque", en: "Alert Tank" }
                }
            },
            {
                id: "pipes",
                name_es: "Tuberías",
                name_en: "Pipes",
                quick_reference: {
                    assess: { es: "Eval Tubos", en: "Assess Pipes" },
                    alerts: { es: "Alerta Tubos", en: "Alert Pipes" }
                }
            }
        ]
    };
    
    const helpers = {
        escapeHTML: (str) => str,
        localize: (obj) => obj.es,
        translate: (key) => key
    };
    
    let typeErrorThrown1 = false;
    try {
        ProtocolRenderer.renderQuickReference(null, helpers);
    } catch (e) {
        if (e instanceof TypeError) typeErrorThrown1 = true;
    }
    
    let typeErrorThrown2 = false;
    try {
        ProtocolRenderer.renderQuickReference(protocol, null);
    } catch (e) {
        if (e instanceof TypeError) typeErrorThrown2 = true;
    }
    
    const originalJson = JSON.stringify(protocol);
    const htmlEs = ProtocolRenderer.renderQuickReference(protocol, helpers);
    const isUnmodified = JSON.stringify(protocol) === originalJson;
    
    const helpersEn = {
        escapeHTML: (str) => str,
        localize: (obj) => obj.en,
        translate: (key) => key
    };
    const htmlEn = ProtocolRenderer.renderQuickReference(protocol, helpersEn);
    
    const escapeHelpers = {
        escapeHTML: (str) => str.replace(/</g, "&lt;"),
        localize: (obj) => "<b>bold</b>",
        translate: (key) => key
    };
    const escapedHtml = ProtocolRenderer.renderQuickReference(protocol, escapeHelpers);
    
    const encodeBase64 = (value) => btoa(unescape(encodeURIComponent(value)));
    
    return {
        typeErrorThrown1,
        typeErrorThrown2,
        isUnmodified,
        htmlEsBase64: encodeBase64(htmlEs),
        htmlEnBase64: encodeBase64(htmlEn),
        escapedHtmlBase64: encodeBase64(escapedHtml)
    };
    """
    res = run_js_in_chrome(js_payload)
    assert res["success"] is True
    data = res["data"]
    
    assert data["typeErrorThrown1"] is True
    assert data["typeErrorThrown2"] is True
    assert data["isUnmodified"] is True
    
    html_es = base64.b64decode(data["htmlEsBase64"]).decode("utf-8")
    assert html_es.count("<article class=\"protocol-quick-card\"") == 1
    
    assert "Bomba" in html_es
    assert "Tanque" in html_es
    assert "Tuberías" in html_es
    
    assert "Eval VI" in html_es
    assert "Alerta VI" in html_es
    assert "label.protocol_quick_assess" in html_es
    assert "label.protocol_quick_alerts" in html_es
    
    html_en = base64.b64decode(data["htmlEnBase64"]).decode("utf-8")
    assert "Pump" in html_en
    assert "Tank" in html_en
    assert "Pipes" in html_en
    assert "Assess LV" in html_en
    assert "Alert LV" in html_en
    
    escaped_html = base64.b64decode(data["escapedHtmlBase64"]).decode("utf-8")
    assert "&lt;b>bold&lt;/b>" in escaped_html
    
    for key in ["undefined", "null", "[object Object]"]:
        assert key not in html_es
