import json
import os
import subprocess
import pytest

def test_priority_draft_validity():
    draft_path = "data/measurement-priority.draft.json"
    meas_path = "data/measurements.json"
    sections_path = "data/sections.json"

    assert os.path.exists(draft_path), "El borrador de prioridades no existe."
    assert os.path.exists(meas_path), "El archivo original de mediciones no existe."
    assert os.path.exists(sections_path), "El archivo de secciones clínicas no existe."

    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)

    with open(meas_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    with open(sections_path, "r", encoding="utf-8") as f:
        sections_data = json.load(f)

    real_section_ids = {s["id"] for s in sections_data}
    real_section_titles = {s["title"] for s in sections_data}

    # 1. Existen exactamente 101 mediciones en measurements.json y priorities
    assert len(measurements) == 101, f"Se esperaban 101 mediciones, pero hay {len(measurements)}."
    assert len(draft["priorities"]) == 101, f"Se esperaban 101 prioridades, pero hay {len(draft['priorities'])}."

    # 2. Existen exactamente 101 IDs únicos
    draft_ids = [p["measurement_id"] for p in draft["priorities"]]
    assert len(draft_ids) == 101, "No hay exactamente 101 IDs."
    assert len(set(draft_ids)) == 101, "Existen IDs duplicados en el borrador."

    # 3. No hay IDs desconocidos ni faltantes
    original_ids = {m["id"] for m in measurements}
    assert set(draft_ids) == original_ids, "Los IDs del borrador no coinciden exactamente con los de measurements.json."

    # 5. Distribución exacta
    from collections import Counter
    counts = Counter([p["priority_tier"] for p in draft["priorities"]])
    assert counts[1] == 3, f"Nivel 1 esperado: 3, Encontrado: {counts[1]}"
    assert counts[2] == 37, f"Nivel 2 esperado: 37, Encontrado: {counts[2]}"
    assert counts[3] == 43, f"Nivel 3 esperado: 43, Encontrado: {counts[3]}"
    assert counts[4] == 18, f"Nivel 4 esperado: 18, Encontrado: {counts[4]}"

    # 6. Las nueve mediciones aprobadas están en Nivel 3
    approved_9 = {
        "paat_tsvd", "distensibilidad_vci_meas", "gradiente_medio_mitral",
        "insuficiencia_mitral_severa_meas", "insuficiencia_aortica_severa_meas",
        "insuficiencia_tricuspidea_severa_meas", "vena_contracta_meas",
        "variacion_mitral_respiratoria", "variacion_tricuspidea_respiratoria"
    }
    for m_id in approved_9:
        entry = next(p for p in draft["priorities"] if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 3, f"{m_id} debería estar en Nivel 3. Encontrado: {entry['priority_tier']}"
        assert entry["pocus_scope"] == "contextual", f"{m_id} debería tener scope 'contextual'. Encontrado: {entry['pocus_scope']}"

    # 7. Las tres mediciones retiradas permanecen en Nivel 3
    withdrawn_3 = {"velocidad_tsvi", "tiempo_desaceleracion_e", "grosor_pared_vd"}
    for m_id in withdrawn_3:
        entry = next(p for p in draft["priorities"] if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 3, f"{m_id} debería permanecer en Nivel 3. Encontrado: {entry['priority_tier']}"
        assert entry["pocus_scope"] == "contextual", f"{m_id} debería tener scope 'contextual'. Encontrado: {entry['pocus_scope']}"

    # 8. FEVI permanece en Nivel 2
    fevi_entry = next(p for p in draft["priorities"] if p["measurement_id"] == "fevi")
    assert fevi_entry["priority_tier"] == 2, f"FEVI debería ser Nivel 2. Encontrado: {fevi_entry['priority_tier']}"
    assert fevi_entry["pocus_scope"] == "extended", f"FEVI debería tener scope 'extended'. Encontrado: {fevi_entry['pocus_scope']}"

    # 9. Los tres parámetros bloqueados permanecen en Nivel 1
    locked_3 = {"relacion_vd_vi", "diametro_vci_meas", "colapsabilidad_vci_meas"}
    for m_id in locked_3:
        entry = next(p for p in draft["priorities"] if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 1, f"{m_id} debería ser Nivel 1. Encontrado: {entry['priority_tier']}"
        assert entry["pocus_scope"] == "basic", f"{m_id} debería tener scope 'basic'. Encontrado: {entry['pocus_scope']}"
        # 10. Los tres de Nivel 1 tienen confidence moderate
        assert entry["confidence"] == "moderate", f"{m_id} debería tener confianza 'moderate'. Encontrado: {entry['confidence']}"

    # 11 y 12. priority_label y pocus_scope coinciden con priority_tier
    expected_labels = {
        1: "Núcleo POCUS",
        2: "POCUS extendido",
        3: "Dependiente del contexto",
        4: "Avanzado / ecocardiografía integral"
    }
    expected_scopes = {
        1: "basic",
        2: "extended",
        3: "contextual",
        4: "advanced"
    }

    valid_ref_ids = {r["id"] for r in draft["references"]}
    section_display_orders = {}

    for p in draft["priorities"]:
        m_id = p["measurement_id"]
        tier = p["priority_tier"]

        assert p["priority_label"] == expected_labels[tier], f"Medición '{m_id}' tiene etiqueta de prioridad incoherente."
        assert p["pocus_scope"] == expected_scopes[tier], f"Medición '{m_id}' tiene scope de POCUS incoherente."

        # 15. Cada medición tiene rationale
        assert p["rationale"] and p["rationale"].strip(), f"Medición '{m_id}' tiene justificación vacía."

        # 16. Cada medición tiene al menos una reference_id
        assert len(p["reference_ids"]) >= 1, f"Medición '{m_id}' no tiene referencias asignadas."

        # 17. Cada reference_id existe en la lista de referencias
        for rid in p["reference_ids"]:
            assert rid in valid_ref_ids, f"Medición '{m_id}' tiene referencia inexistente: '{rid}'."

        # 18. original_order está presente
        assert "original_order" in p, f"Medición '{m_id}' no tiene original_order."

        # 19. primary_window se conserva
        orig = next(m for m in measurements if m["id"] == m_id)
        assert p["primary_window"] == orig.get("primary_window", ""), f"Medición '{m_id}' no conserva primary_window."

        # 20. section_id no se sustituye por la ventana
        assert p["section_id"] == orig["section_id"], f"Medición '{m_id}' tiene section_id incorrecto."
        assert p["section_id"] in real_section_ids, f"Medición '{m_id}' tiene section_id inexistente."
        assert p["section_title"] in real_section_titles, f"Medición '{m_id}' tiene section_title inexistente."

        # Agrupar display orders por sección
        s_id = p["section_id"]
        if s_id not in section_display_orders:
            section_display_orders[s_id] = []
        section_display_orders[s_id].append(p["display_order"])

    # 13 y 14. display_order es consecutivo y no duplicado dentro de cada sección
    for s_id, orders in section_display_orders.items():
        assert len(orders) == len(set(orders)), f"Sección '{s_id}' tiene display_order duplicados."
        assert sorted(orders) == list(range(1, len(orders) + 1)), f"Sección '{s_id}' no tiene display_order consecutivos desde 1."

def test_script_reproducibility():
    # 21. El script generador es reproducible (determinista)
    draft_path = "data/measurement-priority.draft.json"

    # Ejecutar build_priority_draft.py
    subprocess.run(["python3", "scripts/build_priority_draft.py"], check=True)
    with open(draft_path, "r", encoding="utf-8") as f:
        first_run = f.read()

    # Volver a ejecutar
    subprocess.run(["python3", "scripts/build_priority_draft.py"], check=True)
    with open(draft_path, "r", encoding="utf-8") as f:
        second_run = f.read()

    assert first_run == second_run, "La ejecución del script build_priority_draft.py no es determinista."
