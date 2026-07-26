import os
import json
import re
import pytest

def test_catalog_minimum_pocus_set():
    path = "data/minimum_pocus_set.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Exactly 10 items
    assert len(data) == 10

    # IDs 1 to 10
    ids = [item["id"] for item in data]
    assert ids == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # source_page == 11 for all
    for item in data:
        assert item["source_page"] == 11
        assert isinstance(item["skill"], dict)
        assert "es" in item["skill"]
        assert "en" in item["skill"]
        assert isinstance(item["skill"]["es"], str) and item["skill"]["es"].strip() != ""
        assert isinstance(item["skill"]["en"], str) and item["skill"]["en"].strip() != ""

    # Exact strings ES
    es_expected = {
        1: "FEVI visual y, cuando sea posible, Simpson biplano.",
        2: "VTI del TSVI, volumen sistólico, gasto cardiaco e índice cardiaco.",
        3: "Tamaño y función del VD: relación VD/VI, TAPSE, s' y FAC.",
        4: "Velocidad de insuficiencia tricuspídea y estimación de PASP.",
        5: "VCI y estimación de presión auricular derecha.",
        6: "E/A, e', E/e' y LAVI para evaluación diastólica integrada.",
        7: "Velocidad máxima y gradientes de la válvula aórtica.",
        8: "Búsqueda y graduación integrada de insuficiencias valvulares.",
        9: "Derrame pericárdico y signos ecográficos de taponamiento.",
        10: "Alteraciones segmentarias de contractilidad y respuesta dinámica del VTI."
    }

    en_expected = {
        1: "Visual LVEF and, when possible, biplane Simpson.",
        2: "LVOT VTI, stroke volume, cardiac output, and cardiac index.",
        3: "RV size and function: RV/LV ratio, TAPSE, s′, and FAC.",
        4: "Tricuspid regurgitation velocity and PASP estimation.",
        5: "IVC and right atrial pressure estimation.",
        6: "E/A, e′, E/e′, and LAVI for integrated diastolic assessment.",
        7: "Aortic valve peak velocity and gradients.",
        8: "Detection and integrated grading of valvular regurgitation.",
        9: "Pericardial effusion and echocardiographic signs of tamponade.",
        10: "Regional wall-motion abnormalities and dynamic VTI response."
    }

    for item in data:
        item_id = item["id"]
        assert item["skill"]["es"] == es_expected[item_id]
        assert item["skill"]["en"] == en_expected[item_id]


def test_translations_keys():
    path = "data/translations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["translations"]

    expected_keys = {
        "label.minimum_set_desc": {
            "es": "Habilidades y destrezas ecográficas básicas que el operador POCUS debe dominar para una evaluación cardiaca inicial completa.",
            "en": "Basic ultrasound skills and competencies that the POCUS operator should master for a complete initial cardiac assessment."
        },
        "label.integration_principle": {
            "es": "Principio de integración",
            "en": "Integration principle"
        },
        "label.integration_principle_text": {
            "es": "La función diastólica, la función del VD, la hipertensión pulmonar, la severidad valvular y el taponamiento no deben definirse mediante una sola medición aislada.",
            "en": "Diastolic function, RV function, pulmonary hypertension, valvular severity, and tamponade should not be defined by a single isolated measurement."
        }
    }

    for key, val in expected_keys.items():
        assert key in data
        assert data[key]["es"] == val["es"]
        assert data[key]["en"] == val["en"]


def test_router_render_minimum_set():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate the renderMinimumSet function content
    match = re.search(r"renderMinimumSet\(container\)\s*\{(.*?)\n\s*\},", content, re.DOTALL)
    assert match, "Could not find renderMinimumSet in router.js"
    func_body = match.group(1)

    # 1. Uses I18n.localize(item.skill)
    assert "I18n.localize" in func_body
    assert "item.skill" in func_body
    assert "${item.skill}" not in func_body

    # 2. Defines escapeHTML locally
    assert "const escapeHTML =" in func_body

    # 3. Uses translation keys
    assert 'label.minimum_set_desc' in func_body
    assert 'label.integration_principle' in func_body
    assert 'label.integration_principle_text' in func_body

    # 4. Old paragraphs are gone
    assert "Habilidades y destrezas ecográficas básicas que el operador POCUS debe dominar" not in func_body
    assert "La función diastólica, la función del VD, la hipertensión pulmonar, la severidad valvular" not in func_body


def test_protection_clinical_data():
    # Measurements count
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101
    for m in measurements:
        assert isinstance(m["measurement"], dict)
        assert "es" in m["measurement"]
        assert "en" in m["measurement"]

    # Protocols count
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols = json.load(f)["protocols"]
    assert len(protocols) == 1
    assert protocols[0]["id"] == "rush"

    # Locus Pocus brand intact
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)["translations"]
    assert translations["app.name"]["es"] == "LOCUS POCUS"
    assert translations["app.name"]["en"] == "LOCUS POCUS"

    with open("index.html", "r", encoding="utf-8") as f:
        index_content = f.read()
    assert "LOCUS POCUS" in index_content

def test_service_worker_cache_revision_e1a():
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v17-c3d1-brand1-e1a" in content
    assert "./assets/js/router.js" in content
    assert "./data/translations.json" in content
    assert "./data/minimum_pocus_set.json" in content
    assert "locus-pocus-icon-192.png" in content
    # Verify cache-first behavior is still present
    assert "caches.match" in content

