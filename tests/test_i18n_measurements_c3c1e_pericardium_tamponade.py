import os
import json
import pytest

def test_pericardium_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {
        "derrame_pericardico_pequeno", "derrame_pericardico_moderado", "derrame_pericardico_grande",
        "colapso_ad_meas", "colapso_vd_meas", "variacion_mitral_respiratoria",
        "variacion_tricuspidea_respiratoria", "vci_pletorica_meas", "movimiento_pendular_meas"
    }
    for tid in target_ids:
        assert tid in ids

def test_pericardium_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "derrame_pericardico_pequeno": 1,
        "derrame_pericardico_moderado": 2,
        "derrame_pericardico_grande": 3,
        "colapso_ad_meas": 4,
        "colapso_vd_meas": 5,
        "variacion_mitral_respiratoria": 6,
        "variacion_tricuspidea_respiratoria": 7,
        "vci_pletorica_meas": 8,
        "movimiento_pendular_meas": 9
    }

    expected_related = {
        "derrame_pericardico_pequeno": ["derrame_pericardico_term"],
        "derrame_pericardico_moderado": ["derrame_pericardico_term"],
        "derrame_pericardico_grande": ["derrame_pericardico_term"],
        "colapso_ad_meas": ["colapso_sistolico_ad_term", "ad_term"],
        "colapso_vd_meas": ["colapso_diastolico_vd_term", "vd_term"],
        "variacion_mitral_respiratoria": ["variacion_respiratoria_transmitral_term", "onda_e_term"],
        "variacion_tricuspidea_respiratoria": ["variacion_respiratoria_trantricuspidea_term"],
        "vci_pletorica_meas": ["vci_pletorica_term", "vci_term"],
        "movimiento_pendular_meas": ["movimiento_pendular_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "pericardium_tamponade"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 10
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

            # alternate_windows except colapso_ad_meas
            if i_id != "colapso_ad_meas":
                assert item["alternate_windows"] == {"es": [], "en": []}
            else:
                assert item["alternate_windows"] == {
                    "es": ["PLAX puede complementar según localización del derrame."],
                    "en": ["PLAX may complement the assessment depending on the effusion location."]
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

def test_pericardium_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 12. Las 9 abreviaturas son objetos bilingües
    target_ids = {
        "derrame_pericardico_pequeno", "derrame_pericardico_moderado", "derrame_pericardico_grande",
        "colapso_ad_meas", "colapso_vd_meas", "variacion_mitral_respiratoria",
        "variacion_tricuspidea_respiratoria", "vci_pletorica_meas", "movimiento_pendular_meas"
    }
    for i_id in target_ids:
        item = next(m for m in data if m["id"] == i_id)
        assert isinstance(item["abbreviation"], dict)
        assert "es" in item["abbreviation"] and "en" in item["abbreviation"]

    # 13. Las unidades mm y % permanecen strings
    string_units = ["derrame_pericardico_pequeno", "derrame_pericardico_moderado", "derrame_pericardico_grande", "variacion_mitral_respiratoria", "variacion_tricuspidea_respiratoria"]
    for i_id in string_units:
        item = next(m for m in data if m["id"] == i_id)
        assert isinstance(item["units"], str)
        assert item["units"] in ["mm", "%"]

    # 14. Las cuatro unidades adimensionales son bilingües
    bilingual_units = ["colapso_ad_meas", "colapso_vd_meas", "vci_pletorica_meas", "movimiento_pendular_meas"]
    for i_id in bilingual_units:
        item = next(m for m in data if m["id"] == i_id)
        assert isinstance(item["units"], dict)
        assert item["units"] == {"es": "adimensional", "en": "dimensionless"}

def test_pericardium_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dp = next(m for m in data if m["id"] == "derrame_pericardico_pequeno")
    assert "<10 mm" in dp["normal_values"]["es"]
    assert "<10 mm" in dp["normal_values"]["en"]

    dm = next(m for m in data if m["id"] == "derrame_pericardico_moderado")
    assert "10-20 mm" in dm["normal_values"]["es"]
    assert "10-20 mm" in dm["normal_values"]["en"]

    dg = next(m for m in data if m["id"] == "derrame_pericardico_grande")
    assert ">20 mm" in dg["normal_values"]["es"]
    assert ">20 mm" in dg["normal_values"]["en"]

    vm = next(m for m in data if m["id"] == "variacion_mitral_respiratoria")
    assert "<25%" in vm["normal_values"]["es"]
    assert "<25%" in vm["normal_values"]["en"]
    assert "Doppler pulsado" in vm["modality"]["es"]

    vt = next(m for m in data if m["id"] == "variacion_tricuspidea_respiratoria")
    assert "<40%" in vt["normal_values"]["es"]
    assert "<40%" in vt["normal_values"]["en"]
    assert "Doppler pulsado" in vt["modality"]["es"]

    vci = next(m for m in data if m["id"] == "vci_pletorica_meas")
    assert ">2,1 cm" in vci["formula_or_method"]["es"]
    assert ">2.1 cm" in vci["formula_or_method"]["en"]
    assert "1-2 cm" in vci["acquisition_key"]["es"]

    # 21-25 criteria
    col_ad = next(m for m in data if m["id"] == "colapso_ad_meas")
    assert "Ausente normalmente." in col_ad["normal_values"]["es"]
    assert "modo M opcional" in col_ad["modality"]["es"]
    assert "Sístole" in col_ad["acquisition_timing"]["es"]

    col_vd = next(m for m in data if m["id"] == "colapso_vd_meas")
    assert "Ausente normalmente." in col_vd["normal_values"]["es"]
    assert "modo M opcional" in col_vd["modality"]["es"]
    assert "Diástole temprana" in col_vd["acquisition_timing"]["es"]

def test_previous_migrated_sections_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 29. Las 27 anteriores siguen siendo bilingües
    all_prev = {
        "ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas",
        "diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir",
        "area_mitral_planimetria", "area_mitral_pht", "gradiente_medio_mitral", "pht_meas", "relacion_vti_mitral_tsvi",
        "onda_e_mitral", "onda_a_mitral", "relacion_e_a", "tiempo_desaceleracion_e", "ivrt_meas",
        "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "velocidad_it_diastology",
        "lavi_diastology", "la_strain_diastology"
    }
    for item in data:
        if item["id"] in all_prev:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # 30. No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
