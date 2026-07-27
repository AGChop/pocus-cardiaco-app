import os
import json

def test_unit_warnings_json_validity_and_bilingual():
    path = "data/unit_warnings.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 11

    expected_spanish_parameters = [
        "Masa del VI",
        "Área del TSVI",
        "Volumen sistólico",
        "Gasto cardiaco",
        "Bernoulli",
        "PISA / EROA",
        "RVP ecográfica",
        "Strain",
        "Señal Doppler",
        "VCI en Ventilación",
        "Verificación general"
    ]

    expected_english_translations = {
        "Masa del VI": {
            "parameter": "LV mass",
            "warning": "LVIDd, IVSd, and PWTd must be in cm before applying the formula."
        },
        "Área del TSVI": {
            "parameter": "LVOT area",
            "warning": "The diameter must be in cm. The resulting area is in cm²."
        },
        "Volumen sistólico": {
            "parameter": "Stroke volume",
            "warning": "Area in cm² x VTI in cm = cm³, equivalent to mL."
        },
        "Gasto cardiaco": {
            "parameter": "Cardiac output",
            "warning": "SV in mL x HR / 1000 = L/min."
        },
        "Bernoulli": {
            "parameter": "Bernoulli",
            "warning": "With velocity in m/s, ΔP = 4V² yields mmHg."
        },
        "PISA / EROA": {
            "parameter": "PISA / EROA",
            "warning": "The radius must be in cm, and velocities must use consistent units."
        },
        "RVP ecográfica": {
            "parameter": "Echocardiographic PVR",
            "warning": "RVOT VTI must be used, not LVOT VTI."
        },
        "Strain": {
            "parameter": "Strain",
            "warning": "Values are negative: a less negative value indicates reduced deformation."
        },
        "Señal Doppler": {
            "parameter": "Doppler signal",
            "warning": "Do not use an incomplete or misaligned Doppler signal."
        },
        "VCI en Ventilación": {
            "parameter": "IVC during mechanical ventilation",
            "warning": "Do not extrapolate IVC criteria from spontaneous breathing to mechanical ventilation."
        },
        "Verificación general": {
            "parameter": "General verification",
            "warning": "Confirm the view, unit, cardiac cycle timing, and Doppler alignment before accepting a result."
        }
    }

    for idx, item in enumerate(data):
        assert "parameter" in item
        assert "warning" in item
        assert "source_page" in item

        # source_page es int y es 3
        assert isinstance(item["source_page"], int)
        assert item["source_page"] == 3

        # Estructura del objeto bilingüe
        p = item["parameter"]
        w = item["warning"]
        assert isinstance(p, dict)
        assert isinstance(w, dict)
        assert "es" in p and "en" in p
        assert "es" in w and "en" in w

        # Conserva orden de textos españoles
        es_param = p["es"]
        assert es_param == expected_spanish_parameters[idx]

        # Validaciones de traducción inglesa exacta
        ref = expected_english_translations[es_param]
        assert p["en"] == ref["parameter"]
        assert w["en"] == ref["warning"]

        # Validaciones no XSS
        for lang in ["es", "en"]:
            assert "<script" not in p[lang].lower()
            assert "javascript:" not in p[lang].lower()
            assert "onerror=" not in p[lang].lower()
            assert "onclick=" not in p[lang].lower()
            assert "<script" not in w[lang].lower()
            assert "javascript:" not in w[lang].lower()
            assert "onerror=" not in w[lang].lower()
            assert "onclick=" not in w[lang].lower()

def test_router_js_unit_warnings():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # router utiliza I18n.localize y escapeHTML
    assert "I18n.localize(w.parameter)" in content
    assert "I18n.localize(w.warning)" in content
    assert "escapeHTML(parameter)" in content
    assert "escapeHTML(warning)" in content
    assert "escapeHTML(w.source_page)" in content

    # El título no tiene Frecuentes concatenado
    assert '<h2>${I18n.translate("label.unit_warnings")}</h2>' in content

    # Se conservan las etiquetas de origen y nav.home
    assert 'I18n.translate("label.origen")' in content
    assert 'I18n.translate("nav.home")' in content

def test_unmodified_files_c3b():
    assert os.path.exists("data/translations.json")
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/windows.json")
    assert os.path.exists("assets/js/app.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/i18n.js")
    assert os.path.exists("service-worker.js")
