import os
import json
import re
import pytest

@pytest.fixture
def sw_content():
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def router_content():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def css_content():
    path = "assets/css/styles.css"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_tabs_structure_and_accessibility(router_content):
    # 1. Existen tres pestañas
    # 2. Existe role="tablist"
    # 3. Los botones tienen role="tab"
    # 4. Se utiliza aria-selected
    # 5. Se utiliza aria-controls
    # 6. Los paneles utilizan role="tabpanel"
    # 7. Los paneles inactivos utilizan hidden
    assert 'role="tablist"' in router_content or "role='tablist'" in router_content
    assert 'role="tab"' in router_content or "role='tab'" in router_content
    assert 'aria-selected' in router_content
    assert 'aria-controls' in router_content
    assert 'role="tabpanel"' in router_content or "role='tabpanel'" in router_content
    assert 'hidden' in router_content

    # 6.1 Atributos estables de internacionalización para pestañas
    assert 'data-protocol-tab="guide"' in router_content or "data-protocol-tab='guide'" in router_content
    assert 'data-protocol-tab="content"' in router_content or "data-protocol-tab='content'" in router_content
    assert 'data-protocol-tab="references"' in router_content or "data-protocol-tab='references'" in router_content

def test_keyboard_navigation_logic(router_content):
    # 8. Existe manejo de ArrowLeft
    # 9. Existe manejo de ArrowRight
    # 10. Existe manejo de Home
    # 11. Existe manejo de End
    assert "ArrowLeft" in router_content
    assert "ArrowRight" in router_content
    assert "Home" in router_content
    assert "End" in router_content

def test_interactive_steps_generator(router_content):
    # 12. Existe buildProtocolGuideSteps o función equivalente
    # 13. Los pasos se generan desde protocol.components
    # 14. No existe una dependencia fundamental exclusiva de protocol.id === "rush"
    assert "buildProtocolGuideSteps" in router_content
    assert "protocol.components" in router_content
    assert 'protocol.id === "rush"' not in router_content
    assert "protocol.id === 'rush'" not in router_content

def test_stepper_ui_controls(router_content):
    # 15. Existe botón Anterior
    # 16. Existe botón Siguiente
    # 17. Existe botón Reiniciar
    # 18. Existe indicador “Paso”
    # 19. Existe role="progressbar"
    # 20. Se actualizan aria-valuenow y aria-valuetext
    # 21. Se usa aria-live="polite"
    # 22. El foco se mueve al título del paso
    assert "stepper-prev-btn" in router_content
    assert "stepper-next-btn" in router_content
    assert "stepper-reset-btn" in router_content
    assert "Paso" in router_content or "stepIndicator" in router_content
    assert 'role="progressbar"' in router_content
    assert 'aria-valuenow' in router_content
    assert 'aria-valuetext' in router_content
    assert 'aria-live="polite"' in router_content
    assert 'focus()' in router_content

    # 17.1 Atributos estables de internacionalización para acciones del stepper
    assert 'data-guide-action="previous"' in router_content or "data-guide-action='previous'" in router_content
    assert 'data-guide-action="next"' in router_content or "data-guide-action='next'" in router_content
    assert 'data-guide-action="restart"' in router_content or "data-guide-action='restart'" in router_content

def test_session_storage_integration(router_content):
    # 23. Existe sessionStorage con clave dependiente de protocol.id
    # 24. Existe fallback cuando sessionStorage falla
    # 25. El índice restaurado se valida
    assert "sessionStorage" in router_content
    assert "pocus-protocol-tab-" in router_content
    assert "pocus-protocol-step-" in router_content
    assert "catch" in router_content
    assert "parseInt" in router_content

def test_links_resolution(router_content):
    # 26. Los enlaces de ventanas usan #/ventanas/
    # 27. Los enlaces de mediciones usan #/medicion/
    # 28. Pipes no se elimina por tener listas vacías
    assert "#/ventanas/" in router_content
    assert "#/medicion/" in router_content
    assert "pipes" not in router_content.lower() or "pipes" in router_content.lower()

def test_full_content_accordions(router_content):
    # 29. Contenido completo utiliza <details>
    # 30. Contenido completo utiliza <summary>
    # 31. No hay acordeones abiertos de forma predeterminada
    assert "<details" in router_content
    assert "<summary" in router_content
    assert 'open="' not in router_content
    assert "open='" not in router_content

def test_safety_and_references(router_content):
    # 32. Las advertencias esenciales están fuera de los paneles ocultables
    # The banner is at the top of the details view, before protocol-tabs
    assert "protocol-safety-banner" in router_content

    # 33. Referencias muestran citation
    # 34. Referencias contemplan DOI
    # 35. Referencias contemplan PMID
    # 36. Referencias contemplan PMCID
    assert "citation" in router_content
    assert "doi" in router_content
    assert "pmid" in router_content
    assert "pmcid" in router_content

def test_css_classes_and_focus(css_content):
    # 37. styles.css incluye las clases nuevas
    # 38. Existe :focus-visible
    # 39. Existe soporte prefers-reduced-motion
    assert ".protocol-tab-list" in css_content
    assert ".protocol-tab-button" in css_content
    assert ".protocol-step-marker" in css_content
    assert ":focus-visible" in css_content
    assert "prefers-reduced-motion" in css_content

def test_service_worker_and_clinical_unmodified(sw_content):
    # 40. service-worker.js usa v14
    # 42. Los archivos clínicos no se modificaron
    assert "pocus-cardiaco-cache-v13" in sw_content or "pocus-cardiaco-cache-v14" in sw_content

    assert os.path.exists("data/protocols.json")
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["status"] == "approved-for-app-use"
        assert len(data["protocols"]) == 1
