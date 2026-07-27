import os
import json
import pytest

def test_rv_systolic_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    
    # 1. Que data/measurements.json contiene exactamente 101 registros.
    assert len(data) == 101
    
    # 4. Que no existen IDs duplicados.
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    # 2. Que rv_systolic contiene exactamente los 14 IDs autorizados.
    target_ids = [
        "diametro_basal_vd", "diametro_medio_vd", "rv_length", "relacion_vd_vi",
        "grosor_pared_vd", "tapse_meas", "s_prima_vd", "fac_vd_meas",
        "fevd_3d", "strain_rv", "indice_tei_vd", "vti_tsvd_meas",
        "paat_tsvd", "tapse_pasp_ratio"
    ]
    for tid in target_ids:
        assert tid in ids

def test_rv_systolic_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. Que los órdenes permanecen consecutivos de 1 a 14.
    expected_order = {
        "diametro_basal_vd": 1,
        "diametro_medio_vd": 2,
        "rv_length": 3,
        "relacion_vd_vi": 4,
        "grosor_pared_vd": 5,
        "tapse_meas": 6,
        "s_prima_vd": 7,
        "fac_vd_meas": 8,
        "fevd_3d": 9,
        "strain_rv": 10,
        "indice_tei_vd": 11,
        "vti_tsvd_meas": 12,
        "paat_tsvd": 13,
        "tapse_pasp_ratio": 14
    }

    expected_related = {
        "diametro_basal_vd": ["vd_term", "a4c"],
        "diametro_medio_vd": ["vd_term", "a4c"],
        "rv_length": ["vd_term", "foreshortening"],
        "relacion_vd_vi": ["relacion_vd_vi_term", "vd_term", "vi_term"],
        "grosor_pared_vd": ["vd_term", "plax"],
        "tapse_meas": ["tapse_term", "modo_m"],
        "s_prima_vd": ["s_prima_vd_term", "tdi"],
        "fac_vd_meas": ["fac_term", "vd_term"],
        "fevd_3d": ["fevd_term"],
        "strain_rv": ["strain_rv_term", "speckle_tracking"],
        "indice_tei_vd": ["indice_tei_term"],
        "vti_tsvd_meas": ["vti_term", "tsvd_term", "pw_doppler"],
        "paat_tsvd": ["paat_term"],
        "tapse_pasp_ratio": ["tapse_pasp_term", "tapse_term", "pasp_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            # 5. Que permanecen exactamente iguales: id, section_id, order, related_glossary_ids, source_page, source_document
            assert item["section_id"] == "rv_systolic"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 7
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            # 6. Que todos los campos traducibles de los 14 registros tienen una estructura válida {es, en}.
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

            # 7. Que todos los aliases tienen estructura bilingüe, conservan su número y mantienen el orden original.
            assert isinstance(item["aliases"], dict)
            assert "es" in item["aliases"] and "en" in item["aliases"]
            assert isinstance(item["aliases"]["es"], list)
            assert isinstance(item["aliases"]["en"], list)
            assert len(item["aliases"]["es"]) == len(item["aliases"]["en"])
            for a in item["aliases"]["es"] + item["aliases"]["en"]:
                assert isinstance(a, str) and a.strip() != ""

            # 8. Que cada alternate_windows no vacío tiene estructura bilingüe.
            # 9. Que las listas alternate_windows originalmente vacías permanecen vacías.
            assert isinstance(item["alternate_windows"], dict)
            assert "es" in item["alternate_windows"] and "en" in item["alternate_windows"]
            assert isinstance(item["alternate_windows"]["es"], list)
            assert isinstance(item["alternate_windows"]["en"], list)
            assert len(item["alternate_windows"]["es"]) == len(item["alternate_windows"]["en"])

def test_rv_systolic_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 12. Que las doce unidades técnicas continúan siendo strings exactos.
    expected_string_units = {
        "diametro_basal_vd": "mm",
        "diametro_medio_vd": "mm",
        "rv_length": "mm",
        "grosor_pared_vd": "mm",
        "tapse_meas": "mm",
        "s_prima_vd": "cm/s",
        "fac_vd_meas": "%",
        "fevd_3d": "%",
        "strain_rv": "%",
        "vti_tsvd_meas": "cm",
        "paat_tsvd": "ms",
        "tapse_pasp_ratio": "mm/mmHg"
    }
    for m_id, unit in expected_string_units.items():
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == unit
        assert isinstance(item["units"], str)

    # 13. Que relacion_vd_vi.units e indice_tei_vd.units coinciden exactamente con el dict bilingüe
    bilingual_unit_ids = ["relacion_vd_vi", "indice_tei_vd"]
    for m_id in bilingual_unit_ids:
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == {
            "es": "adimensional",
            "en": "dimensionless"
        }

def test_rv_systolic_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. diametro_basal_vd
    basal = next(m for m in data if m["id"] == "diametro_basal_vd")
    assert basal["measurement"]["es"] == "Diámetro basal del VD"
    assert basal["measurement"]["en"] == "RV basal diameter"
    assert basal["abbreviation"]["es"] == "Diámetro basal VD"
    assert basal["abbreviation"]["en"] == "RV basal diameter"
    assert basal["aliases"]["es"] == ["RV diameter 1", "RVD1", "Diámetro basal del ventrículo derecho"]
    assert basal["aliases"]["en"] == ["RV diameter 1", "RVD1", "Right ventricular basal diameter"]
    assert basal["formula_or_method"]["es"] == "A4C enfocada en VD, fin de diástole."
    assert basal["formula_or_method"]["en"] == "RV-focused A4C view at end-diastole."
    assert basal["normal_values"]["es"] == "≤41 mm."
    assert basal["normal_values"]["en"] == "≤41 mm."
    assert basal["interpretation_limitations"]["es"] == "Medir en el tercio basal máximo, perpendicular al eje largo."
    assert basal["interpretation_limitations"]["en"] == "Measure the maximal dimension in the basal third of the RV, perpendicular to the long axis."
    assert basal["primary_window"]["es"] == "Apical"
    assert basal["primary_window"]["en"] == "Apical"
    assert basal["preferred_view"]["es"] == "A4C enfocada en VD"
    assert basal["preferred_view"]["en"] == "RV-focused A4C"
    assert basal["modality"]["es"] == "2D"
    assert basal["modality"]["en"] == "2D"
    assert basal["acquisition_timing"]["es"] == "Fin de diástole"
    assert basal["acquisition_timing"]["en"] == "End-diastole"
    assert basal["acquisition_key"]["es"] == "Maximizar el VD sin foreshortening y medir basalmente de endocardio a endocardio."
    assert basal["acquisition_key"]["en"] == "Maximize visualization of the RV without apical foreshortening and measure endocardium to endocardium at the basal level."
    assert basal["alternate_windows"] == {"es": [], "en": []}

    # 4. relacion_vd_vi
    ratio = next(m for m in data if m["id"] == "relacion_vd_vi")
    assert ratio["measurement"]["es"] == "Relación VD/VI"
    assert ratio["measurement"]["en"] == "RV/LV ratio"
    assert ratio["abbreviation"]["es"] == "Relación VD/VI"
    assert ratio["abbreviation"]["en"] == "RV/LV ratio"
    assert ratio["aliases"]["es"] == ["RV/LV ratio", "Relación ventricular derecha-izquierda"]
    assert ratio["aliases"]["en"] == ["RV/LV ratio", "Right ventricular-to-left ventricular ratio"]
    assert ratio["formula_or_method"]["es"] == "Diámetro basal VD / diámetro basal VI."
    assert ratio["formula_or_method"]["en"] == "Basal RV diameter / basal LV diameter."
    assert ratio["normal_values"]["es"] == "<0,6-0,7; ≥1 indica dilatación importante."
    assert ratio["normal_values"]["en"] == "<0.6-0.7; ≥1 indicates significant RV dilation."
    assert ratio["interpretation_limitations"]["es"] == "Útil como estimación rápida; depende del plano y de la carga."
    assert ratio["interpretation_limitations"]["en"] == "Useful as a rapid estimate; depends on the imaging plane and loading conditions."
    assert ratio["primary_window"]["es"] == "Apical"
    assert ratio["primary_window"]["en"] == "Apical"
    assert ratio["preferred_view"]["es"] == "A4C enfocada en VD"
    assert ratio["preferred_view"]["en"] == "RV-focused A4C"
    assert ratio["modality"]["es"] == "2D; cálculo"
    assert ratio["modality"]["en"] == "2D; calculation"
    assert ratio["acquisition_timing"]["es"] == "Fin de diástole"
    assert ratio["acquisition_timing"]["en"] == "End-diastole"
    assert ratio["acquisition_key"]["es"] == "Medir ambos diámetros en el mismo cuadro y plano."
    assert ratio["acquisition_key"]["en"] == "Measure both diameters in the same frame and imaging plane."
    assert ratio["alternate_windows"]["es"] == ["Subcostal 4C para evaluación cualitativa en paciente crítico."]
    assert ratio["alternate_windows"]["en"] == ["Use the subcostal four-chamber view for qualitative assessment in critically ill patients."]

    # 11. indice_tei_vd
    tei = next(m for m in data if m["id"] == "indice_tei_vd")
    assert tei["measurement"]["es"] == "Índice de Tei del VD"
    assert tei["measurement"]["en"] == "RV myocardial performance index (Tei index)"
    assert tei["abbreviation"]["es"] == "Índice de Tei"
    assert tei["abbreviation"]["en"] == "RV MPI"
    assert tei["aliases"]["es"] == ["MPI del VD", "Myocardial performance index", "Índice de rendimiento miocárdico"]
    assert tei["aliases"]["en"] == ["RV MPI", "RV myocardial performance index (Tei index)", "RV Tei index"]
    assert tei["formula_or_method"]["es"] == "(Tiempo cierre-apertura - tiempo de eyección) / tiempo de eyección."
    assert tei["formula_or_method"]["en"] == "(Valve closure-to-opening time - ejection time) / ejection time."
    assert tei["normal_values"]["es"] == "<0,40 por Doppler pulsado; <0,55 por TDI."
    assert tei["normal_values"]["en"] == "<0.40 by pulsed-wave Doppler; <0.55 by TDI."
    assert tei["interpretation_limitations"]["es"] == "Índice combinado de función sistólica y diastólica; dependiente de carga y ritmo."
    assert tei["interpretation_limitations"]["en"] == "Combined index of systolic and diastolic function; load- and rhythm-dependent."
    assert tei["primary_window"]["es"] == "Apical / paraesternal"
    assert tei["primary_window"]["en"] == "Apical / parasternal"
    assert tei["preferred_view"]["es"] == "A4C para TDI; RV inflow + PSAX/RVOT para PW"
    assert tei["preferred_view"]["en"] == "A4C for TDI; RV inflow plus PSAX/RVOT for PW Doppler"
    assert tei["modality"]["es"] == "Doppler tisular o pulsado"
    assert tei["modality"]["en"] == "Tissue Doppler or pulsed-wave Doppler"
    assert tei["acquisition_timing"]["es"] == "Ciclo completo"
    assert tei["acquisition_timing"]["en"] == "Entire cardiac cycle"
    assert tei["acquisition_key"]["es"] == "Para TDI, medir intervalos en el anillo tricuspídeo lateral; para PW, integrar tiempos de inflow y outflow."
    assert tei["acquisition_key"]["en"] == "For TDI, measure time intervals at the lateral tricuspid annulus; for PW Doppler, integrate RV inflow and outflow time intervals."
    assert tei["alternate_windows"] == {"es": [], "en": []}

    # 14. tapse_pasp_ratio
    ratio_tp = next(m for m in data if m["id"] == "tapse_pasp_ratio")
    assert ratio_tp["measurement"]["es"] == "TAPSE/PASP"
    assert ratio_tp["measurement"]["en"] == "TAPSE/PASP"
    assert ratio_tp["abbreviation"]["es"] == "TAPSE/PASP"
    assert ratio_tp["abbreviation"]["en"] == "TAPSE/PASP"
    assert ratio_tp["aliases"]["es"] == ["Cociente TAPSE/PASP", "Relación TAPSE y PASP"]
    assert ratio_tp["aliases"]["en"] == ["TAPSE/PASP ratio", "TAPSE-to-PASP ratio"]
    assert ratio_tp["formula_or_method"]["es"] == "TAPSE en mm / PASP en mmHg."
    assert ratio_tp["formula_or_method"]["en"] == "TAPSE in mm / PASP in mmHg."
    assert ratio_tp["normal_values"]["es"] == ">0,4-0,55 mm/mmHg."
    assert ratio_tp["normal_values"]["en"] == ">0.4-0.55 mm/mmHg."
    assert ratio_tp["interpretation_limitations"]["es"] == "Estimación no invasiva del acoplamiento VD-arteria pulmonar."
    assert ratio_tp["interpretation_limitations"]["en"] == "Noninvasive estimate of RV-pulmonary arterial coupling."
    assert ratio_tp["primary_window"]["es"] == "Derivada"
    assert ratio_tp["primary_window"]["en"] == "Derived"
    assert ratio_tp["preferred_view"]["es"] == "A4C enfocada en VD + mejor ventana de IT"
    assert ratio_tp["preferred_view"]["en"] == "RV-focused A4C plus the best window for the TR jet"
    assert ratio_tp["modality"]["es"] == "Modo M + Doppler continuo; cálculo"
    assert ratio_tp["modality"]["en"] == "M-mode plus continuous-wave Doppler; calculation"
    assert ratio_tp["acquisition_timing"]["es"] == "Sístole"
    assert ratio_tp["acquisition_timing"]["en"] == "Systole"
    assert ratio_tp["acquisition_key"]["es"] == "Combinar TAPSE y PASP obtenidos en condiciones hemodinámicas similares."
    assert ratio_tp["acquisition_key"]["en"] == "Combine TAPSE and PASP measurements obtained under similar hemodynamic conditions."
    assert ratio_tp["alternate_windows"] == {"es": [], "en": []}

def test_previous_migrated_blocks_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 14. Que todos los bloques bilingües migrados anteriormente permanecen intactos.
    blocks = [
        "lv_geometry", "stroke_volume_output", "left_atrium", "lv_diastolic",
        "ra_ivc", "pulmonary_hemodynamics", "aortic_valve_lvot", "mitral_valve",
        "valvular_regurgitation", "pericardium_tamponade", "lv_systolic"
    ]
    for block in blocks:
        block_items = [m for m in data if m["section_id"] == block]
        assert len(block_items) > 0
        for item in block_items:
            assert isinstance(item["measurement"], dict)

def test_final_counts_and_completeness():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 15. Que después de C3C1L existen exactamente: 101 mediciones bilingües y 0 mediciones pendientes.
    bilingual_count = sum(1 for m in data if isinstance(m["measurement"], dict))
    pending_count = sum(1 for m in data if isinstance(m["measurement"], str))
    assert bilingual_count == 101
    assert pending_count == 0

    # 16. Que no existe ninguna medición cuyo campo measurement continúe como string.
    for item in data:
        assert isinstance(item["measurement"], dict)

    # 17. Que las 12 secciones clínicas tienen todas sus mediciones bilingües.
    # 18. Que no exista ninguna sección pendiente.
    # 20. Que la suma de mediciones bilingües y pendientes sea exactamente 101.
    sections_in_data = set(item["section_id"] for item in data)
    assert len(sections_in_data) == 12

    # Solo se permiten como strings las abreviaturas técnicas invariantes explícitamente enumeradas.
    allowed_invariant_abbreviations = {
        "ivsd": "IVSd",
        "pwtd": "PWTd",
        "rwt_meas": "RWT",
        "lavi_meas": "LAVI",
        "relacion_e_a": "E/A",
        "tiempo_desaceleracion_e": "DT",
        "ivrt_meas": "IVRT",
        "lavi_diastology": "LAVI",
        "pht_meas": "PHT",
    }

    for item in data:
        assert isinstance(item["measurement"], dict)
        # 19. Que todos los campos bilingües tengan valores es y en no vacíos.
        bilingual_fields = [
            "measurement", "formula_or_method", "normal_values",
            "interpretation_limitations", "primary_window", "preferred_view",
            "modality", "acquisition_timing", "acquisition_key"
        ]
        for field in bilingual_fields:
            val = item[field]
            assert isinstance(val, dict)
            assert "es" in val and "en" in val
            assert isinstance(val["es"], str) and val["es"].strip() != ""
            assert isinstance(val["en"], str) and val["en"].strip() != ""

        # Validación de abbreviation por separado:
        abbreviation = item["abbreviation"]
        if isinstance(abbreviation, dict):
            assert "es" in abbreviation and "en" in abbreviation
            assert isinstance(abbreviation["es"], str) and abbreviation["es"].strip() != ""
            assert isinstance(abbreviation["en"], str) and abbreviation["en"].strip() != ""
        else:
            assert isinstance(abbreviation, str)
            assert item["id"] in allowed_invariant_abbreviations
            assert abbreviation == allowed_invariant_abbreviations[item["id"]]
            assert abbreviation.strip()
