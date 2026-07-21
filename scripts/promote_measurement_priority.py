import json
import os
from collections import Counter

def promote():
    draft_path = "data/measurement-priority.draft.json"
    meas_path = "data/measurements.json"
    output_path = "data/measurement-priority.json"

    if not os.path.exists(draft_path):
        raise FileNotFoundError(f"No se encontró el borrador en {draft_path}")
    if not os.path.exists(meas_path):
        raise FileNotFoundError(f"No se encontró el archivo de mediciones en {meas_path}")

    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)

    with open(meas_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    priorities = draft.get("priorities", [])

    # 1. Validar 101 mediciones
    if len(priorities) != 101:
        raise ValueError(f"Se esperaban 101 mediciones en el borrador, pero hay {len(priorities)}")

    # 2. Validar 101 IDs únicos
    draft_ids = [p["measurement_id"] for p in priorities]
    if len(set(draft_ids)) != 101:
        raise ValueError("Existen IDs duplicados en el borrador de prioridades.")

    # Validar coincidencia exacta con measurements.json
    meas_ids = {m["id"] for m in measurements}
    if set(draft_ids) != meas_ids:
        raise ValueError("Los IDs del borrador no coinciden exactamente con measurements.json.")

    # 3. Validar distribución exacta 3 / 37 / 43 / 18
    counts = Counter([p["priority_tier"] for p in priorities])
    if counts[1] != 3 or counts[2] != 37 or counts[3] != 43 or counts[4] != 18:
        raise ValueError(f"Distribución incorrecta: Nivel 1={counts[1]}, Nivel 2={counts[2]}, Nivel 3={counts[3]}, Nivel 4={counts[4]}")

    # 4. Validar display_order consecutivo y sin duplicados por sección
    section_orders = {}
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

    for p in priorities:
        m_id = p["measurement_id"]
        tier = p["priority_tier"]

        # Validar rationale y reference_ids
        if not p.get("rationale") or not p["rationale"].strip():
            raise ValueError(f"Medición {m_id} no tiene rationale válido.")
        if not p.get("reference_ids") or len(p["reference_ids"]) < 1:
            raise ValueError(f"Medición {m_id} no tiene reference_ids asignadas.")

        # Validar coincidencia de label y scope
        if p.get("priority_label") != expected_labels[tier]:
            raise ValueError(f"Medición {m_id} tiene priority_label incorrecto.")
        if p.get("pocus_scope") != expected_scopes[tier]:
            raise ValueError(f"Medición {m_id} tiene pocus_scope incorrecto.")

        s_id = p["section_id"]
        if s_id not in section_orders:
            section_orders[s_id] = []
        section_orders[s_id].append(p["display_order"])

    for s_id, orders in section_orders.items():
        if len(orders) != len(set(orders)):
            raise ValueError(f"Sección {s_id} contiene display_order duplicados.")
        if sorted(orders) != list(range(1, len(orders) + 1)):
            raise ValueError(f"Sección {s_id} no tiene display_order consecutivo desde 1.")

    # 5. Crear metadatos superiores para el archivo final aprobado con campos en la raíz
    approved_data = {
        "status": "approved-for-app-ordering",
        "version": "1.0.0",
        "approved_on": "2026-07-21",
        "source": "data/measurement-priority.draft.json",
        "ordering_disclaimer": "Esta clasificación representa prioridad clínica de visualización dentro de una herramienta educativa. No representa frecuencia mundial de uso, importancia diagnóstica absoluta ni sustituye el juicio clínico.",
        "metadata": draft.get("metadata", {}),
        "references": draft.get("references", []),
        "priorities": priorities
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(approved_data, f, indent=2, ensure_ascii=False)

    print(f"Archivo de prioridades aprobado creado con éxito en {output_path}")

if __name__ == "__main__":
    promote()
