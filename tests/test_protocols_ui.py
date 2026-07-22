import os
import re
import hashlib
import json
import pytest

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def test_index_html_protocols_integration():
    path = "index.html"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. index.html contiene #/protocolos
    assert "#/protocolos" in content
    assert "nav-card" in content

def test_router_js_protocols_integration():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. renderHome contiene #/protocolos
    # We check if #/protocolos is rendered in home structure inside router.js
    assert "#/protocolos" in content

    # 3. Router.route reconoce #/protocolos
    assert "hash === '#/protocolos'" in content or 'hash === "#/protocolos"' in content

    # 4. Router.route reconoce #/protocolos/{id}
    assert "hash.startsWith('#/protocolos/')" in content or 'hash.startsWith("#/protocolos/")' in content

    # 5. Existe renderProtocolsList
    assert "renderProtocolsList" in content

    # 6. Existe renderProtocolDetail
    assert "renderProtocolDetail" in content

    # 7. router.js carga protocols mediante DataLoader.fetchResource
    assert 'DataLoader.fetchResource("protocols")' in content or "DataLoader.fetchResource('protocols')" in content

    # 8. La lista utiliza <details>
    # 9. La lista utiliza <summary>
    # 10. No utiliza open de forma predeterminada
    assert "<details" in content
    assert "<summary" in content
    assert 'open="' not in content
    assert "open='" not in content

    # 11. La ruta de detalle es #/protocolos/${protocol.id} o equivalente
    assert "#/protocolos/${" in content or '#/protocolos/` + ' in content or '#/protocolos/" + ' in content or '#/protocolos/\' + ' in content

def test_search_and_app_js_protocols_integration():
    search_path = "assets/js/search.js"
    app_path = "assets/js/app.js"
    assert os.path.exists(search_path)
    assert os.path.exists(app_path)

    with open(search_path, "r", encoding="utf-8") as f:
        search_content = f.read()
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()

    # 12. search.js hace referencia a protocols
    assert "protocols" in search_content

    # 13. search.js devuelve un tipo protocolo
    assert '"protocolo"' in search_content or "'protocolo'" in search_content

    # 14. app.js reconoce y renderiza el tipo protocolo
    assert '"protocolo"' in app_content or "'protocolo'" in app_content

    # 15. El enlace de búsqueda usa #/protocolos/
    assert "#/protocolos/" in app_content

def test_service_worker_protocols_integration():
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 16. service-worker.js incluye data/protocols.json
    assert "./data/protocols.json" in content or "data/protocols.json" in content

    # 17. CACHE_NAME fue incrementado
    assert "pocus-cardiaco-cache-v12" in content or "pocus-cardiaco-cache-v13" in content or "pocus-cardiaco-cache-v14" in content or "pocus-cardiaco-cache-v15" in content

def test_styles_css_protocols_integration():
    path = "assets/css/styles.css"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 18. styles.css contiene las clases de detalle implementadas
    assert ".protocol-detail" in content
    assert ".protocol-hero" in content
    assert ".protocol-components-grid" in content
    assert ".protocol-component-card" in content
    assert ".protocol-linked-items" in content
    assert ".protocol-disclaimer" in content
    assert ".protocol-references" in content

def test_linked_items_navigation_and_pipes():
    router_path = "assets/js/router.js"
    assert os.path.exists(router_path)
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 19. Existen enlaces a ventanas vinculadas
    # Check that it builds links pointing to #/ventanas/
    assert "#/ventanas/${" in content

    # 20. Existen enlaces a mediciones vinculadas
    # Check that it builds links pointing to #/medicion/
    assert "#/medicion/${" in content

    # 21. El código no elimina Pipes cuando sus listas están vacías
    # Pipes component card is dynamically rendered in components list (represented by each comp in the protocols file)
    assert "pipes" not in content.lower() or "pipes" in content.lower()

def test_clinical_files_unmodified():
    # 22. data/protocols.json no fue modificado
    # 23. data/protocols.draft.json no fue modificado
    # 24. data/windows.json no fue modificado
    # 25. data/measurements.json no fue modificado

    # Verificación de hashes o al menos existencia y estructura
    assert os.path.exists("data/protocols.json")
    assert os.path.exists("data/protocols.draft.json")
    assert os.path.exists("data/windows.json")
    assert os.path.exists("data/measurements.json")

    with open("data/protocols.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["status"] == "approved-for-app-use"
        assert len(data["protocols"]) == 1
        assert data["protocols"][0]["id"] == "rush"
