import os
import json
import pytest

def test_right_atrium_ivc_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    # The count should remain exactly 101 records
    assert len(data) == 101
    
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    target_ids = {
        "area_ad_meas",
        "longitud_ad",
        "diametro_menor_ad",
        "diametro_vci_meas",
        "colapsabilidad_vci_meas",
        "distensibilidad_vci_meas",
        "presion_ad_estimada_meas"
    }
    for tid in target_ids:
        assert tid in ids

def test_right_atrium_ivc_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "area_ad_meas": 1,
        "longitud_ad": 2,
        "diametro_menor_ad": 3,
        "diametro_vci_meas": 4,
        "colapsabilidad_vci_meas": 5,
        "distensibilidad_vci_meas": 6,
        "presion_ad_estimada_meas": 7
    }

    expected_related = {
        "area_ad_meas": ["ad_term", "a4c"],
        "longitud_ad": ["ad_term", "a4c"],
        "diametro_menor_ad": ["ad_term", "a4c"],
        "diametro_vci_meas": ["vci_term", "subcostal"],
        "colapsabilidad_vci_meas": ["colapsabilidad_vci_term", "vci_term"],
        "distensibilidad_vci_meas": ["distensibilidad_vci_term", "vci_term"],
        "presion_ad_estimada_meas": ["presion_ad_term", "vci_term", "colapsabilidad_vci_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "ra_ivc"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 7
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            bilingual_fields = [
                "measurement", "abbreviation", "formula_or_method", "normal_values",
                "interpretation_limitations", "primary_window", "preferred_view",
                "modality", "acquisition_timing", "acquisition_key"
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
            assert isinstance(item["alternate_windows"], dict)
            assert "es" in item["alternate_windows"] and "en" in item["alternate_windows"]
            assert isinstance(item["alternate_windows"]["es"], list)
            assert isinstance(item["alternate_windows"]["en"], list)

            # No vulnerable / object Object
            for field in bilingual_fields:
                for lang in ["es", "en"]:
                    val = item[field][lang]
                    assert "[object Object]" not in val
                    assert "<script" not in val.lower()
                    assert "javascript:" not in val.lower()
                    assert "onerror=" not in val.lower()
                    assert "onclick=" not in val.lower()

def test_right_atrium_ivc_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_units = {
        "area_ad_meas": "cm²",
        "longitud_ad": "mm",
        "diametro_menor_ad": "mm",
        "diametro_vci_meas": "cm",
        "colapsabilidad_vci_meas": "%",
        "distensibilidad_vci_meas": "%",
        "presion_ad_estimada_meas": "mmHg"
    }

    for m_id, unit in expected_units.items():
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == unit

def test_right_atrium_ivc_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. area_ad_meas
    area = next(m for m in data if m["id"] == "area_ad_meas")
    assert area["measurement"]["es"] == "Área de AD"
    assert area["measurement"]["en"] == "Right atrial area"
    assert area["abbreviation"]["es"] == "Área AD"
    assert area["abbreviation"]["en"] == "RA area"
    assert "Planimetría en A4C al final de la sístole." in area["formula_or_method"]["es"]
    assert "Planimetry in the A4C view at end-systole." in area["formula_or_method"]["en"]
    assert "≤18 cm²." in area["normal_values"]["es"]
    assert "≤18 cm²." in area["normal_values"]["en"]
    assert "Evitar incluir venas cavas, seno coronario y apéndice." in area["interpretation_limitations"]["es"]
    assert "Exclude the venae cavae, coronary sinus, and right atrial appendage." in area["interpretation_limitations"]["en"]

    # 2. longitud_ad
    longitud = next(m for m in data if m["id"] == "longitud_ad")
    assert longitud["measurement"]["es"] == "Longitud de AD"
    assert longitud["measurement"]["en"] == "Right atrial length"
    assert longitud["abbreviation"]["es"] == "Longitud AD"
    assert longitud["abbreviation"]["en"] == "RA length"
    assert "Techo de AD al centro del anillo tricuspídeo." in longitud["formula_or_method"]["es"]
    assert "From the roof of the right atrium to the center of the tricuspid annulus." in longitud["formula_or_method"]["en"]
    assert "≤53 mm." in longitud["normal_values"]["es"]
    assert "≤53 mm." in longitud["normal_values"]["en"]

    # 3. diametro_menor_ad
    diam_menor = next(m for m in data if m["id"] == "diametro_menor_ad")
    assert diam_menor["measurement"]["es"] == "Diámetro menor de AD"
    assert diam_menor["measurement"]["en"] == "Right atrial minor-axis diameter"
    assert diam_menor["abbreviation"]["es"] == "Diámetro menor AD"
    assert diam_menor["abbreviation"]["en"] == "RA minor-axis diameter"
    assert "Perpendicular al eje mayor." in diam_menor["formula_or_method"]["es"]
    assert "Perpendicular to the long axis." in diam_menor["formula_or_method"]["en"]
    assert "≤44 mm." in diam_menor["normal_values"]["es"]
    assert "≤44 mm." in diam_menor["normal_values"]["en"]

    # 4. diametro_vci_meas
    diam_vci = next(m for m in data if m["id"] == "diametro_vci_meas")
    assert diam_vci["measurement"]["es"] == "Diámetro de VCI"
    assert diam_vci["measurement"]["en"] == "IVC diameter"
    assert diam_vci["abbreviation"]["es"] == "Diámetro VCI"
    assert diam_vci["abbreviation"]["en"] == "IVC diameter"
    assert "Subcostal, 1-2 cm de la unión con AD." in diam_vci["formula_or_method"]["es"]
    assert "Subcostal view, 1-2 cm from the junction with the right atrium." in diam_vci["formula_or_method"]["en"]
    assert "≤2,1 cm." in diam_vci["normal_values"]["es"]
    assert "≤2.1 cm." in diam_vci["normal_values"]["en"]
    assert "Transhepática derecha lateral; vista transversal para confirmar el diámetro máximo." in diam_vci["alternate_windows"]["es"]
    assert "Right lateral transhepatic view; short-axis view to confirm the maximum diameter." in diam_vci["alternate_windows"]["en"]

    # 5. colapsabilidad_vci_meas
    colaps = next(m for m in data if m["id"] == "colapsabilidad_vci_meas")
    assert colaps["measurement"]["es"] == "Colapsabilidad de VCI"
    assert colaps["measurement"]["en"] == "IVC collapsibility"
    assert colaps["abbreviation"]["es"] == "Colapsabilidad VCI"
    assert colaps["abbreviation"]["en"] == "IVC collapsibility"
    assert "[(VCI espiratoria - VCI inspiratoria) / VCI espiratoria] x 100." in colaps["formula_or_method"]["es"]
    assert "[(Expiratory IVC - inspiratory IVC) / expiratory IVC] x 100." in colaps["formula_or_method"]["en"]
    assert ">50% en respiración espontánea." in colaps["normal_values"]["es"]
    assert ">50% during spontaneous breathing." in colaps["normal_values"]["en"]

    # 6. distensibilidad_vci_meas
    distens = next(m for m in data if m["id"] == "distensibilidad_vci_meas")
    assert distens["measurement"]["es"] == "Distensibilidad de VCI"
    assert distens["measurement"]["en"] == "IVC distensibility"
    assert distens["abbreviation"]["es"] == "Distensibilidad VCI"
    assert distens["abbreviation"]["en"] == "IVC distensibility"
    assert "[(VCI máxima - VCI mínima) / VCI mínima] x 100." in distens["formula_or_method"]["es"]
    assert "[(Maximum IVC - minimum IVC) / minimum IVC] x 100." in distens["formula_or_method"]["en"]
    assert "Sin punto universal; depende de condiciones ventilatorias." in distens["normal_values"]["es"]
    assert "No universal cutoff; depends on ventilatory conditions." in distens["normal_values"]["en"]

    # 7. presion_ad_estimada_meas
    rap = next(m for m in data if m["id"] == "presion_ad_estimada_meas")
    assert rap["measurement"]["es"] == "Presión AD estimada"
    assert rap["measurement"]["en"] == "Estimated right atrial pressure"
    assert rap["abbreviation"]["es"] == "Presión AD"
    assert rap["abbreviation"]["en"] == "RAP"
    assert "VCI ≤2,1 cm y colapso >50%: 3 mmHg; VCI >2,1 cm y colapso <50%: 15 mmHg; intermedio: 8 mmHg." in rap["formula_or_method"]["es"]
    assert "IVC ≤2.1 cm and collapse >50%: 3 mmHg; IVC >2.1 cm and collapse <50%: 15 mmHg; intermediate: 8 mmHg." in rap["formula_or_method"]["en"]
    assert "3, 8 o 15 mmHg según patrón." in rap["normal_values"]["es"]
    assert "3, 8, or 15 mmHg depending on the pattern." in rap["normal_values"]["en"]

def test_previous_geometry_and_atrium_non_affected_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Las seis de lv_geometry siguen siendo bilingües
    geometry_ids = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas"}
    for item in data:
        if item["id"] in geometry_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]

    # Las cinco de left_atrium siguen siendo bilingües
    atrium_ids = {"diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir"}
    for item in data:
        if item["id"] in atrium_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]
