import os
import json
import pytest

def test_left_atrium_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {"diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir"}
    for tid in target_ids:
        assert tid in ids

def test_left_atrium_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "diametro_ap_ai": 1,
        "volumen_ai_meas": 2,
        "lavi_meas": 3,
        "dilatacion_ai_class": 4,
        "la_strain_reservoir": 5
    }

    expected_related = {
        "diametro_ap_ai": ["ai_term", "plax"],
        "volumen_ai_meas": ["ai_term", "simpson_biplano"],
        "lavi_meas": ["lavi_term", "bsa", "indexed"],
        "dilatacion_ai_class": ["lavi_term", "ai_term"],
        "la_strain_reservoir": ["la_strain_reservoir_term", "speckle_tracking"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "left_atrium"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 5
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            bilingual_fields = [
                "measurement", "formula_or_method", "normal_values", "interpretation_limitations",
                "primary_window", "preferred_view", "modality", "acquisition_timing", "acquisition_key"
            ]
            for field in bilingual_fields:
                val = item[field]
                assert isinstance(val, dict), f"Campo '{field}' en '{i_id}' no es dict."
                assert "es" in val and "en" in val
                assert isinstance(val["es"], str) and val["es"].strip() != ""
                assert isinstance(val["en"], str) and val["en"].strip() != ""

            # aliases
            assert isinstance(item["aliases"], dict)
            assert "es" in item["aliases"] and "en" in item["aliases"]
            assert isinstance(item["aliases"]["es"], list)
            assert isinstance(item["aliases"]["en"], list)
            for a in item["aliases"]["es"] + item["aliases"]["en"]:
                assert isinstance(a, str) and a.strip() != ""

            # alternate_windows
            assert item["alternate_windows"] == {"es": [], "en": []}

            # No vulnerable / object Object
            for field in bilingual_fields:
                for lang in ["es", "en"]:
                    val = item[field][lang]
                    assert "[object Object]" not in val
                    assert "<script" not in val.lower()
                    assert "javascript:" not in val.lower()
                    assert "onerror=" not in val.lower()
                    assert "onclick=" not in val.lower()

def test_left_atrium_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 15. abbreviation permanece string para LAVI
    lavi = next(m for m in data if m["id"] == "lavi_meas")
    assert lavi["abbreviation"] == "LAVI"

    # 16. Las otras cuatro abreviaturas son objetos bilingües
    la_ap = next(m for m in data if m["id"] == "diametro_ap_ai")
    assert la_ap["abbreviation"] == {"es": "Diámetro AP de AI", "en": "LA AP diameter"}

    la_vol = next(m for m in data if m["id"] == "volumen_ai_meas")
    assert la_vol["abbreviation"] == {"es": "Volumen AI", "en": "LA volume"}

    dil = next(m for m in data if m["id"] == "dilatacion_ai_class")
    assert dil["abbreviation"] == {"es": "Dilatación AI", "en": "LA enlargement"}

    strain = next(m for m in data if m["id"] == "la_strain_reservoir")
    assert strain["abbreviation"] == {"es": "LA Strain Reservorio", "en": "LA reservoir strain"}

    # 17. units permanece string en las cinco
    assert la_ap["units"] == "mm"
    assert la_vol["units"] == "mL"
    assert lavi["units"] == "mL/m²"
    assert dil["units"] == "mL/m²"
    assert strain["units"] == "%"

def test_left_atrium_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    la_ap = next(m for m in data if m["id"] == "diametro_ap_ai")
    assert "27-40 mm" in la_ap["normal_values"]["es"]
    assert "27-40 mm" in la_ap["normal_values"]["en"]

    lavi = next(m for m in data if m["id"] == "lavi_meas")
    assert "≤34 mL/m²" in lavi["normal_values"]["es"]
    assert "≤34 mL/m²" in lavi["normal_values"]["en"]

    dil = next(m for m in data if m["id"] == "dilatacion_ai_class")
    assert "35-41" in dil["normal_values"]["es"]
    assert "42-48" in dil["normal_values"]["es"]
    assert ">48" in dil["normal_values"]["es"]
    assert "35-41" in dil["normal_values"]["en"]
    assert "42-48" in dil["normal_values"]["en"]
    assert ">48" in dil["normal_values"]["en"]

    strain = next(m for m in data if m["id"] == "la_strain_reservoir")
    assert "phase" in strain["formula_or_method"]["es"]
    assert "phase" in strain["formula_or_method"]["en"]
    assert ">18-23%" in strain["normal_values"]["es"]
    assert "≤18%" in strain["normal_values"]["es"]
    assert ">18-23%" in strain["normal_values"]["en"]
    assert "≤18%" in strain["normal_values"]["en"]

def test_previous_geometry_and_non_atrium_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 25. Las seis de lv_geometry siguen siendo bilingües
    geometry_ids = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas"}
    for item in data:
        if item["id"] in geometry_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # 26. No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
