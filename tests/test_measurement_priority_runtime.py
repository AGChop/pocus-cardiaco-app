import json
import os
import hashlib
import subprocess
import pytest

def test_measurement_priority_runtime():
    approved_path = "data/measurement-priority.json"
    draft_path = "data/measurement-priority.draft.json"
    meas_path = "data/measurements.json"
    sw_path = "service-worker.js"
    loader_path = "assets/js/data-loader.js"

    # 1. data/measurement-priority.json existe
    assert os.path.exists(approved_path), "El archivo data/measurement-priority.json no existe."

    # 2. Es JSON válido
    with open(approved_path, "r", encoding="utf-8") as f:
        approved_data = json.load(f)

    with open(draft_path, "r", encoding="utf-8") as f:
        draft_data = json.load(f)

    with open(meas_path, "r", encoding="utf-8") as f:
        meas_data = json.load(f)

    priorities = approved_data.get("priorities", [])

    # 3. Contiene exactamente 101 mediciones
    assert len(priorities) == 101, f"Se esperaban 101 mediciones en el archivo final, pero hay {len(priorities)}"

    # 4. Contiene 101 IDs únicos
    approved_ids = [p["measurement_id"] for p in priorities]
    assert len(approved_ids) == 101, "No hay exactamente 101 IDs."
    assert len(set(approved_ids)) == 101, "Existen IDs duplicados en el archivo final."

    # 12. Los IDs coinciden exactamente con measurements.json
    meas_ids = {m["id"] for m in meas_data}
    assert set(approved_ids) == meas_ids, "Los IDs no coinciden exactamente con measurements.json."

    # 5. Distribución es 3 / 37 / 43 / 18
    from collections import Counter
    counts = Counter([p["priority_tier"] for p in priorities])
    assert counts[1] == 3, f"Nivel 1 esperado: 3, Encontrado: {counts[1]}"
    assert counts[2] == 37, f"Nivel 2 esperado: 37, Encontrado: {counts[2]}"
    assert counts[3] == 43, f"Nivel 3 esperado: 43, Encontrado: {counts[3]}"
    assert counts[4] == 18, f"Nivel 4 esperado: 18, Encontrado: {counts[4]}"

    # 6. Los objetos de prioridad del archivo final coinciden con los del draft
    draft_priorities = draft_data.get("priorities", [])
    draft_map = {p["measurement_id"]: p for p in draft_priorities}
    for p in priorities:
        m_id = p["measurement_id"]
        assert m_id in draft_map, f"Medición {m_id} no encontrada en draft."
        dp = draft_map[m_id]
        assert p["priority_tier"] == dp["priority_tier"], f"Mismatch en tier para {m_id}"
        assert p["display_order"] == dp["display_order"], f"Mismatch en display_order para {m_id}"
        assert p["rationale"] == dp["rationale"], f"Mismatch en rationale para {m_id}"

    # 7. Metadatos superiores en la raíz
    assert approved_data.get("status") == "approved-for-app-ordering", "Status incorrecto en la raíz."
    assert approved_data.get("version") == "1.0.0", "Versión incorrecta en la raíz."
    assert approved_data.get("approved_on") == "2026-07-21", "approved_on incorrecto en la raíz."
    assert approved_data.get("source") == "data/measurement-priority.draft.json", "source incorrecto en la raíz."
    assert isinstance(approved_data.get("ordering_disclaimer"), str) and len(approved_data.get("ordering_disclaimer")) > 0, "ordering_disclaimer inválido o vacío."

    # Conservación del objeto metadata original
    assert "metadata" in approved_data and isinstance(approved_data["metadata"], dict), "El objeto metadata no fue conservado."

    # 10 y 11. display_order es consecutivo y no duplicado dentro de cada sección
    section_orders = {}
    for p in priorities:
        s_id = p["section_id"]
        if s_id not in section_orders:
            section_orders[s_id] = []
        section_orders[s_id].append(p["display_order"])

    for s_id, orders in section_orders.items():
        assert len(orders) == len(set(orders)), f"Sección {s_id} tiene display_order duplicados."
        assert sorted(orders) == list(range(1, len(orders) + 1)), f"Sección {s_id} no tiene display_order consecutivo desde 1."

    # 13. Conserva rationale y reference_ids
    for p in priorities:
        assert p.get("rationale") and p["rationale"].strip(), f"Medición {p['measurement_id']} sin rationale."
        assert p.get("reference_ids") and len(p["reference_ids"]) >= 1, f"Medición {p['measurement_id']} sin reference_ids."

    # 14. service-worker.js incluye data/measurement-priority.json
    with open(sw_path, "r", encoding="utf-8") as f:
        sw_content = f.read()
    assert "data/measurement-priority.json" in sw_content, "service-worker.js no incluye data/measurement-priority.json"

    # 15. DataLoader hace referencia a data/measurement-priority.json
    with open(loader_path, "r", encoding="utf-8") as f:
        loader_content = f.read()
    assert "data/measurement-priority.json" in loader_content, "DataLoader no hace referencia a data/measurement-priority.json"

    # 16. Existe una ruta de respaldo cuando falla la carga (validado en data-loader.js con console.warn y retorno de measurements)
    assert "console.warn" in loader_content, "data-loader.js no implementa console.warn para respaldo."

    # 17. El orden no elimina mediciones (siguen estando las 101)
    assert len(priorities) == len(meas_data), "El orden eliminó mediciones de la base de datos."

    # 19. Las nueve reclasificaciones aprobadas permanecen en Nivel 3
    approved_9 = {
        "paat_tsvd", "distensibilidad_vci_meas", "gradiente_medio_mitral",
        "insuficiencia_mitral_severa_meas", "insuficiencia_aortica_severa_meas",
        "insuficiencia_tricuspidea_severa_meas", "vena_contracta_meas",
        "variacion_mitral_respiratoria", "variacion_tricuspidea_respiratoria"
    }
    for m_id in approved_9:
        entry = next(p for p in priorities if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 3, f"{m_id} debería estar en Nivel 3."

    # 20. velocidad_tsvi, tiempo_desaceleracion_e y grosor_pared_vd permanecen en Nivel 3
    withdrawn_3 = {"velocidad_tsvi", "tiempo_desaceleracion_e", "grosor_pared_vd"}
    for m_id in withdrawn_3:
        entry = next(p for p in priorities if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 3, f"{m_id} debería estar en Nivel 3."

    # 21. fevi permanece en Nivel 2
    fevi_entry = next(p for p in priorities if p["measurement_id"] == "fevi")
    assert fevi_entry["priority_tier"] == 2, "FEVI debería ser Nivel 2."

    # 22. relacion_vd_vi, diametro_vci_meas y colapsabilidad_vci_meas permanecen en Nivel 1
    locked_3 = {"relacion_vd_vi", "diametro_vci_meas", "colapsabilidad_vci_meas"}
    for m_id in locked_3:
        entry = next(p for p in priorities if p["measurement_id"] == m_id)
        assert entry["priority_tier"] == 1, f"{m_id} debería ser Nivel 1."

def test_promotion_reproducibility():
    # 18. Script de promoción es reproducible (hash idéntico byte por byte)
    approved_path = "data/measurement-priority.json"

    subprocess.run(["python3", "scripts/promote_measurement_priority.py"], check=True)
    with open(approved_path, "rb") as f:
        hash1 = hashlib.sha256(f.read()).hexdigest()

    subprocess.run(["python3", "scripts/promote_measurement_priority.py"], check=True)
    with open(approved_path, "rb") as f:
        hash2 = hashlib.sha256(f.read()).hexdigest()

    assert hash1 == hash2, "El script de promoción no es reproducible byte por byte."
