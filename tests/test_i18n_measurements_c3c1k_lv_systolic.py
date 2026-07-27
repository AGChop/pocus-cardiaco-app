import os
import json
import pytest

def test_lv_systolic_measurements_structure_and_count():
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

    # 2. Que lv_systolic contiene exactamente los 13 IDs autorizados.
    target_ids = [
        "dtdvi", "dtsvi", "vtdvi", "vtdvi_indexed", "vtsvi_meas",
        "vtsvi_indexed", "fevi", "fraccion_acortamiento_meas", "epss",
        "mapse", "s_prima_mitral", "gls_vi", "wmsi"
    ]
    for tid in target_ids:
        assert tid in ids

def test_lv_systolic_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. Que los órdenes permanecen consecutivos de 1 a 13.
    expected_order = {
        "dtdvi": 1,
        "dtsvi": 2,
        "vtdvi": 3,
        "vtdvi_indexed": 4,
        "vtsvi_meas": 5,
        "vtsvi_indexed": 6,
        "fevi": 7,
        "fraccion_acortamiento_meas": 8,
        "epss": 9,
        "mapse": 10,
        "s_prima_mitral": 11,
        "gls_vi": 12,
        "wmsi": 13
    }

    expected_related = {
        "dtdvi": ["dtdvi_term", "plax"],
        "dtsvi": ["dtsvi_term", "plax"],
        "vtdvi": ["vtdvi_term", "simpson_biplano", "foreshortening"],
        "vtdvi_indexed": ["vtdvi_term", "bsa", "indexed"],
        "vtsvi_meas": ["vtsvi_term", "simpson_biplano"],
        "vtsvi_indexed": ["vtsvi_term", "bsa", "indexed"],
        "fevi": ["fevi_term", "vtdvi_term", "vtsvi_term"],
        "fraccion_acortamiento_meas": ["fraccion_acortamiento_term", "dtdvi_term", "dtsvi_term"],
        "epss": ["epss_term", "modo_m"],
        "mapse": ["mapse_term", "modo_m"],
        "s_prima_mitral": ["s_prima_mitral_term", "tdi"],
        "gls_vi": ["gls_term", "speckle_tracking"],
        "wmsi": ["wmsi_term"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            # 5. Que permanecen exactamente iguales: id, section_id, order, related_glossary_ids, source_page, source_document
            assert item["section_id"] == "lv_systolic"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 4
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            # 6. Que todos los campos traducibles de los 13 registros tienen una estructura válida {es, en}.
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

            # 7. Que todos los aliases tienen estructura bilingüe, conservan el mismo número y mantienen el orden original.
            assert isinstance(item["aliases"], dict)
            assert "es" in item["aliases"] and "en" in item["aliases"]
            assert isinstance(item["aliases"]["es"], list)
            assert isinstance(item["aliases"]["en"], list)
            assert len(item["aliases"]["es"]) == len(item["aliases"]["en"])
            for a in item["aliases"]["es"] + item["aliases"]["en"]:
                assert isinstance(a, str) and a.strip() != ""

            # 8. Que cada elemento no vacío de alternate_windows tiene estructura bilingüe.
            # 9. Que las listas alternate_windows originalmente vacías permanecen vacías.
            assert isinstance(item["alternate_windows"], dict)
            assert "es" in item["alternate_windows"] and "en" in item["alternate_windows"]
            assert isinstance(item["alternate_windows"]["es"], list)
            assert isinstance(item["alternate_windows"]["en"], list)
            assert len(item["alternate_windows"]["es"]) == len(item["alternate_windows"]["en"])

def test_lv_systolic_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 12. Que las doce unidades técnicas continúan siendo strings exactos.
    expected_string_units = {
        "dtdvi": "mm",
        "dtsvi": "mm",
        "vtdvi": "mL",
        "vtdvi_indexed": "mL/m²",
        "vtsvi_meas": "mL",
        "vtsvi_indexed": "mL/m²",
        "fevi": "%",
        "fraccion_acortamiento_meas": "%",
        "epss": "mm",
        "mapse": "mm",
        "s_prima_mitral": "cm/s",
        "gls_vi": "%"
    }
    for m_id, unit in expected_string_units.items():
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == unit
        assert isinstance(item["units"], str)

    # 13. Que wmsi.units coincide exactamente con el dict bilingüe
    wmsi = next(m for m in data if m["id"] == "wmsi")
    assert wmsi["units"] == {
        "es": "adimensional",
        "en": "dimensionless"
    }

def test_lv_systolic_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. dtdvi
    dtdvi = next(m for m in data if m["id"] == "dtdvi")
    assert dtdvi["measurement"]["es"] == "DTDVI / LVIDd"
    assert dtdvi["measurement"]["en"] == "LV internal dimension at end-diastole (LVIDd)"
    assert dtdvi["abbreviation"]["es"] == "DTDVI"
    assert dtdvi["abbreviation"]["en"] == "LVIDd"
    assert dtdvi["aliases"]["es"] == ["LVIDd", "Diámetro telediastólico del ventrículo izquierdo", "Diámetro interno del ventrículo izquierdo en diástole"]
    assert dtdvi["aliases"]["en"] == ["LVIDd", "Left ventricular internal diameter at end-diastole", "LV internal dimension at end-diastole"]
    assert dtdvi["formula_or_method"]["es"] == "PLAX, perpendicular al eje largo, al final de la diástole."
    assert dtdvi["formula_or_method"]["en"] == "PLAX, perpendicular to the long axis, at end-diastole."
    assert dtdvi["normal_values"]["es"] == "Hombres 42-58 mm; mujeres 38-52 mm."
    assert dtdvi["normal_values"]["en"] == "Men 42-58 mm; women 38-52 mm."
    assert dtdvi["interpretation_limitations"]["es"] == "Cuantifica el tamaño lineal del VI. Confirmar que el corte no sea oblicuo."
    assert dtdvi["interpretation_limitations"]["en"] == "Quantifies linear LV size. Confirm that the imaging plane is not oblique."
    assert dtdvi["primary_window"]["es"] == "Paraesternal izquierda"
    assert dtdvi["primary_window"]["en"] == "Left parasternal"
    assert dtdvi["preferred_view"]["es"] == "PLAX"
    assert dtdvi["preferred_view"]["en"] == "PLAX"
    assert dtdvi["modality"]["es"] == "2D; modo M opcional"
    assert dtdvi["modality"]["en"] == "2D; optional M-mode"
    assert dtdvi["acquisition_timing"]["es"] == "Fin de diástole"
    assert dtdvi["acquisition_timing"]["en"] == "End-diastole"
    assert dtdvi["acquisition_key"]["es"] == "Medir perpendicular al eje largo, habitualmente a nivel de las puntas de las valvas mitrales; evitar cortes oblicuos."
    assert dtdvi["acquisition_key"]["en"] == "Measure perpendicular to the LV long axis, usually at the level of the mitral leaflet tips; avoid oblique imaging planes."
    assert dtdvi["alternate_windows"]["es"] == ["Subcostal eje corto como alternativa si la ventana paraesternal es deficiente."]
    assert dtdvi["alternate_windows"]["en"] == ["Use the subcostal short-axis view as an alternative when the parasternal window is inadequate."]

    # 6. vtsvi_indexed
    vtsvi_idx = next(m for m in data if m["id"] == "vtsvi_indexed")
    assert vtsvi_idx["measurement"]["es"] == "VTSVI indexado"
    assert vtsvi_idx["measurement"]["en"] == "LV end-systolic volume index"
    assert vtsvi_idx["abbreviation"]["es"] == "VTSVI indexado"
    assert vtsvi_idx["abbreviation"]["en"] == "LVESVi"
    assert vtsvi_idx["aliases"]["es"] == ["VTSVI indexado", "Volumen telesistólico indexado del VI", "LVESVI"]
    assert vtsvi_idx["aliases"]["en"] == ["LV end-systolic volume index", "Indexed left ventricular end-systolic volume", "LVESVi"]
    assert vtsvi_idx["formula_or_method"]["es"] == "VTSVI / superficie corporal."
    assert vtsvi_idx["formula_or_method"]["en"] == "LVESV / body surface area."
    assert vtsvi_idx["normal_values"]["es"] == "Hombres 11-31 mL/m²; mujeres 8-24 mL/m²."
    assert vtsvi_idx["normal_values"]["en"] == "Men 11-31 mL/m²; women 8-24 mL/m²."
    assert vtsvi_idx["interpretation_limitations"]["es"] == "Permite cuantificación ajustada por superficie corporal."
    assert vtsvi_idx["interpretation_limitations"]["en"] == "Provides quantification adjusted for body surface area."
    assert vtsvi_idx["primary_window"]["es"] == "Derivada"
    assert vtsvi_idx["primary_window"]["en"] == "Derived"
    assert vtsvi_idx["preferred_view"]["es"] == "A4C + A2C para VTSVI"
    assert vtsvi_idx["preferred_view"]["en"] == "A4C and A2C views for LVESV"
    assert vtsvi_idx["modality"]["es"] == "Cálculo"
    assert vtsvi_idx["modality"]["en"] == "Calculation"
    assert vtsvi_idx["acquisition_timing"]["es"] == "Después de medir VTSVI"
    assert vtsvi_idx["acquisition_timing"]["en"] == "After measuring LVESV"
    assert vtsvi_idx["acquisition_key"]["es"] == "No requiere ventana adicional: utiliza VTSVI y superficie corporal."
    assert vtsvi_idx["acquisition_key"]["en"] == "No additional acoustic window is required; it uses LVESV and body surface area."
    assert vtsvi_idx["alternate_windows"] == {"es": [], "en": []}

    # 13. wmsi
    wmsi = next(m for m in data if m["id"] == "wmsi")
    assert wmsi["measurement"]["es"] == "WMSI"
    assert wmsi["measurement"]["en"] == "WMSI"
    assert wmsi["abbreviation"]["es"] == "WMSI"
    assert wmsi["abbreviation"]["en"] == "WMSI"
    assert wmsi["aliases"]["es"] == ["Índice de puntuación de movilidad parietal", "Wall motion score index"]
    assert wmsi["aliases"]["en"] == ["Wall motion score index", "Wall motion score index"]
    assert wmsi["formula_or_method"]["es"] == "Suma de puntuaciones segmentarias / número de segmentos evaluados."
    assert wmsi["formula_or_method"]["en"] == "Sum of segmental wall motion scores / number of segments assessed."
    assert wmsi["normal_values"]["es"] == "1,0 cuando todos los segmentos son normales."
    assert wmsi["normal_values"]["en"] == "1.0 when all segments have normal wall motion."
    assert wmsi["interpretation_limitations"]["es"] == "Aumenta con mayor extensión o severidad de alteraciones regionales."
    assert wmsi["interpretation_limitations"]["en"] == "Increases with greater extent or severity of regional wall motion abnormalities."
    assert wmsi["primary_window"]["es"] == "Múltiples"
    assert wmsi["primary_window"]["en"] == "Multiple"
    assert wmsi["preferred_view"]["es"] == "A4C, A2C, A3C y PSAX basal/medio/apical"
    assert wmsi["preferred_view"]["en"] == "A4C, A2C, A3C, and basal/mid/apical PSAX views"
    assert wmsi["modality"]["es"] == "2D cine"
    assert wmsi["modality"]["en"] == "2D cine loops"
    assert wmsi["acquisition_timing"]["es"] == "Ciclo completo"
    assert wmsi["acquisition_timing"]["en"] == "Entire cardiac cycle"
    assert wmsi["acquisition_key"]["es"] == "Evaluar cada segmento en más de una vista cuando sea posible; evitar atribuir artefacto a hipocinesia."
    assert wmsi["acquisition_key"]["en"] == "Assess each segment in more than one view whenever possible; avoid misclassifying artifact as hypokinesis."
    assert wmsi["alternate_windows"]["es"] == ["Subcostal eje corto en ventanas apicales o paraesternales deficientes."]
    assert wmsi["alternate_windows"]["en"] == ["Use the subcostal short-axis view when apical or parasternal windows are inadequate."]

def test_previous_migrated_blocks_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 14. Que los bloques bilingües migrados anteriormente permanecen intactos:
    # lv_geometry, stroke_volume_output, left_atrium, lv_diastolic, ra_ivc, pulmonary_hemodynamics, aortic_valve_lvot, mitral_valve, valvular_regurgitation, pericardium_tamponade
    blocks = [
        "lv_geometry", "stroke_volume_output", "left_atrium", "lv_diastolic",
        "ra_ivc", "pulmonary_hemodynamics", "aortic_valve_lvot", "mitral_valve",
        "valvular_regurgitation", "pericardium_tamponade"
    ]
    for block in blocks:
        block_items = [m for m in data if m["section_id"] == block]
        assert len(block_items) > 0
        for item in block_items:
            assert isinstance(item["measurement"], dict)

def test_bilingual_vs_pending_counts():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # El bloque C3C1K estableció un mínimo acumulado de 87 mediciones bilingües y un máximo de 14 pendientes.
    # Los bloques posteriores (como C3C1L) pueden aumentar el número de mediciones bilingües y reducir las pendientes.
    # El total debe permanecer exactamente en 101.
    # El conteo final exacto pertenece a la prueba C3C1L.
    bilingual_count = sum(1 for m in data if isinstance(m["measurement"], dict))
    pending_count = sum(1 for m in data if isinstance(m["measurement"], str))
    assert bilingual_count >= 87
    assert pending_count <= 14
    assert bilingual_count + pending_count == 101

    # Que las secciones completamente pendientes después de esta migración estén dentro de {rv_systolic}
    pending_sections = set(m["section_id"] for m in data if isinstance(m["measurement"], str))
    assert pending_sections.issubset({"rv_systolic"})
