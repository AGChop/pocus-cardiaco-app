import os
import json
import pytest

def test_mitral_valve_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {"area_mitral_planimetria", "area_mitral_pht", "gradiente_medio_mitral", "pht_meas", "relacion_vti_mitral_tsvi"}
    for tid in target_ids:
        assert tid in ids

def test_mitral_valve_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "area_mitral_planimetria": 1,
        "area_mitral_pht": 2,
        "gradiente_medio_mitral": 3,
        "pht_meas": 4,
        "relacion_vti_mitral_tsvi": 5
    }

    expected_related = {
        "area_mitral_planimetria": ["area_mitral_term", "psax"],
        "area_mitral_pht": ["area_mitral_term", "pht_term"],
        "gradiente_medio_mitral": ["gradiente_mitral_medio_term", "cw_doppler"],
        "pht_meas": ["pht_term"],
        "relacion_vti_mitral_tsvi": ["vti_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "mitral_valve"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 9
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

def test_mitral_valve_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 15. abbreviation permanece string para pht_meas
    pht = next(m for m in data if m["id"] == "pht_meas")
    assert pht["abbreviation"] == "PHT"

    # 16. Las otras cuatro abreviaturas son objetos bilingües
    amp = next(m for m in data if m["id"] == "area_mitral_planimetria")
    assert amp["abbreviation"] == {"es": "Área mitral por planimetría", "en": "Mitral valve area by planimetry"}

    am_pht = next(m for m in data if m["id"] == "area_mitral_pht")
    assert am_pht["abbreviation"] == {"es": "Área mitral por PHT", "en": "Mitral valve area by PHT"}

    gmm = next(m for m in data if m["id"] == "gradiente_medio_mitral")
    assert gmm["abbreviation"] == {"es": "Gradiente medio mitral", "en": "Mean mitral gradient"}

    rel = next(m for m in data if m["id"] == "relacion_vti_mitral_tsvi")
    assert rel["abbreviation"] == {"es": "VTI mitral/VTI TSVI", "en": "Mitral VTI/LVOT VTI"}

    # 17. units permanece string para cm², mmHg y ms
    assert amp["units"] == "cm²"
    assert am_pht["units"] == "cm²"
    assert gmm["units"] == "mmHg"
    assert pht["units"] == "ms"

    # 18. units es bilingüe y usa "dimensionless" en la relación VTI
    assert rel["units"] == {"es": "adimensional", "en": "dimensionless"}

def test_mitral_valve_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    amp = next(m for m in data if m["id"] == "area_mitral_planimetria")
    assert "4-6 cm²" in amp["normal_values"]["es"]
    assert "4-6 cm²" in amp["normal_values"]["en"]

    am_pht = next(m for m in data if m["id"] == "area_mitral_pht")
    assert "220 / PHT" in am_pht["formula_or_method"]["es"]
    assert "220 / PHT" in am_pht["formula_or_method"]["en"]
    assert ">4 cm²" in am_pht["normal_values"]["es"]
    assert ">4 cm²" in am_pht["normal_values"]["en"]

    gmm = next(m for m in data if m["id"] == "gradiente_medio_mitral")
    assert "<2-3 mmHg" in gmm["normal_values"]["es"]
    assert "<2-3 mmHg" in gmm["normal_values"]["en"]

    pht = next(m for m in data if m["id"] == "pht_meas")
    assert "<50-60 ms" in pht["normal_values"]["es"]
    assert "<50-60 ms" in pht["normal_values"]["en"]

    rel = next(m for m in data if m["id"] == "relacion_vti_mitral_tsvi")
    assert "<1,0-1,3" in rel["normal_values"]["es"]
    assert "<1.0-1.3" in rel["normal_values"]["en"]
    assert "VTI TSVI" in rel["formula_or_method"]["es"]
    assert "LVOT VTI" in rel["formula_or_method"]["en"]

def test_previous_migrated_sections_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 28. Las seis de lv_geometry siguen siendo bilingües
    geometry_ids = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas"}
    for item in data:
        if item["id"] in geometry_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # 29. Las cinco de left_atrium siguen siendo bilingües
    atrium_ids = {"diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir"}
    for item in data:
        if item["id"] in atrium_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # 30. No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
