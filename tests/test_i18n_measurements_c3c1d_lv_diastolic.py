import os
import json
import pytest

def test_lv_diastolic_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {
        "onda_e_mitral", "onda_a_mitral", "relacion_e_a", "tiempo_desaceleracion_e", "ivrt_meas",
        "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "velocidad_it_diastology",
        "lavi_diastology", "la_strain_diastology"
    }
    for tid in target_ids:
        assert tid in ids

def test_lv_diastolic_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "onda_e_mitral": 1,
        "onda_a_mitral": 2,
        "relacion_e_a": 3,
        "tiempo_desaceleracion_e": 4,
        "ivrt_meas": 5,
        "e_septal_meas": 6,
        "e_lateral_meas": 7,
        "relacion_e_e_promedio": 8,
        "velocidad_it_diastology": 9,
        "lavi_diastology": 10,
        "la_strain_diastology": 11
    }

    expected_related = {
        "onda_e_mitral": ["onda_e_term", "pw_doppler"],
        "onda_a_mitral": ["onda_a_term", "pw_doppler"],
        "relacion_e_a": ["relacion_e_a_term", "onda_e_term", "onda_a_term"],
        "tiempo_desaceleracion_e": ["tiempo_desaceleracion_e_term", "onda_e_term"],
        "ivrt_meas": ["ivrt_term"],
        "e_septal_meas": ["e_prima_term", "tdi"],
        "e_lateral_meas": ["e_prima_term", "tdi"],
        "relacion_e_e_promedio": ["relacion_e_e_term", "onda_e_term", "e_prima_term"],
        "velocidad_it_diastology": ["it_term", "cw_doppler"],
        "lavi_diastology": ["lavi_term", "bsa", "indexed"],
        "la_strain_diastology": ["la_strain_reservoir_term", "speckle_tracking"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "lv_diastolic"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 6
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

def test_lv_diastolic_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 15. abbreviation permanece string para E/A, DT, IVRT, LAVI
    for mid in ["relacion_e_a", "tiempo_desaceleracion_e", "ivrt_meas", "lavi_diastology"]:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["abbreviation"], str)

    # 16. Las otras siete abreviaturas son objetos bilingües
    bilingual_abbrs = {"onda_e_mitral", "onda_a_mitral", "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "velocidad_it_diastology", "la_strain_diastology"}
    for mid in bilingual_abbrs:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["abbreviation"], dict)
        assert "es" in item["abbreviation"] and "en" in item["abbreviation"]

    # 17. units permanece string en las indicadas
    string_units = ["onda_e_mitral", "onda_a_mitral", "tiempo_desaceleracion_e", "ivrt_meas", "e_septal_meas", "e_lateral_meas", "velocidad_it_diastology", "lavi_diastology", "la_strain_diastology"]
    for mid in string_units:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["units"], str)

    # 18. Solo las dos unidades "adimensional" son bilingües
    for mid in ["relacion_e_a", "relacion_e_e_promedio"]:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["units"], dict)
        assert item["units"]["es"] == "adimensional"
        assert item["units"]["en"] == "dimensionless"

def test_lv_diastolic_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 21. La palabra española "function" permanece en la_strain_diastology
    la_strain = next(m for m in data if m["id"] == "la_strain_diastology")
    assert "function" in la_strain["normal_values"]["es"]

    # 22. e' con apóstrofo curvo permanece en relacion_e_e_promedio
    prom = next(m for m in data if m["id"] == "relacion_e_e_promedio")
    assert "e’" in prom["acquisition_key"]["es"]

    # 23-25. Doppler modalities check
    e = next(m for m in data if m["id"] == "onda_e_mitral")
    assert "Doppler pulsado" in e["modality"]["es"]
    assert "Pulsed-wave Doppler" in e["modality"]["en"]

    e_sept = next(m for m in data if m["id"] == "e_septal_meas")
    assert "Doppler tisular pulsado" in e_sept["modality"]["es"]
    assert "Pulsed-wave tissue Doppler" in e_sept["modality"]["en"]

    it = next(m for m in data if m["id"] == "velocidad_it_diastology")
    assert "Doppler continuo" in it["modality"]["es"]
    assert "continuous-wave doppler" in it["modality"]["en"].lower()

def test_previous_migrated_sections_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 31. Las 16 anteriores siguen siendo bilingües
    all_prev = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas", "diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir", "area_mitral_planimetria", "area_mitral_pht", "gradiente_medio_mitral", "pht_meas", "relacion_vti_mitral_tsvi"}
    for item in data:
        if item["id"] in all_prev:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # 32. No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
