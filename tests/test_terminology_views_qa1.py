import os
import json
import re

def test_qa1_translation_keys_corrected():
    # 1. Los valores exactos es/en de las siete claves corregidas.
    path = "data/translations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    translations = data.get("translations", {})
    
    # 1. nav.windows
    assert translations["nav.windows"]["es"] == "Vistas ecocardiográficas"
    assert translations["nav.windows"]["en"] == "Echocardiographic Views"
    
    # 2. label.window
    assert translations["label.window"]["es"] == "Vista"
    assert translations["label.window"]["en"] == "View"
    
    # 3. label.clinical_window_label
    assert translations["label.clinical_window_label"]["es"] == "Vistas vinculadas"
    assert translations["label.clinical_window_label"]["en"] == "Linked views"
    
    # 4. error.windows_load_title
    assert translations["error.windows_load_title"]["es"] == "Error al cargar las vistas"
    assert translations["error.windows_load_title"]["en"] == "Error loading echocardiographic views"
    
    # 5. error.windows_load_text
    assert translations["error.windows_load_text"]["es"] == "Lo sentimos, no pudimos cargar la lista de vistas ecocardiográficas. Por favor, intente nuevamente más tarde."
    assert translations["error.windows_load_text"]["en"] == "Sorry, we could not load the list of echocardiographic views. Please try again later."
    
    # 6. error.window_detail_load_text
    assert translations["error.window_detail_load_text"]["es"] == "No se pudo cargar la información de la vista ecocardiográfica."
    assert translations["error.window_detail_load_text"]["en"] == "The echocardiographic view information could not be loaded."
    
    # 7. nav.back_to_windows
    assert translations["nav.back_to_windows"]["es"] == "Volver a Vistas"
    assert translations["nav.back_to_windows"]["en"] == "Back to Views"


def test_qa1_distinction_preserved():
    # 2. La preservación exacta de las claves que describen verdaderas ventanas acústicas o campos de adquisición.
    path = "data/translations.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    translations = data.get("translations", {})
    
    assert translations["label.primary_window"]["es"] == "Ventana Primaria"
    assert translations["label.primary_window"]["en"] == "Primary Window"
    
    assert translations["label.alternate_windows"]["es"] == "Ventanas Alternativas"
    assert translations["label.alternate_windows"]["en"] == "Alternate Windows"
    
    assert "ventanas de adquisición" in translations["label.glossary_desc"]["es"]
    assert "acquisition windows" in translations["label.glossary_desc"]["en"]
    
    assert translations["label.preferred_view"]["es"] == "Vista Preferida"
    assert translations["label.preferred_view"]["en"] == "Preferred View"
    
    assert translations["label.clinical_views_label"]["es"] == "Vistas sugeridas"
    assert translations["label.clinical_views_label"]["en"] == "Suggested views"


def test_qa1_windows_json_intact():
    # 3. data/windows.json conserva exactamente 12 registros, conserva IDs y estructura,
    # y cada window.en continúa usando la terminología "view" sin modificar registros clínicos.
    path = "data/windows.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        windows = json.load(f)
        
    assert len(windows) == 12
    
    expected_ids = [
        "plax",
        "psax",
        "a4c",
        "rv_focused_a4c",
        "a2c",
        "a3c",
        "a5c",
        "subcostal_4c",
        "subcostal_ivc",
        "rv_inflow",
        "right_parasternal",
        "suprasternal",
    ]
    
    assert [item["id"] for item in windows] == expected_ids
    
    for item in windows:
        assert "window" in item
        assert "es" in item["window"]
        assert "en" in item["window"]
        assert "view" in item["window"]["en"].lower()
        assert "typical_probe_position" in item
        assert "favored_structures" in item
        
    # Verify no clinical record was modified (check a sample)
    plax = next(w for w in windows if w["id"] == "plax")
    assert plax["abbreviation"] == "PLAX"
    assert "Borde esternal izquierdo" in plax["typical_probe_position"]["es"]


def test_qa1_architecture_intact():
    # 4. Arquitectura interna intacta.
    # - La ruta continúa siendo #/ventanas
    # - DataLoader.getWindows continúa presente
    # - renderWindowsList y renderWindowDetail conservan sus nombres
    # - El campo item.window continúa utilizándose
    # - linked_window_ids no cambia
    
    # Check data-loader.js for getWindows
    with open("assets/js/data-loader.js", "r", encoding="utf-8") as f:
        dl_content = f.read()
    assert "async getWindows()" in dl_content
    
    # Check router.js
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        router_content = f.read()
        
    assert "hash === '#/ventanas'" in router_content or "hash.startsWith('#/ventanas/')" in router_content
    assert "async renderWindowsList" in router_content
    assert "async renderWindowDetail" in router_content
    assert "item.window" in router_content or "window.es" in router_content or "window.en" in router_content
    assert "linked_window_ids" in router_content
    
    # Check that windows.json is loaded
    assert "data/windows.json" not in router_content # must load via data-loader
    assert "DataLoader.getWindows()" in router_content


def test_qa1_index_html_updates():
    # 5. index.html fallback, i18n, href y meta tags.
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # fallback visible
    assert '<h2 data-i18n="nav.windows">Vistas ecocardiográficas</h2>' in content
    
    # maintains i18n and href
    assert 'data-i18n="nav.windows"' in content
    assert 'href="#/ventanas"' in content
    
    # new social description
    new_desc = "Glosario, mediciones, vistas y protocolos de POCUS cardíaco."
    assert f'content="{new_desc}"' in content
    assert content.count(new_desc) == 2
    
    # old social description no longer present
    old_desc = "Glosario, mediciones, ventanas y protocolos de POCUS cardíaco."
    assert old_desc not in content


def test_qa1_service_worker():
    # 6. Service worker updates.
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "const CACHE_NAME = 'pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1';" in content
    assert "'./index.html'" in content or "'./'" in content
    assert "'./data/translations.json'" in content
    assert "'./data/windows.json'" in content
    
    # strategy remains
    assert "self.addEventListener('install'" in content
    assert "self.addEventListener('fetch'" in content


def test_qa1_protection_and_keys():
    # 7. Protecciones generales.
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101
    
    with open("data/minimum_pocus_set.json", "r", encoding="utf-8") as f:
        min_set = json.load(f)
    assert len(min_set) == 10
    
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = data.get("translations", {})
    
    assert translations["label.cutoff_point"]["en"] == "Cutoff value"
    assert translations["label.abbreviations_list_title"]["en"] == "Abbreviations"
