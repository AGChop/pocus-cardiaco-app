import os
import json
import pytest

def test_pulmonary_hemodynamics_measurements_structure_and_count():
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
        "gradiente_vd_ad",
        "pasp_meas",
        "presion_media_pulmonar",
        "presion_diastolica_pulmonar",
        "rvp_ecografica",
        "indice_excentricidad_vi",
        "aplanamiento_septal_meas"
    }
    for tid in target_ids:
        assert tid in ids

def test_pulmonary_hemodynamics_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_order = {
        "gradiente_vd_ad": 1,
        "pasp_meas": 2,
        "presion_media_pulmonar": 3,
        "presion_diastolica_pulmonar": 4,
        "rvp_ecografica": 5,
        "indice_excentricidad_vi": 6,
        "aplanamiento_septal_meas": 7
    }

    expected_related = {
        "gradiente_vd_ad": ["bernoulli_term", "it_term"],
        "pasp_meas": ["pasp_term", "psvd_term", "bernoulli_term", "presion_ad_term"],
        "presion_media_pulmonar": ["mpap_term", "pr_term", "presion_ad_term"],
        "presion_diastolica_pulmonar": ["pr_term", "presion_ad_term"],
        "rvp_ecografica": ["rvp_term", "it_term", "tsvd_term"],
        "indice_excentricidad_vi": ["indice_excentricidad_term"],
        "aplanamiento_septal_meas": ["psax", "indice_excentricidad_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            assert item["section_id"] == "pulmonary_hemodynamics"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 8
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

def test_pulmonary_hemodynamics_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Las cuatro de mmHg son strings
    mmHg_ids = ["gradiente_vd_ad", "pasp_meas", "presion_media_pulmonar", "presion_diastolica_pulmonar"]
    for m_id in mmHg_ids:
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == "mmHg"

    # rvp_ecografica es objeto bilingüe
    rvp = next(m for m in data if m["id"] == "rvp_ecografica")
    assert rvp["units"] == {"es": "UW", "en": "WU"}

    # indice_excentricidad_vi es objeto bilingüe
    ecc = next(m for m in data if m["id"] == "indice_excentricidad_vi")
    assert ecc["units"] == {"es": "adimensional", "en": "dimensionless"}

    # aplanamiento_septal_meas es objeto bilingüe
    flat = next(m for m in data if m["id"] == "aplanamiento_septal_meas")
    assert flat["units"] == {"es": "adimensional", "en": "dimensionless"}

def test_pulmonary_hemodynamics_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. gradiente_vd_ad
    grad = next(m for m in data if m["id"] == "gradiente_vd_ad")
    assert grad["measurement"]["es"] == "Gradiente VD-AD"
    assert grad["measurement"]["en"] == "RV-RA gradient"
    assert grad["abbreviation"]["es"] == "Gradiente VD-AD"
    assert grad["abbreviation"]["en"] == "RV-RA gradient"
    assert "4 x velocidad máxima de IT²." in grad["formula_or_method"]["es"]
    assert "4 x peak TR velocity²." in grad["formula_or_method"]["en"]
    assert "Depende de la velocidad." in grad["normal_values"]["es"]
    assert "Depends on the measured velocity." in grad["normal_values"]["en"]
    assert "Aplicar Bernoulli con velocidad en m/s para obtener mmHg." in grad["interpretation_limitations"]["es"]
    assert "Apply the modified Bernoulli equation using velocity in m/s to obtain mmHg." in grad["interpretation_limitations"]["en"]

    # 2. pasp_meas
    pasp = next(m for m in data if m["id"] == "pasp_meas")
    assert pasp["measurement"]["es"] == "PSVD / PASP"
    assert pasp["measurement"]["en"] == "RVSP / PASP"
    assert pasp["abbreviation"]["es"] == "PASP"
    assert pasp["abbreviation"]["en"] == "PASP"
    assert "4 x VIT² + presión AD." in pasp["formula_or_method"]["es"]
    assert "4 x peak TR velocity² + RAP." in pasp["formula_or_method"]["en"]
    assert "Habitualmente <35 mmHg." in pasp["normal_values"]["es"]
    assert "Usually <35 mmHg." in pasp["normal_values"]["en"]
    assert "PASP equivale a PSVD solo sin obstrucción pulmonar/TSVD significativa." in pasp["interpretation_limitations"]["es"]
    assert "PASP equals RVSP only in the absence of significant pulmonic valve or RVOT obstruction." in pasp["interpretation_limitations"]["en"]

    # 3. presion_media_pulmonar
    mpap = next(m for m in data if m["id"] == "presion_media_pulmonar")
    assert mpap["measurement"]["es"] == "Presión media pulmonar por PR"
    assert mpap["measurement"]["en"] == "Mean pulmonary artery pressure from PR"
    assert mpap["abbreviation"]["es"] == "mPAP"
    assert mpap["abbreviation"]["en"] == "mPAP"
    assert "4 x velocidad protodiastólica de PR² + presión AD." in mpap["formula_or_method"]["es"]
    assert "4 x early diastolic PR velocity² + RAP." in mpap["formula_or_method"]["en"]
    assert "<20 mmHg." in mpap["normal_values"]["es"]
    assert "<20 mmHg." in mpap["normal_values"]["en"]
    assert "La definición hemodinámica de hipertensión pulmonar requiere confirmación invasiva." in mpap["interpretation_limitations"]["es"]
    assert "The hemodynamic definition of pulmonary hypertension requires invasive confirmation." in mpap["interpretation_limitations"]["en"]

    # 4. presion_diastolica_pulmonar
    dpap = next(m for m in data if m["id"] == "presion_diastolica_pulmonar")
    assert dpap["measurement"]["es"] == "Presión diastólica pulmonar"
    assert dpap["measurement"]["en"] == "Pulmonary artery diastolic pressure"
    assert dpap["abbreviation"]["es"] == "dPAP"
    assert dpap["abbreviation"]["en"] == "dPAP"
    assert "4 x velocidad telediastólica de PR² + presión AD." in dpap["formula_or_method"]["es"]
    assert "4 x end-diastolic PR velocity² + RAP." in dpap["formula_or_method"]["en"]
    assert "Aprox. <15 mmHg." in dpap["normal_values"]["es"]
    assert "Approx. <15 mmHg." in dpap["normal_values"]["en"]

    # 5. rvp_ecografica
    rvp = next(m for m in data if m["id"] == "rvp_ecografica")
    assert rvp["measurement"]["es"] == "RVP ecográfica"
    assert rvp["measurement"]["en"] == "Echocardiographic PVR"
    assert rvp["abbreviation"]["es"] == "RVP ecográfica"
    assert rvp["abbreviation"]["en"] == "Echocardiographic PVR"
    assert "[(Vmax IT / VTI del TSVD) x 10] + 0,16." in rvp["formula_or_method"]["es"]
    assert "[(Peak TR velocity / RVOT VTI) x 10] + 0.16." in rvp["formula_or_method"]["en"]
    assert "Normal <1,5 UW; >2 UW es anormal." in rvp["normal_values"]["es"]
    assert "Normal <1.5 WU; >2 WU is abnormal." in rvp["normal_values"]["en"]
    assert "Corrección importante: usa VTI del TSVD/RVOT, no VTI del TSVI." in rvp["interpretation_limitations"]["es"]
    assert "Important correction: uses RVOT VTI, not LVOT VTI." in rvp["interpretation_limitations"]["en"]

    # 6. indice_excentricidad_vi
    ecc = next(m for m in data if m["id"] == "indice_excentricidad_vi")
    assert ecc["measurement"]["es"] == "Índice de excentricidad del VI"
    assert ecc["measurement"]["en"] == "LV eccentricity index"
    assert ecc["abbreviation"]["es"] == "Índice de excentricidad"
    assert ecc["abbreviation"]["en"] == "Eccentricity index"
    assert "Diámetro paralelo al septo / diámetro perpendicular." in ecc["formula_or_method"]["es"]
    assert "Diameter parallel to the septum / perpendicular diameter." in ecc["formula_or_method"]["en"]
    assert "Aprox. 1,0." in ecc["normal_values"]["es"]
    assert "Approx. 1.0." in ecc["normal_values"]["en"]

    # 7. aplanamiento_septal_meas
    flat = next(m for m in data if m["id"] == "aplanamiento_septal_meas")
    assert flat["measurement"]["es"] == "Aplanamiento septal"
    assert flat["measurement"]["en"] == "Septal flattening"
    assert flat["abbreviation"]["es"] == "Aplanamiento septal"
    assert flat["abbreviation"]["en"] == "Septal flattening"
    assert "Evaluación cualitativa en eje corto." in flat["formula_or_method"]["es"]
    assert "Qualitative assessment in the short-axis view." in flat["formula_or_method"]["en"]
    assert "Ausente normalmente." in flat["normal_values"]["es"]
    assert "Normally absent." in flat["normal_values"]["en"]

def test_previous_geometry_atrium_and_ra_ivc_intact():
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

    # Las siete de ra_ivc siguen siendo bilingües
    ra_ivc_ids = {
        "area_ad_meas",
        "longitud_ad",
        "diametro_menor_ad",
        "diametro_vci_meas",
        "colapsabilidad_vci_meas",
        "distensibilidad_vci_meas",
        "presion_ad_estimada_meas"
    }
    for item in data:
        if item["id"] in ra_ivc_ids:
            assert isinstance(item["measurement"], dict)
            assert "es" in item["measurement"] and "en" in item["measurement"]
