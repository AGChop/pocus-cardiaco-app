import os
import json
import hashlib
import re

def test_qa3_measurements_count_and_spanish_hash():
    # 8. Sigue habiendo exactamente 101 registros
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101

    # 3. Construir la proyección española exactamente así
    projection = []
    for item in measurements:
        spanish_fields = {
            key: value["es"]
            for key, value in item.items()
            if isinstance(value, dict) and "es" in value
        }
        projection.append({
            "id": item["id"],
            "es": spanish_fields,
        })

    payload = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    sha = hashlib.sha256(payload).hexdigest()

    assert sha == "8602489c09530fbcc05cd710f08f6edc2fe80df05a5f36702a31718735483c47"

def test_qa3_exact_english_values():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    # 1. Comprobar los 19 valores exactos de measurement.en
    expected_measurements = {
        "dtdvi": "LV internal dimension at end-diastole (LVIDd)",
        "dtsvi": "LV internal dimension at end-systole (LVIDs)",
        "vtdvi_indexed": "LV end-diastolic volume index",
        "vtsvi_indexed": "LV end-systolic volume index",
        "s_prima_mitral": "Mitral annular peak systolic velocity (s′)",
        "e_septal_meas": "Septal mitral annular e′ velocity",
        "e_lateral_meas": "Lateral mitral annular e′ velocity",
        "relacion_e_e_promedio": "Average E/e′ ratio",
        "lavi_diastology": "LA volume index for diastolic function assessment",
        "la_strain_diastology": "LA reservoir strain for diastolic function assessment",
        "s_prima_vd": "Tricuspid annular peak systolic velocity (s′)",
        "strain_rv": "RV free wall longitudinal strain",
        "indice_tei_vd": "RV myocardial performance index (Tei index)",
        "paat_tsvd": "RVOT acceleration time",
        "rvp_ecografica": "Echocardiographic estimate of pulmonary vascular resistance",
        "velocidad_max_aortica": "Peak aortic jet velocity",
        "gradiente_max_aortico": "Peak instantaneous transaortic gradient",
        "gradiente_medio_aortico": "Mean transaortic pressure gradient",
        "movimiento_pendular_meas": "Swinging heart"
    }

    # 2. Comprobar las abreviaturas inglesas
    expected_abbreviations = {
        "dtdvi": "LVIDd",
        "dtsvi": "LVIDs",
        "s_prima_mitral": "Mitral annular s′",
        "e_septal_meas": "Septal e′",
        "e_lateral_meas": "Lateral e′",
        "relacion_e_e_promedio": "Average E/e′",
        "s_prima_vd": "Tricuspid annular s′",
        "strain_rv": "RVFWS",
        "indice_tei_vd": "RV MPI",
        "paat_tsvd": "RVOT AccT",
        "rvp_ecografica": "PVR",
        "movimiento_pendular_meas": "Swinging heart"
    }

    # 3. Comprobar aliases.en correspondientes
    expected_aliases = {
        "dtdvi": [
            "LVIDd",
            "Left ventricular internal diameter at end-diastole",
            "LV internal dimension at end-diastole"
        ],
        "dtsvi": [
            "LVIDs",
            "Left ventricular internal diameter at end-systole",
            "LV internal dimension at end-systole"
        ],
        "vtdvi_indexed": [
            "LV end-diastolic volume index",
            "Indexed left ventricular end-diastolic volume",
            "LVEDVi"
        ],
        "vtsvi_indexed": [
            "LV end-systolic volume index",
            "Indexed left ventricular end-systolic volume",
            "LVESVi"
        ],
        "s_prima_mitral": [
            "Mitral annular peak systolic velocity (s′)",
            "Mitral annular s′",
            "s′"
        ],
        "e_septal_meas": [
            "Septal mitral annular e′ velocity",
            "Septal e′"
        ],
        "e_lateral_meas": [
            "Lateral mitral annular e′ velocity",
            "Lateral e′"
        ],
        "relacion_e_e_promedio": [
            "Average E/e′",
            "Average E/e′ ratio",
            "E/e′ ratio (average)"
        ],
        "lavi_diastology": [
            "Left atrial volume index in diastolic assessment"
        ],
        "la_strain_diastology": [
            "LA reservoir strain in diastolic assessment"
        ],
        "s_prima_vd": [
            "Tricuspid s′",
            "Tricuspid annular peak systolic velocity (s′)",
            "Tricuspid s′ velocity"
        ],
        "strain_rv": [
            "Right ventricular free wall longitudinal strain",
            "RV free wall strain"
        ],
        "indice_tei_vd": [
            "RV MPI",
            "RV myocardial performance index (Tei index)",
            "RV Tei index"
        ],
        "paat_tsvd": [
            "Pulmonary artery acceleration time",
            "RVOT acceleration time",
            "PAAT"
        ],
        "rvp_ecografica": [
            "Echocardiographic pulmonary vascular resistance",
            "Echocardiographic PVR"
        ],
        "movimiento_pendular_meas": [
            "Swinging heart",
            "Pendular heart motion"
        ]
    }

    m_map = {m["id"]: m for m in measurements}

    for m_id, expected_name in expected_measurements.items():
        assert m_map[m_id]["measurement"]["en"] == expected_name

    for m_id, expected_abbr in expected_abbreviations.items():
        assert m_map[m_id]["abbreviation"]["en"] == expected_abbr

    for m_id, expected_alias_list in expected_aliases.items():
        # 4. Comprobar que en aliases.en no haya duplicados
        actual_aliases = m_map[m_id]["aliases"]["en"]
        assert len(actual_aliases) == len(set(actual_aliases)), f"Duplicate alias found for {m_id}"

        # Verify that all expected aliases exist in the actual aliases list
        for alias in expected_alias_list:
            assert alias in actual_aliases, f"Alias {alias} not found in {m_id}"

    # 5. Comprobar que la notación prima se exprese consistentemente utilizando el símbolo prima real ′ (U+2032)
    prima_ids = ["s_prima_mitral", "e_septal_meas", "e_lateral_meas", "relacion_e_e_promedio", "s_prima_vd"]
    for m_id in prima_ids:
        item = m_map[m_id]
        for key in ["measurement", "abbreviation", "aliases"]:
            if key in item and "en" in item[key]:
                val = item[key]["en"]
                if isinstance(val, str):
                    if any(char in val for char in ["e'", "s'", "e’", "s’", "e´", "s´"]):
                        raise AssertionError(f"Incorrect prime symbol in {m_id}.{key}.en: {val}")
                elif isinstance(val, list):
                    for alias in val:
                        if any(char in alias for char in ["e'", "s'", "e’", "s’", "e´", "s´"]):
                            raise AssertionError(f"Incorrect prime symbol in alias {alias} of {m_id}")

def test_qa3_service_worker_cache():
    # 7. CACHE_NAME exacto en service-worker.js
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1).startswith("pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final")
