import pytest
import os
import re

# Pruebas estáticas para validar que los acordeones de Glosario y Ventanas se implementaron correctamente

@pytest.fixture
def router_content():
    router_path = "assets/js/router.js"
    assert os.path.exists(router_path), f"No se encontró {router_path}"
    with open(router_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def css_content():
    css_path = "assets/css/styles.css"
    assert os.path.exists(css_path), f"No se encontró {css_path}"
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def sw_content():
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path), f"No se encontró {sw_path}"
    with open(sw_path, "r", encoding="utf-8") as f:
        return f.read()

def test_glossary_rendering_uses_details_and_summary(router_content):
    start = router_content.find("async renderGlossaryList")
    end = router_content.find("async renderGlossaryDetail")
    assert start != -1
    assert end != -1
    func_code = router_content[start:end]

    # Validar que usa details y summary con las clases correspondientes
    assert "details" in func_code
    assert "summary" in func_code
    assert "content-accordion" in func_code
    assert "glossary-accordion" in func_code
    assert "content-accordion-summary" in func_code
    assert "content-accordion-body" in func_code

    # 5. El Glosario conserva la ruta #/glosario/${item.id} o #/glosario/${item.id}
    assert "#/glosario/${item.id}" in func_code

    # 7. Existen los botones o acciones Detalle
    assert 'class="btn-card-action"' in func_code or "btn-card-action" in func_code
    assert "Detalle" in func_code

    # 8. Se conservan los selectores de Copiar y Favorito del Glosario
    assert "copy-m-t-${item.id}" in func_code
    assert "fav-t-${item.id}" in func_code

    # 13. No se utiliza el atributo open de forma predeterminada
    assert "open=" not in func_code
    assert " open " not in func_code
    assert 'open=""' not in func_code

def test_windows_rendering_uses_details_and_summary(router_content):
    start = router_content.find("async renderWindowsList")
    end = router_content.find("async renderWindowDetail")
    assert start != -1
    assert end != -1
    func_code = router_content[start:end]

    # Validar que usa details y summary con las clases correspondientes
    assert "details" in func_code
    assert "summary" in func_code
    assert "content-accordion" in func_code
    assert "window-accordion" in func_code
    assert "content-accordion-summary" in func_code
    assert "content-accordion-body" in func_code

    # 6. Ventanas conserva la ruta #/ventanas/${item.id}
    assert "#/ventanas/${item.id}" in func_code

    # 7. Existen los botones o acciones Detalle
    assert "Detalle" in func_code

    # 13. No se utiliza el atributo open de forma predeterminada
    assert "open=" not in func_code
    assert " open " not in func_code
    assert 'open=""' not in func_code

def test_styles_contains_accordion_classes(css_content):
    # 9. styles.css contiene .content-accordion-grid
    assert ".content-accordion-grid" in css_content
    # 10. styles.css contiene .content-accordion
    assert ".content-accordion" in css_content
    # 11. styles.css contiene .content-accordion-summary
    assert ".content-accordion-summary" in css_content
    # 12. Existe una regla responsive desde 768 px con dos columnas
    # Busquemos @media con min-width: 768px y repeat(2, minmax(0, 1fr)) o similar
    assert "@media" in css_content
    assert "768px" in css_content
    assert "repeat(2" in css_content

def test_service_worker_cache_and_contents(sw_content):
    # 14. service-worker.js contiene router.js y styles.css
    assert "router.js" in sw_content
    assert "styles.css" in sw_content

    # 15. La versión del caché fue incrementada a v11 o superior
    assert "pocus-cardiaco-cache-v11" in sw_content or "pocus-cardiaco-cache-v12" in sw_content or "pocus-cardiaco-cache-v13" in sw_content or "pocus-cardiaco-cache-v14" in sw_content or "pocus-cardiaco-cache-v15" in sw_content or "pocus-cardiaco-cache-v16" in sw_content
