import os
import json
import pytest

def test_stroke_volume_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {
        "area_tsvi_meas", "vti_tsvi_meas", "volumen_sistolico_meas", "sv_index",
        "gasto_cardiaco_meas", "cardiac_index", "plr_vti_change", "rvs_meas", "irvs_meas"
    }
    for tid in target_ids:
        assert tid in ids

def test_stroke_volume_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "area_tsvi_meas": 1,
        "vti_tsvi_meas": 2,
        "volumen_sistolico_meas": 3,
        "sv_index": 4,
        "gasto_cardiaco_meas": 5,
        "cardiac_index": 6,
        "plr_vti_change": 7,
        "rvs_meas": 8,
        "irvs_meas": 9
    }

    expected_related = {
        "area_tsvi_meas": ["area_tsvi_term", "tsvi_term"],
        "vti_tsvi_meas": ["vti_term", "tsvi_term", "pw_doppler"],
        "volumen_sistolico_meas": ["volumen_sistolico_term", "area_tsvi_term", "vti_term"],
        "sv_index": ["indice_volumen_sistolico_term", "bsa", "indexed"],
        "gasto_cardiaco_meas": ["gasto_cardiaco_term", "volumen_sistolico_term"],
        "cardiac_index": ["indice_cardiaco_term", "bsa", "indexed"],
        "plr_vti_change": ["plr_term", "vti_term"],
        "rvs_meas": ["rvs_term", "pam_term", "presion_ad_term", "gasto_cardiaco_term"],
        "irvs_meas": ["irvs_term", "pam_term", "presion_ad_term", "indice_cardiaco_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "stroke_volume_output"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 5
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            bilingual_fields = [
                "measurement", "abbreviation", "formula_or_method", "normal_values", "interpretation_limitations",
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

            # alternate_windows except vti_tsvi_meas
            if i_id != "vti_tsvi_meas":
                assert item["alternate_windows"] == {"es": [], "en": []}
            else:
                assert item["alternate_windows"] == {
                    "es": ["A4C con inclinación anterior para abrir el TSVI."],
                    "en": ["A4C with anterior angulation to open the LVOT."]
                }

            # No vulnerable / object Object
            for field in bilingual_fields:
                for lang in ["es", "en"]:
                    val = item[field][lang]
                    assert "[object Object]" not in val
                    assert "<script" not in val.lower()
                    assert "javascript:" not in val.lower()
                    assert "onerror=" not in val.lower()
                    assert "onclick=" not in val.lower()

def test_stroke_volume_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units_map = {
        "area_tsvi_meas": "cm²",
        "vti_tsvi_meas": "cm",
        "volumen_sistolico_meas": "mL",
        "sv_index": "mL/m²",
        "gasto_cardiaco_meas": "L/min",
        "cardiac_index": "L/min/m²",
        "plr_vti_change": "%",
        "rvs_meas": "dyn·s·cm⁻⁵",
        "irvs_meas": "dyn·s·cm⁻⁵·m²"
    }
    for i_id, expected_unit in units_map.items():
        item = next(m for m in data if m["id"] == i_id)
        assert item["units"] == expected_unit
        assert isinstance(item["units"], str)

def test_stroke_volume_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. area_tsvi_meas
    area = next(m for m in data if m["id"] == "area_tsvi_meas")
    assert area["measurement"]["es"] == "Área del TSVI"
    assert area["measurement"]["en"] == "LVOT area"
    assert "diámetro²" in area["formula_or_method"]["es"]
    assert "diameter²" in area["formula_or_method"]["en"]

    # 2. vti_tsvi_meas
    vti = next(m for m in data if m["id"] == "vti_tsvi_meas")
    # Preservar el error ortográfico original
    assert "alinedado" in vti["interpretation_limitations"]["es"]
    assert "aligned" in vti["interpretation_limitations"]["en"]

    # 7. plr_vti_change
    plr = next(m for m in data if m["id"] == "plr_vti_change")
    assert "elevación pasiva de piernas" in plr["measurement"]["es"].lower()
    assert "passive leg raising" in plr["measurement"]["en"].lower()

    # 8. rvs_meas
    rvs = next(m for m in data if m["id"] == "rvs_meas")
    assert "PAM" in rvs["formula_or_method"]["es"]
    assert "MAP" in rvs["formula_or_method"]["en"]
    assert rvs["acquisition_timing"]["es"] == "Después de estimar GC y presión AD"
    assert rvs["acquisition_timing"]["en"] == "After estimating cardiac output and right atrial pressure"

    # 9. irvs_meas
    irvs = next(m for m in data if m["id"] == "irvs_meas")
    assert irvs["acquisition_timing"]["es"] == "Después de estimar IC y presión AD"
    assert irvs["acquisition_timing"]["en"] == "After estimating cardiac index and right atrial pressure"

def test_previous_migrated_sections_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Las 27 anteriores siguen siendo bilingües
    all_prev = {
        "ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas",
        "diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir",
        "area_mitral_planimetria", "area_mitral_pht", "gradiente_medio_mitral", "pht_meas", "relacion_vti_mitral_tsvi",
        "onda_e_mitral", "onda_a_mitral", "relacion_e_a", "tiempo_desaceleracion_e", "ivrt_meas",
        "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "velocidad_it_diastology",
        "lavi_diastology", "la_strain_diastology", "derrame_pericardico_pequeno", "derrame_pericardico_moderado",
        "derrame_pericardico_grande", "colapso_ad_meas", "colapso_vd_meas", "variacion_mitral_respiratoria",
        "variacion_tricuspidea_respiratoria", "vci_pletorica_meas", "movimiento_pendular_meas"
    }
    for item in data:
        if item["id"] in all_prev:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
