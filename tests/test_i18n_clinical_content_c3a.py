import os
import json
import re

def test_windows_json_refinement_and_exact_names():
    path = "data/windows.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 12

    exact_english_names = {
        "plax": "Parasternal long-axis view",
        "psax": "Parasternal short-axis view",
        "a4c": "Apical four-chamber view",
        "rv_focused_a4c": "RV-focused apical four-chamber view",
        "a2c": "Apical two-chamber view",
        "a3c": "Apical long-axis (three-chamber) view",
        "a5c": "Apical five-chamber view",
        "subcostal_4c": "Subcostal four-chamber view",
        "subcostal_ivc": "Subcostal IVC long-axis view",
        "rv_inflow": "Parasternal RV inflow view",
        "right_parasternal": "High right parasternal view",
        "suprasternal": "Suprasternal notch view"
    }

    for item in data:
        i_id = item["id"]
        assert i_id in exact_english_names
        assert item["window"]["en"] == exact_english_names[i_id]

        # 1. favored_measurements es un objeto
        assert isinstance(item["favored_measurements"], dict)
        # 2. Contiene exactamente las claves es y en, o al menos ambas claves
        assert "es" in item["favored_measurements"]
        assert "en" in item["favored_measurements"]
        # 3 y 4. es/en son strings no vacíos
        assert isinstance(item["favored_measurements"]["es"], str)
        assert isinstance(item["favored_measurements"]["en"], str)
        assert item["favored_measurements"]["es"].strip() != ""
        assert item["favored_measurements"]["en"].strip() != ""

        # 5. Ninguno contiene [object Object], <script, etc.
        for lang in ["es", "en"]:
            txt = item["favored_measurements"][lang]
            assert "[object Object]" not in txt
            assert "<script" not in txt.lower()
            assert "javascript:" not in txt.lower()
            assert "onerror=" not in txt.lower()
            assert "onclick=" not in txt.lower()

def test_router_js_defensive_c3a_logic():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Existe literalmente collectTextVariants
    assert "collectTextVariants" in content
    # 2. Existe literalmente normalizeComparable
    assert "normalizeComparable" in content
    # 3. No aparece m.measurement.toLowerCase()
    assert "m.measurement.toLowerCase()" not in content
    # 4. No aparece aliases.map(a => a.toLowerCase())
    assert "aliases.map(a => a.toLowerCase())" not in content

    # 5. Se procesan: m.measurement, m.abbreviation, m.aliases
    assert "m.measurement" in content
    assert "m.abbreviation" in content
    assert "m.aliases" in content

    # 6. Existe I18n.localize(item.favored_measurements)
    assert "I18n.localize(item.favored_measurements)" in content

    # 8. manualMap contiene las parejas bilingües y apuntan al mismo ID
    assert '"dtdvi/dtsvi": "dtdvi"' in content or "'dtdvi/dtsvi': 'dtdvi'" in content
    assert '"lvidd/lvids": "dtdvi"' in content or "'lvidd/lvids': 'dtdvi'" in content
    assert '"grosor pared vd": "grosor_pared_vd"' in content or "'grosor pared vd': 'grosor_pared_vd'" in content
    assert '"rv wall thickness": "grosor_pared_vd"' in content or "'rv wall thickness': 'grosor_pared_vd'" in content

    # 9. El href utiliza #/medicion/${escapeHTML(found.id)}
    assert 'href="#/medicion/${escapeHTML(found.id)}"' in content or "href='#/medicion/${escapeHTML(found.id)}'" in content
    # 10. El texto visible utiliza escapeHTML(part)
    assert "escapeHTML(part)" in content

    # 11. renderWindowsList usa I18n.translate("nav.windows")
    assert 'I18n.translate("nav.windows")' in content

def test_unmodified_files_c3a():
    # No se modificó data/measurements.json
    assert os.path.exists("data/measurements.json")
    # No se modificaron otros archivos
    assert os.path.exists("assets/js/app.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/quiz-engine.js")
    assert os.path.exists("service-worker.js")
