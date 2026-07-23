import os
import json
import pytest

def test_aortic_valve_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {
        "velocidad_max_aortica", "gradiente_max_aortico", "gradiente_medio_aortico",
        "ava_meas", "ava_indexed", "dvi_meas", "velocidad_tsvi"
    }
    for tid in target_ids:
        assert tid in ids

def test_aortic_valve_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "velocidad_max_aortica": 1,
        "gradiente_max_aortico": 2,
        "gradiente_medio_aortico": 3,
        "ava_meas": 4,
        "ava_indexed": 5,
        "dvi_meas": 6,
        "velocidad_tsvi": 7
    }

    expected_related = {
        "velocidad_max_aortica": ["vmax_aortica_term", "cw_doppler"],
        "gradiente_max_aortico": ["gradiente_max_term", "bernoulli_term", "vmax_aortica_term"],
        "gradiente_medio_aortico": ["gradiente_medio_term", "vmax_aortica_term"],
        "ava_meas": ["ava_term", "area_tsvi_term", "vti_term"],
        "ava_indexed": ["ava_term", "bsa", "indexed"],
        "dvi_meas": ["dvi_term", "vti_term", "vmax_aortica_term"],
        "velocidad_tsvi": ["tsvi_term", "pw_doppler"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "aortic_valve_lvot"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 9
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

            # alternate_windows except velocidad_max_aortica
            if i_id != "velocidad_max_aortica":
                assert item["alternate_windows"] == {"es": [], "en": []}
            else:
                assert item["alternate_windows"] == {
                    "es": ["Apical; paraesternal derecha; supraesternal."],
                    "en": ["Apical; right parasternal; suprasternal."]
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

def test_aortic_valve_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units_map = {
        "velocidad_max_aortica": "m/s",
        "gradiente_max_aortico": "mmHg",
        "gradiente_medio_aortico": "mmHg",
        "ava_meas": "cm²",
        "ava_indexed": "cm²/m²",
        "velocidad_tsvi": "m/s"
    }
    for i_id, expected_unit in units_map.items():
        item = next(m for m in data if m["id"] == i_id)
        assert item["units"] == expected_unit
        assert isinstance(item["units"], str)

    # dvi_meas units is bilingual object
    dvi = next(m for m in data if m["id"] == "dvi_meas")
    assert dvi["units"] == {"es": "adimensional", "en": "dimensionless"}

def test_aortic_valve_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. velocidad_max_aortica
    vmax = next(m for m in data if m["id"] == "velocidad_max_aortica")
    assert vmax["measurement"]["es"] == "Velocidad máxima aórtica"
    assert vmax["measurement"]["en"] == "Peak aortic velocity"
    assert "<2,0 m/s." == vmax["normal_values"]["es"]
    assert "<2.0 m/s." == vmax["normal_values"]["en"]

    # 4. ava_meas
    ava = next(m for m in data if m["id"] == "ava_meas")
    assert ava["measurement"]["es"] == "Área valvular aórtica (AVA)"
    assert ava["measurement"]["en"] == "Aortic valve area (AVA)"

    # 6. dvi_meas
    dvi = next(m for m in data if m["id"] == "dvi_meas")
    assert dvi["measurement"]["es"] == "Índice adimensional (DVI)"
    assert dvi["measurement"]["en"] == "Doppler velocity index (DVI)"
    assert "<0,25" in dvi["interpretation_limitations"]["es"]
    assert "<0.25" in dvi["interpretation_limitations"]["en"]

def test_previous_migrated_sections_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Las 36 anteriores siguen siendo bilingües
    all_prev = {
        "ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas",
        "diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir",
        "area_mitral_planimetria", "area_mitral_pht", "gradiente_medio_mitral", "pht_meas", "relacion_vti_mitral_tsvi",
        "onda_e_mitral", "onda_a_mitral", "relacion_e_a", "tiempo_desaceleracion_e", "ivrt_meas",
        "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "velocidad_it_diastology",
        "lavi_diastology", "la_strain_diastology", "derrame_pericardico_pequeno", "derrame_pericardico_moderado",
        "derrame_pericardico_grande", "colapso_ad_meas", "colapso_vd_meas", "variacion_mitral_respiratoria",
        "variacion_tricuspidea_respiratoria", "vci_pletorica_meas", "movimiento_pendular_meas",
        "area_tsvi_meas", "vti_tsvi_meas", "volumen_sistolico_meas", "sv_index", "gasto_cardiaco_meas",
        "cardiac_index", "plr_vti_change", "rvs_meas", "irvs_meas"
    }
    for item in data:
        if item["id"] in all_prev:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
