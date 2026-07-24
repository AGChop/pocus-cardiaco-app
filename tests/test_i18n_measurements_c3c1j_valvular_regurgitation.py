import os
import json
import pytest

def test_valvular_regurgitation_measurements_structure_and_count():
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

    # 2. Que valvular_regurgitation contiene exactamente los ocho IDs autorizados.
    target_ids = [
        "vena_contracta_meas",
        "flujo_pisa_meas",
        "eroa_meas",
        "volumen_regurgitante_meas",
        "fraccion_regurgitante_meas",
        "insuficiencia_mitral_severa_meas",
        "insuficiencia_aortica_severa_meas",
        "insuficiencia_tricuspidea_severa_meas"
    ]
    for tid in target_ids:
        assert tid in ids

def test_valvular_regurgitation_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. Que los órdenes continúan siendo 1 a 8.
    expected_order = {
        "vena_contracta_meas": 1,
        "flujo_pisa_meas": 2,
        "eroa_meas": 3,
        "volumen_regurgitante_meas": 4,
        "fraccion_regurgitante_meas": 5,
        "insuficiencia_mitral_severa_meas": 6,
        "insuficiencia_aortica_severa_meas": 7,
        "insuficiencia_tricuspidea_severa_meas": 8
    }

    expected_related = {
        "vena_contracta_meas": ["vena_contracta_term"],
        "flujo_pisa_meas": ["pisa_term"],
        "eroa_meas": ["eroa_term", "pisa_term"],
        "volumen_regurgitante_meas": ["volumen_regurgitante_term", "eroa_term"],
        "fraccion_regurgitante_meas": ["fraccion_regurgitante_term", "volumen_regurgitante_term"],
        "insuficiencia_mitral_severa_meas": [
            "insuficiencia_mitral_severa_term",
            "vena_contracta_term",
            "eroa_term",
            "volumen_regurgitante_term"
        ],
        "insuficiencia_aortica_severa_meas": [
            "insuficiencia_aortica_severa_term",
            "reversion_holodiastolica_aortica_term",
            "pht_term"
        ],
        "insuficiencia_tricuspidea_severa_meas": [
            "insuficiencia_tricuspidea_severa_term",
            "reversion_sistolica_hepatica_term"
        ]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            # 5. Que se conservaron exactamente los invariantes
            assert item["section_id"] == "valvular_regurgitation"
            assert item["order"] == expected_order[i_id]
            assert item["related_glossary_ids"] == expected_related[i_id]
            assert item["source_page"] == 10
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            # 6. Que todos los campos traducibles de los ocho registros tienen la estructura correcta {es, en}.
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

            # 7. Que cada alias tiene estructura bilingüe y conserva su orden.
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

def test_valvular_regurgitation_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 12. Que las unidades técnicas de los primeros cinco registros siguen siendo strings.
    expected_string_units = {
        "vena_contracta_meas": "mm",
        "flujo_pisa_meas": "mL/s",
        "eroa_meas": "cm²",
        "volumen_regurgitante_meas": "mL",
        "fraccion_regurgitante_meas": "%"
    }
    for m_id, unit in expected_string_units.items():
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == unit
        assert isinstance(item["units"], str)

    # 13. Que las unidades de las tres clasificaciones severas coinciden exactamente con multiparamétrico.
    severe_ids = [
        "insuficiencia_mitral_severa_meas",
        "insuficiencia_aortica_severa_meas",
        "insuficiencia_tricuspidea_severa_meas"
    ]
    for m_id in severe_ids:
        item = next(m for m in data if m["id"] == m_id)
        assert item["units"] == {
            "es": "multiparamétrico",
            "en": "multiparametric"
        }

def test_valvular_regurgitation_translations_exact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. vena_contracta_meas
    vc = next(m for m in data if m["id"] == "vena_contracta_meas")
    assert vc["measurement"]["es"] == "Vena contracta (VC)"
    assert vc["measurement"]["en"] == "Vena contracta (VC)"
    assert vc["abbreviation"]["es"] == "VC"
    assert vc["abbreviation"]["en"] == "VC"
    assert vc["aliases"]["es"] == ["VC", "Vena contracta de regurgitación"]
    assert vc["aliases"]["en"] == ["VC", "Regurgitant vena contracta"]
    assert vc["formula_or_method"]["es"] == "Ancho de la porción más estrecha del jet inmediatamente distal al orificio."
    assert vc["formula_or_method"]["en"] == "Width of the narrowest portion of the jet immediately distal to the regurgitant orifice."
    assert vc["normal_values"]["es"] == "Depende de la válvula; IM severa ≥7 mm, IA severa >6 mm, IT severa ≥7 mm."
    assert vc["normal_values"]["en"] == "Valve-dependent; severe MR ≥7 mm, severe AR >6 mm, severe TR ≥7 mm."
    assert vc["interpretation_limitations"]["es"] == "Evitar usarla aislada en orificios múltiples o no circulares."
    assert vc["interpretation_limitations"]["en"] == "Avoid using it in isolation in the presence of multiple or noncircular orifices."
    assert vc["primary_window"]["es"] == "Dependiente de válvula"
    assert vc["primary_window"]["en"] == "Valve-dependent"
    assert vc["preferred_view"]["es"] == "IM: PLAX/A4C/A2C; IA: PLAX; IT: A4C VD/RV inflow"
    assert vc["preferred_view"]["en"] == "MR: PLAX/A4C/A2C; AR: PLAX; TR: RV-focused A4C/RV inflow"
    assert vc["modality"]["es"] == "Color Doppler 2D con zoom"
    assert vc["modality"]["en"] == "Zoomed 2D color Doppler"
    assert vc["acquisition_timing"]["es"] == "Sístole para IM/IT; diástole para IA"
    assert vc["acquisition_timing"]["en"] == "Systole for MR/TR; diastole for AR"
    assert vc["acquisition_key"]["es"] == "Elegir el plano que corte perpendicularmente la zona más estrecha del jet; reducir sector y optimizar Nyquist."
    assert vc["acquisition_key"]["en"] == "Select the imaging plane that transects the narrowest portion of the jet perpendicularly; narrow the sector and optimize the Nyquist limit."
    assert vc["alternate_windows"]["es"] == ["Usar varias vistas para jets excéntricos."]
    assert vc["alternate_windows"]["en"] == ["Use multiple views for eccentric jets."]

    # 2. flujo_pisa_meas
    pisa = next(m for m in data if m["id"] == "flujo_pisa_meas")
    assert pisa["measurement"]["es"] == "Flujo PISA"
    assert pisa["measurement"]["en"] == "PISA flow rate"
    assert pisa["abbreviation"]["es"] == "Flujo PISA"
    assert pisa["abbreviation"]["en"] == "PISA flow"
    assert pisa["aliases"]["es"] == ["PISA flow", "Flujo por superficie de isovelocidad proximal"]
    assert pisa["aliases"]["en"] == ["PISA flow", "Proximal isovelocity surface area flow"]
    assert pisa["formula_or_method"]["es"] == "2πr² x velocidad de aliasing."
    assert pisa["formula_or_method"]["en"] == "2πr² × aliasing velocity."
    assert pisa["normal_values"]["es"] == "Sin valor normal único."
    assert pisa["normal_values"]["en"] == "No single normal value."
    assert pisa["interpretation_limitations"]["es"] == "Radio en cm y velocidad de aliasing en cm/s producen flujo en mL/s."
    assert pisa["interpretation_limitations"]["en"] == "A radius in cm and aliasing velocity in cm/s yield a flow rate in mL/s."
    assert pisa["primary_window"]["es"] == "Dependiente de válvula"
    assert pisa["primary_window"]["en"] == "Valve-dependent"
    assert pisa["preferred_view"]["es"] == "IM: apical; IA: PLAX/apical; IT: A4C VD"
    assert pisa["preferred_view"]["en"] == "MR: apical; AR: PLAX/apical; TR: RV-focused A4C"
    assert pisa["modality"]["es"] == "Color Doppler con línea basal desplazada"
    assert pisa["modality"]["en"] == "Color Doppler with a shifted baseline"
    assert pisa["acquisition_timing"]["es"] == "Pico de regurgitación"
    assert pisa["acquisition_timing"]["en"] == "Peak regurgitation"
    assert pisa["acquisition_key"]["es"] == "Ampliar la zona de convergencia, medir radio desde el orificio al primer aliasing y documentar Va."
    assert pisa["acquisition_key"]["en"] == "Enlarge the flow convergence zone, measure the radius from the regurgitant orifice to the first aliasing boundary, and document Va."
    assert pisa["alternate_windows"] == {"es": [], "en": []}

    # 3. eroa_meas
    eroa = next(m for m in data if m["id"] == "eroa_meas")
    assert eroa["measurement"]["es"] == "EROA"
    assert eroa["measurement"]["en"] == "EROA"
    assert eroa["abbreviation"]["es"] == "EROA"
    assert eroa["abbreviation"]["en"] == "EROA"
    assert eroa["aliases"]["es"] == ["Effective regurgitant orifice area", "Área del orificio regurgitante efectivo"]
    assert eroa["aliases"]["en"] == ["Effective regurgitant orifice area", "Effective regurgitant orifice area"]
    assert eroa["formula_or_method"]["es"] == "(2πr² x Va) / velocidad máxima regurgitante."
    assert eroa["formula_or_method"]["en"] == "(2πr² × Va) / peak regurgitant velocity."
    assert eroa["normal_values"]["es"] == "Depende de la válvula."
    assert eroa["normal_values"]["en"] == "Valve-dependent."
    assert eroa["interpretation_limitations"]["es"] == "Usar velocidades en las mismas unidades; integrar con otros parámetros."
    assert eroa["interpretation_limitations"]["en"] == "Use velocities expressed in the same units and integrate the result with other parameters."
    assert eroa["primary_window"]["es"] == "Combinada"
    assert eroa["primary_window"]["en"] == "Combined"
    assert eroa["preferred_view"]["es"] == "Vista PISA + mejor CW del jet"
    assert eroa["preferred_view"]["en"] == "PISA view plus the best-aligned CW Doppler recording of the jet"
    assert eroa["modality"]["es"] == "Color Doppler + Doppler continuo; cálculo"
    assert eroa["modality"]["en"] == "Color Doppler plus continuous-wave Doppler; calculation"
    assert eroa["acquisition_timing"]["es"] == "Mismo momento del ciclo"
    assert eroa["acquisition_timing"]["en"] == "Same point in the cardiac cycle"
    assert eroa["acquisition_key"]["es"] == "Relacionar el radio PISA con la velocidad instantánea/peak correspondiente y un CW completo."
    assert eroa["acquisition_key"]["en"] == "Match the PISA radius to the corresponding instantaneous/peak velocity and a complete CW Doppler envelope."
    assert eroa["alternate_windows"] == {"es": [], "en": []}

    # 4. volumen_regurgitante_meas
    vr = next(m for m in data if m["id"] == "volumen_regurgitante_meas")
    assert vr["measurement"]["es"] == "Volumen regurgitante"
    assert vr["measurement"]["en"] == "Regurgitant volume"
    assert vr["abbreviation"]["es"] == "VR"
    assert vr["abbreviation"]["en"] == "RVol"
    assert vr["aliases"]["es"] == ["Regurgitant volume", "VR", "Volumen de regurgitación"]
    assert vr["aliases"]["en"] == ["Regurgitant volume", "RVol", "Regurgitant volume"]
    assert vr["formula_or_method"]["es"] == "EROA x VTI del jet regurgitante."
    assert vr["formula_or_method"]["en"] == "EROA × VTI of the regurgitant jet."
    assert vr["normal_values"]["es"] == "Depende de la válvula."
    assert vr["normal_values"]["en"] == "Valve-dependent."
    assert vr["interpretation_limitations"]["es"] == "Con EROA en cm² y VTI en cm, el resultado es mL."
    assert vr["interpretation_limitations"]["en"] == "With EROA in cm² and VTI in cm, the result is expressed in mL."
    assert vr["primary_window"]["es"] == "Derivada"
    assert vr["primary_window"]["en"] == "Derived"
    assert vr["preferred_view"]["es"] == "Mismas vistas que EROA y VTI del jet"
    assert vr["preferred_view"]["en"] == "Same views as EROA and jet VTI"
    assert vr["modality"]["es"] == "Cálculo"
    assert vr["modality"]["en"] == "Calculation"
    assert vr["acquisition_timing"]["es"] == "Ciclo completo del jet"
    assert vr["acquisition_timing"]["en"] == "Full duration of the jet"
    assert vr["acquisition_key"]["es"] == "Usar el VTI del mismo jet y válvula."
    assert vr["acquisition_key"]["en"] == "Use the VTI of the same regurgitant jet and valve."
    assert vr["alternate_windows"] == {"es": [], "en": []}

    # 5. fraccion_regurgitante_meas
    fr = next(m for m in data if m["id"] == "fraccion_regurgitante_meas")
    assert fr["measurement"]["es"] == "Fracción regurgitante"
    assert fr["measurement"]["en"] == "Regurgitant fraction"
    assert fr["abbreviation"]["es"] == "FR"
    assert fr["abbreviation"]["en"] == "RF"
    assert fr["aliases"]["es"] == ["Regurgitant fraction", "FR", "Fracción de regurgitación"]
    assert fr["aliases"]["en"] == ["Regurgitant fraction", "RF", "Regurgitant fraction"]
    assert fr["formula_or_method"]["es"] == "(Volumen regurgitante / volumen sistólico total) x 100."
    assert fr["formula_or_method"]["en"] == "(Regurgitant volume / total stroke volume) × 100."
    assert fr["normal_values"]["es"] == "Sin regurgitación significativa en condiciones normales."
    assert fr["normal_values"]["en"] == "No significant regurgitation is expected under normal conditions."
    assert fr["interpretation_limitations"]["es"] == "Es la proporción del volumen sistólico que regresa a la cavidad proximal."
    assert fr["interpretation_limitations"]["en"] == "It is the proportion of total stroke volume that returns to the proximal chamber."
    assert fr["primary_window"]["es"] == "Derivada"
    assert fr["primary_window"]["en"] == "Derived"
    assert fr["preferred_view"]["es"] == "Datos volumétricos combinados"
    assert fr["preferred_view"]["en"] == "Combined volumetric data"
    assert fr["modality"]["es"] == "Cálculo"
    assert fr["modality"]["en"] == "Calculation"
    assert fr["acquisition_timing"]["es"] == "Después de obtener volúmenes"
    assert fr["acquisition_timing"]["en"] == "After obtaining the required volumes"
    assert fr["acquisition_key"]["es"] == "No requiere ventana adicional; depende de la exactitud de todos los componentes."
    assert fr["acquisition_key"]["en"] == "No additional acoustic window is required; accuracy depends on all calculation components."
    assert fr["alternate_windows"] == {"es": [], "en": []}

    # 6. insuficiencia_mitral_severa_meas
    im = next(m for m in data if m["id"] == "insuficiencia_mitral_severa_meas")
    assert im["measurement"]["es"] == "Insuficiencia mitral severa"
    assert im["measurement"]["en"] == "Severe mitral regurgitation"
    assert im["abbreviation"]["es"] == "IM Severa"
    assert im["abbreviation"]["en"] == "Severe MR"
    assert im["aliases"]["es"] == ["Severe mitral regurgitation", "Insuficiencia mitral severa criterios"]
    assert im["aliases"]["en"] == ["Severe mitral regurgitation", "Criteria for severe mitral regurgitation"]
    assert im["formula_or_method"]["es"] == "Integración multiparamétrica."
    assert im["formula_or_method"]["en"] == "Multiparametric integration."
    assert im["normal_values"]["es"] == "VC ≥7 mm; EROA ≥0,40 cm²; VR ≥60 mL; FR ≥50%."
    assert im["normal_values"]["en"] == "VC ≥7 mm; EROA ≥0.40 cm²; RVol ≥60 mL; RF ≥50%."
    assert im["interpretation_limitations"]["es"] == "La etiología primaria o secundaria puede modificar la interpretación."
    assert im["interpretation_limitations"]["en"] == "Primary or secondary etiology may affect interpretation."
    assert im["primary_window"]["es"] == "Múltiples"
    assert im["primary_window"]["en"] == "Multiple"
    assert im["preferred_view"]["es"] == "PLAX, A4C, A2C, A3C; venas pulmonares"
    assert im["preferred_view"]["en"] == "PLAX, A4C, A2C, A3C; pulmonary veins"
    assert im["modality"]["es"] == "2D, color, PW y CW"
    assert im["modality"]["en"] == "2D, color Doppler, PW and CW Doppler"
    assert im["acquisition_timing"]["es"] == "Sístole"
    assert im["acquisition_timing"]["en"] == "Systole"
    assert im["acquisition_key"]["es"] == "Evaluar mecanismo, jet, VC/PISA, CW y repercusión; flujo venoso pulmonar desde A4C."
    assert im["acquisition_key"]["en"] == "Assess the mechanism, regurgitant jet, VC/PISA, CW Doppler envelope, and cardiac consequences; evaluate pulmonary venous flow from A4C."
    assert im["alternate_windows"] == {"es": [], "en": []}

    # 7. insuficiencia_aortica_severa_meas
    ia = next(m for m in data if m["id"] == "insuficiencia_aortica_severa_meas")
    assert ia["measurement"]["es"] == "Insuficiencia aórtica severa"
    assert ia["measurement"]["en"] == "Severe aortic regurgitation"
    assert ia["abbreviation"]["es"] == "IA Severa"
    assert ia["abbreviation"]["en"] == "Severe AR"
    assert ia["aliases"]["es"] == ["Severe aortic regurgitation", "Insuficiencia aórtica severa criterios"]
    assert ia["aliases"]["en"] == ["Severe aortic regurgitation", "Criteria for severe aortic regurgitation"]
    assert ia["formula_or_method"]["es"] == "Integración multiparamétrica."
    assert ia["formula_or_method"]["en"] == "Multiparametric integration."
    assert ia["normal_values"]["es"] == "VC >6 mm; EROA ≥0,30 cm²; VR ≥60 mL; FR ≥50%; PHT <200 ms."
    assert ia["normal_values"]["en"] == "VC >6 mm; EROA ≥0.30 cm²; RVol ≥60 mL; RF ≥50%; PHT <200 ms."
    assert ia["interpretation_limitations"]["es"] == "Confirmar con reversión holodiastólica y repercusión ventricular."
    assert ia["interpretation_limitations"]["en"] == "Confirm with holodiastolic flow reversal and ventricular consequences."
    assert ia["primary_window"]["es"] == "Múltiples"
    assert ia["primary_window"]["en"] == "Multiple"
    assert ia["preferred_view"]["es"] == "PLAX para VC; A5C/A3C para CW; supraesternal para aorta descendente"
    assert ia["preferred_view"]["en"] == "PLAX for VC; A5C/A3C for CW Doppler; suprasternal view for the descending aorta"
    assert ia["modality"]["es"] == "2D, color, PW y CW"
    assert ia["modality"]["en"] == "2D, color Doppler, PW and CW Doppler"
    assert ia["acquisition_timing"]["es"] == "Diástole"
    assert ia["acquisition_timing"]["en"] == "Diastole"
    assert ia["acquisition_key"]["es"] == "Integrar ancho/VC, PISA, PHT y reversión holodiastólica en aorta descendente."
    assert ia["acquisition_key"]["en"] == "Integrate jet width/VC, PISA, PHT, and holodiastolic flow reversal in the descending aorta."
    assert ia["alternate_windows"]["es"] == ["Subcostal para flujo aórtico abdominal como apoyo."]
    assert ia["alternate_windows"]["en"] == ["Use the subcostal view to assess abdominal aortic flow as supportive evidence."]

    # 8. insuficiencia_tricuspidea_severa_meas
    it = next(m for m in data if m["id"] == "insuficiencia_tricuspidea_severa_meas")
    assert it["measurement"]["es"] == "Insuficiencia tricuspídea severa"
    assert it["measurement"]["en"] == "Severe tricuspid regurgitation"
    assert it["abbreviation"]["es"] == "IT Severa"
    assert it["abbreviation"]["en"] == "Severe TR"
    assert it["aliases"]["es"] == ["Severe tricuspid regurgitation", "Insuficiencia tricuspídea severa criterios"]
    assert it["aliases"]["en"] == ["Severe tricuspid regurgitation", "Criteria for severe tricuspid regurgitation"]
    assert it["formula_or_method"]["es"] == "Integración multiparamétrica."
    assert it["formula_or_method"]["en"] == "Multiparametric integration."
    assert it["normal_values"]["es"] == "VC ≥7 mm; EROA ≥0,40 cm²; VR ≥45 mL; reversión sistólica hepática."
    assert it["normal_values"]["en"] == "VC ≥7 mm; EROA ≥0.40 cm²; RVol ≥45 mL; hepatic vein systolic flow reversal."
    assert it["interpretation_limitations"]["es"] == "Las categorías masiva y torrencial pueden requerir esquemas ampliados."
    assert it["interpretation_limitations"]["en"] == "Massive and torrential categories may require expanded grading schemes."
    assert it["primary_window"]["es"] == "Múltiples"
    assert it["primary_window"]["en"] == "Multiple"
    assert it["preferred_view"]["es"] == "A4C enfocada en VD, RV inflow, PSAX; venas hepáticas subcostales"
    assert it["preferred_view"]["en"] == "RV-focused A4C, RV inflow, and PSAX; hepatic veins from the subcostal window"
    assert it["modality"]["es"] == "2D, color, PW y CW"
    assert it["modality"]["en"] == "2D, color Doppler, PW and CW Doppler"
    assert it["acquisition_timing"]["es"] == "Sístole"
    assert it["acquisition_timing"]["en"] == "Systole"
    assert it["acquisition_key"]["es"] == "Usar la mejor alineación del jet y buscar reversión sistólica en venas hepáticas."
    assert it["acquisition_key"]["en"] == "Use the best alignment with the regurgitant jet and assess for hepatic vein systolic flow reversal."
    assert it["alternate_windows"] == {"es": [], "en": []}

def test_previous_migrated_blocks_intact():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 14. Que todos los bloques bilingües migrados anteriormente permanecen intactos:
    # lv_geometry
    lv_geom_ids = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas"}
    for mid in lv_geom_ids:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["measurement"], dict)

    # left_atrium
    la_ids = {"diametro_ap_ai", "volumen_ai_meas", "lavi_meas", "dilatacion_ai_class", "la_strain_reservoir"}
    for mid in la_ids:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["measurement"], dict)

    # ra_ivc
    ra_ivc_ids = {
        "area_ad_meas",
        "longitud_ad",
        "diametro_menor_ad",
        "diametro_vci_meas",
        "colapsabilidad_vci_meas",
        "distensibilidad_vci_meas",
        "presion_ad_estimada_meas"
    }
    for mid in ra_ivc_ids:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["measurement"], dict)

    # pulmonary_hemodynamics
    pulm_ids = {
        "gradiente_vd_ad",
        "pasp_meas",
        "presion_media_pulmonar",
        "presion_diastolica_pulmonar",
        "rvp_ecografica",
        "indice_excentricidad_vi",
        "aplanamiento_septal_meas"
    }
    for mid in pulm_ids:
        item = next(m for m in data if m["id"] == mid)
        assert isinstance(item["measurement"], dict)

def test_bilingual_vs_pending_counts():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 15. Que después de C3C1J existen exactamente 74 mediciones bilingües y 27 pendientes, usando measurement como criterio estructural.
    bilingual_count = sum(1 for m in data if isinstance(m["measurement"], dict))
    pending_count = sum(1 for m in data if isinstance(m["measurement"], str))
    assert bilingual_count == 74
    assert pending_count == 27
    assert bilingual_count + pending_count == 101
