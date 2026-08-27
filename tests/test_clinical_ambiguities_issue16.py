import json
from pathlib import Path

def test_clinical_ambiguities_issue16_specifications():
    meas_path = "data/measurements.json"
    approved_path = "data/measurement-priority.json"
    protocols_path = "data/protocols.json"
    protocols_beta_path = "data/protocols.beta.json"

    with open(meas_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    with open(approved_path, "r", encoding="utf-8") as f:
        approved_data = json.load(f)

    # 1. Verificar FEVI normal_values con igualdad exacta y preservación de limitations
    fevi = next(m for m in measurements if m["id"] == "fevi")
    expected_fevi_es = "Simpson biplano: hombres 52–72%; mujeres 54–74% (intervalos de referencia en adultos). Superar el límite superior de referencia no establece por sí solo un estado hiperdinámico; interpretar según el método, la calidad de imagen y el contexto hemodinámico."
    expected_fevi_en = "Biplane Simpson: men 52–72%; women 54–74% (adult reference intervals). Exceeding the upper reference limit alone does not establish a hyperdynamic state; interpret according to the method, image quality, and hemodynamic context."
    assert fevi["normal_values"]["es"] == expected_fevi_es
    assert fevi["normal_values"]["en"] == expected_fevi_en

    # fevi conserva sus interpretation_limitations originales y no contiene disfunción diastólica / diastolic dysfunction
    assert "disfunción diastólica" not in fevi["interpretation_limitations"]["es"]
    assert "diastolic dysfunction" not in fevi["interpretation_limitations"]["en"]
    assert fevi["interpretation_limitations"]["es"] == "Integrar con contractilidad regional, carga y calidad de imagen."
    assert fevi["interpretation_limitations"]["en"] == "Interpret together with regional wall motion, loading conditions, and image quality."

    # 2. Verificar GLS normal_values con igualdad exacta
    gls = next(m for m in measurements if m["id"] == "gls_vi")
    expected_gls_es = "GLS del VI: normal cuando es más negativo que −18%; limítrofe entre −16% y −18%; anormal cuando es menos negativo que −16%. Los valores dependen del fabricante, la versión del software y las condiciones de carga. Para seguimiento seriado, utilizar preferiblemente la misma plataforma y comparar con el valor basal."
    expected_gls_en = "LV GLS: normal when more negative than −18%; borderline from −16% to −18%; abnormal when less negative than −16%. Values depend on the vendor, software version, and loading conditions. For serial follow-up, preferably use the same platform and compare with baseline."
    assert gls["normal_values"]["es"] == expected_gls_es
    assert gls["normal_values"]["en"] == expected_gls_en

    # 3. Referencia de strain y DOI/URL exactos
    ref_consensus = next(r for r in approved_data["references"] if r["id"] == "strain_consensus_2025")
    assert ref_consensus["doi"] == "10.1016/j.echo.2025.07.007"
    assert ref_consensus["url"] == "https://doi.org/10.1016/j.echo.2025.07.007"
    # No debe tener source_page
    assert "source_page" not in ref_consensus

    # El conjunto de measurement_id que incluye strain_consensus_2025 es exactamente {"gls_vi"}
    strain_linked_measurements = {
        p["measurement_id"]
        for p in approved_data["priorities"]
        if "strain_consensus_2025" in p.get("reference_ids", [])
    }
    assert strain_linked_measurements == {"gls_vi"}

    # 4. Limitación multiparamétrica común bilingüe en diástole (exactamente una ocurrencia)
    diastolic_ids = [
        "onda_e_mitral", "onda_a_mitral", "relacion_e_a", "e_septal_meas", "e_lateral_meas",
        "relacion_e_e_promedio", "tiempo_desaceleracion_e", "ivrt_meas",
        "velocidad_it_diastology", "lavi_diastology", "la_strain_diastology"
    ]
    warning_es = "Esta variable aislada no diagnostica ni gradúa la disfunción diastólica ni estima por sí sola las presiones de llenado. Debe integrarse mediante el enfoque multiparamétrico aplicable al ritmo, la FEVI, las enfermedades concomitantes y el contexto clínico."
    warning_en = "This variable alone does not diagnose or grade diastolic dysfunction or independently estimate filling pressures. It must be integrated using the multiparametric approach applicable to rhythm, LVEF, concomitant disease, and clinical context."

    expected_diastolic_ids = set(diastolic_ids)

    warning_es_ids = {
        item["id"]
        for item in measurements
        if warning_es in item.get("interpretation_limitations", {}).get("es", "")
    }
    warning_en_ids = {
        item["id"]
        for item in measurements
        if warning_en in item.get("interpretation_limitations", {}).get("en", "")
    }

    assert warning_es_ids == expected_diastolic_ids
    assert warning_en_ids == expected_diastolic_ids

    for d_id in diastolic_ids:
        item = next(m for m in measurements if m["id"] == d_id)
        assert warning_es in item["interpretation_limitations"]["es"]
        assert warning_en in item["interpretation_limitations"]["en"]
        assert item["interpretation_limitations"]["es"].count(warning_es) == 1
        assert item["interpretation_limitations"]["en"].count(warning_en) == 1

    # 5. Las 25 prioridades del Lote 1 y Lote 2 tienen review_status: approved y metadata completa, las otras 76 continúan pending.
    assert len(approved_data["priorities"]) == 101
    lote1_ids = {
        "relacion_vd_vi", "diametro_vci_meas", "colapsabilidad_vci_meas",
        "fevi", "epss", "mapse", "s_prima_mitral", "tapse_meas", "s_prima_vd", "vti_tsvi_meas"
    }
    lote2_ids = {
        "dtdvi", "dtsvi", "fraccion_acortamiento_meas", "vtdvi", "vtdvi_indexed",
        "vtsvi_meas", "vtsvi_indexed", "gls_vi", "wmsi", "ivsd", "pwtd",
        "rwt_meas", "geometria_vi_meas", "masa_vi_meas", "lv_mass_index"
    }
    approved_ids_expected = lote1_ids.union(lote2_ids)
    assert len(approved_ids_expected) == 25

    approved_count = 0
    pending_count = 0

    for p in approved_data["priorities"]:
        m_id = p["measurement_id"]
        if m_id in approved_ids_expected:
            approved_count += 1
            assert p["review_status"] == "approved", f"Medición {m_id} debería estar approved."
            assert "review_metadata" in p, f"Medición {m_id} debe contener review_metadata."
            meta = p["review_metadata"]
            assert meta["reviewer"] == "AGChop"
            assert meta["reviewed_on"] == "2026-08-25"
            assert meta["decision"] in ["maintain", "change-tier"]
            assert meta["evidence_summary"]["es"] and meta["evidence_summary"]["es"].strip()
            # Criterio: Simpson biplano no se describe como 3D
            if m_id in ["fevi", "vtdvi", "vtdvi_indexed", "vtsvi_meas", "vtsvi_indexed"]:
                es_summary = meta["evidence_summary"]["es"].lower()
                en_summary = meta["evidence_summary"]["en"].lower()
                assert "3d" not in es_summary and "tridimensional" not in es_summary, f"Simpson biplano en {m_id} no debe describirse como 3D."
                assert "3d" not in en_summary and "three-dimensional" not in en_summary, f"Simpson biplano en {m_id} no debe describirse como 3D."

            # Criterio: LVMI / lv_mass_index no afirma "confirmar hipertrofia verdadera"
            if m_id == "lv_mass_index":
                assert "hipertrofia verdadera" not in es_summary and "hipertrofia verdadera" not in p["rationale"].lower()
        else:
            pending_count += 1
            assert p["review_status"] == "pending", f"Medición {m_id} fuera del Lote 1 y 2 debe conservar status pending."

    assert approved_count == 25
    assert pending_count == 76

    # Cargar protocols.json y protocols.beta.json
    with open(protocols_path, "r", encoding="utf-8") as f:
        protocols = json.load(f)
    with open(protocols_beta_path, "r", encoding="utf-8") as f:
        protocols_beta = json.load(f)

    # RUSH aprobado
    assert len(protocols["protocols"]) == 1
    rush = protocols["protocols"][0]
    assert rush["id"] == "rush"
    assert rush["review_status"] == "approved-for-app-use"

    # FATE beta y pending-clinical-review / public-beta
    assert len(protocols_beta["protocols"]) == 1
    fate = protocols_beta["protocols"][0]
    assert fate["id"] == "fate"
    assert fate["review_status"] == "pending-clinical-review"
    assert fate["publication_status"] == "public-beta"

    # 5. Comprobación exacta del service worker
    service_worker = Path("service-worker.js").read_text(encoding="utf-8")
    expected_cache_name = (
        "const CACHE_NAME = "
        "'pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-"
        "final-logo2-pwa1-flow1-quick2-reader1-prender1-fate1-ip1-"
        "beta1-feedback1-clinical1';"
    )
    assert expected_cache_name in service_worker

    # 6. Comprobar también la referencia central
    with open("data/references.json", "r", encoding="utf-8") as f:
        central_references = json.load(f)

    central_strain_refs = [
        ref for ref in central_references
        if ref["id"] == "strain_consensus_2025"
    ]
    assert len(central_strain_refs) == 1
    assert central_strain_refs[0]["doi"] == "10.1016/j.echo.2025.07.007"
    assert central_strain_refs[0]["url"] == "https://doi.org/10.1016/j.echo.2025.07.007"
    assert "source_page" not in central_strain_refs[0]

    # 7. Comprobar las cuatro nuevas referencias del Lote 1 en data/measurement-priority.json
    refs_priorities = approved_data["references"]
    # IVC
    ref_ivc = next(r for r in refs_priorities if r["id"] == "ivc_collapsibility_meta_2023")
    assert ref_ivc["doi"] == "10.1016/j.medine.2021.12.018"
    assert ref_ivc["url"] == "https://doi.org/10.1016/j.medine.2021.12.018"
    assert ref_ivc["year"] == 2023
    assert "Systematic review and meta-analysis" in ref_ivc["title"]
    # Vinculada únicamente a colapsabilidad_vci_meas
    linked_ivc = {p["measurement_id"] for p in approved_data["priorities"] if "ivc_collapsibility_meta_2023" in p.get("reference_ids", [])}
    assert linked_ivc == {"colapsabilidad_vci_meas"}

    # EPSS
    ref_epss = next(r for r in refs_priorities if r["id"] == "epss_accuracy_2022")
    assert ref_epss["doi"] == "10.24908/pocus.v7i1.15220"
    assert ref_epss["url"] == "https://doi.org/10.24908/pocus.v7i1.15220"
    assert ref_epss["year"] == 2022
    assert "E-Point Septal Separation Accuracy" in ref_epss["title"]
    # Vinculada únicamente a epss
    linked_epss = {p["measurement_id"] for p in approved_data["priorities"] if "epss_accuracy_2022" in p.get("reference_ids", [])}
    assert linked_epss == {"epss"}

    # MAPSE
    ref_mapse = next(r for r in refs_priorities if r["id"] == "focused_mapse_2023")
    assert ref_mapse["doi"] == "10.1016/j.ajem.2023.03.018"
    assert ref_mapse["url"] == "https://doi.org/10.1016/j.ajem.2023.03.018"
    assert ref_mapse["year"] == 2023
    assert "mitral annular plane systolic excursion" in ref_mapse["title"]
    # Vinculada únicamente a mapse
    linked_mapse = {p["measurement_id"] for p in approved_data["priorities"] if "focused_mapse_2023" in p.get("reference_ids", [])}
    assert linked_mapse == {"mapse"}

    # LVOT VTI
    ref_vti = next(r for r in refs_priorities if r["id"] == "lvot_vti_fluid_2025")
    assert ref_vti["doi"] == "10.1007/s40477-025-01072-1"
    assert ref_vti["url"] == "https://doi.org/10.1007/s40477-025-01072-1"
    assert ref_vti["year"] == 2025
    assert "Utilization of left ventricular outflow tract" in ref_vti["title"]
    # Vinculada únicamente a vti_tsvi_meas
    linked_vti = {p["measurement_id"] for p in approved_data["priorities"] if "lvot_vti_fluid_2025" in p.get("reference_ids", [])}
    assert linked_vti == {"vti_tsvi_meas"}

    # 8. Comprobar la nueva referencia de Hipertensión del Lote 2 en data/measurement-priority.json
    ref_hyp = next(r for r in refs_priorities if r["id"] == "adult_hypertension_echo_2015")
    assert ref_hyp["doi"] == "10.1016/j.echo.2015.05.002"
    assert ref_hyp["url"] == "https://doi.org/10.1016/j.echo.2015.05.002"
    assert ref_hyp["year"] == 2015
    assert "Adult Hypertension" in ref_hyp["title"]
    # Vinculada únicamente a masa, índice de masa, RWT o geometría
    linked_hyp = {p["measurement_id"] for p in approved_data["priorities"] if "adult_hypertension_echo_2015" in p.get("reference_ids", [])}
    assert linked_hyp == {"masa_vi_meas", "lv_mass_index", "rwt_meas", "geometria_vi_meas"}
