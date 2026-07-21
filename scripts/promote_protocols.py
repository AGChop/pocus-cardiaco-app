import json
import os
import sys

def main():
    draft_path = "data/protocols.draft.json"
    windows_path = "data/windows.json"
    measurements_path = "data/measurements.json"
    output_path = "data/protocols.json"

    # 1. Leer data/protocols.draft.json
    if not os.path.exists(draft_path):
        print(f"Error: {draft_path} no existe.")
        sys.exit(1)
    if not os.path.exists(windows_path):
        print(f"Error: {windows_path} no existe.")
        sys.exit(1)
    if not os.path.exists(measurements_path):
        print(f"Error: {measurements_path} no existe.")
        sys.exit(1)

    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)
    with open(windows_path, "r", encoding="utf-8") as f:
        windows = json.load(f)
    with open(measurements_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    valid_window_ids = {w["id"] for w in windows}
    valid_measurement_ids = {m["id"] for m in measurements}

    # 2. Validaciones
    # - El JSON es válido (ya cargado con éxito)

    # - Existe exactamente un protocolo
    if len(draft.get("protocols", [])) != 1:
        print("Error: No existe exactamente un protocolo en el draft.")
        sys.exit(1)

    protocol = draft["protocols"][0]

    # - El protocolo tiene id "rush"
    if protocol.get("id") != "rush":
        print("Error: El protocolo no tiene el ID 'rush'.")
        sys.exit(1)

    # - Existen exactamente tres componentes
    components = protocol.get("components", [])
    if len(components) != 3:
        print("Error: No existen exactamente tres componentes.")
        sys.exit(1)

    # - Los componentes son pump, tank y pipes
    comp_ids = [c.get("id") for c in components]
    if comp_ids != ["pump", "tank", "pipes"]:
        print(f"Error: Los componentes no son pump, tank y pipes. Encontrados: {comp_ids}")
        sys.exit(1)

    # - No hay IDs duplicados en componentes o referencias
    if len(comp_ids) != len(set(comp_ids)):
        print("Error: Existen IDs de componentes duplicados.")
        sys.exit(1)

    ref_ids = [r.get("id") for r in draft.get("references", [])]
    if len(ref_ids) != len(set(ref_ids)):
        print("Error: Existen IDs de referencias duplicados.")
        sys.exit(1)

    # - Todas las reference_ids utilizadas existen
    ref_set = set(ref_ids)
    for ref_id in protocol.get("reference_ids", []):
        if ref_id not in ref_set:
            print(f"Error: La referencia general '{ref_id}' no existe.")
            sys.exit(1)
    for comp in components:
        for ref_id in comp.get("reference_ids", []):
            if ref_id not in ref_set:
                print(f"Error: La referencia del componente '{ref_id}' no existe.")
                sys.exit(1)

    # - Todos los linked_window_ids existen en data/windows.json
    for comp in components:
        for w_id in comp.get("linked_window_ids", []):
            if w_id not in valid_window_ids:
                print(f"Error: ID de ventana vinculada '{w_id}' no existe en windows.json.")
                sys.exit(1)

    # - Todos los linked_measurement_ids existen en data/measurements.json
    for comp in components:
        for m_id in comp.get("linked_measurement_ids", []):
            if m_id not in valid_measurement_ids:
                print(f"Error: ID de medición vinculada '{m_id}' no existe en measurements.json.")
                sys.exit(1)

    # - Existe disclaimer
    if "disclaimer" not in draft.get("metadata", {}):
        print("Error: Falta el disclaimer en metadata.")
        sys.exit(1)

    # - Existe sequence_note
    if "sequence_note" not in protocol:
        print("Error: Falta sequence_note en el protocolo.")
        sys.exit(1)

    # - Existe limitations
    if "limitations" not in protocol:
        print("Error: Falta limitations en el protocolo.")
        sys.exit(1)

    # - Existe safety_and_workflow_notes
    if "safety_and_workflow_notes" not in protocol:
        print("Error: Falta safety_and_workflow_notes en el protocolo.")
        sys.exit(1)

    # - Cada componente tiene interpretation_limits
    for comp in components:
        if "interpretation_limits" not in comp:
            print(f"Error: El componente '{comp.get('id')}' no tiene 'interpretation_limits'.")
            sys.exit(1)

    # - No existe el texto "El Bombo"
    json_str = json.dumps(draft, ensure_ascii=False)
    if "El Bombo" in json_str:
        print("Error: Se detectó el término no deseado 'El Bombo'.")
        sys.exit(1)

    # - pump.name_es es "La Bomba (Evaluación cardíaca)"
    pump_comp = next(c for c in components if c.get("id") == "pump")
    if pump_comp.get("name_es") != "La Bomba (Evaluación cardíaca)":
        print(f"Error: El nombre en español del componente pump no es correcto: {pump_comp.get('name_es')}")
        sys.exit(1)

    # - No existe Referencia_RUSH_Editor.pdf
    if "Referencia_RUSH_Editor.pdf" in json_str:
        print("Error: Referencia ficticia 'Referencia_RUSH_Editor.pdf' detectada.")
        sys.exit(1)

    # - No existen source_document ni source_page ficticios
    if "source_document" in protocol or "source_page" in protocol:
        print("Error: source_document o source_page ficticios en el protocolo.")
        sys.exit(1)
    for comp in components:
        if "source_document" in comp or "source_page" in comp:
            print(f"Error: source_document o source_page ficticios en el componente '{comp.get('id')}'.")
            sys.exit(1)

    # 3. Crear metadatos actualizados de promoción
    approved_date = "2026-07-21"
    version_str = "1.0.0"
    status_str = "approved-for-app-use"
    source_str = "data/protocols.draft.json"
    disclaimer_str = (
        "Este contenido es educativo. El protocolo RUSH complementa y no sustituye "
        "la valoración clínica, la reanimación ni los estudios diagnósticos "
        "definitivos. Los hallazgos deben integrarse con el contexto clínico."
    )

    # Actualizar metadata anidada
    updated_metadata = dict(draft.get("metadata", {}))
    updated_metadata["version"] = version_str
    updated_metadata["status"] = status_str
    updated_metadata["approved_on"] = approved_date
    updated_metadata["source"] = source_str
    updated_metadata["protocol_count"] = len(draft.get("protocols", []))

    # Construir objeto de salida final
    final_data = {
        "status": status_str,
        "version": version_str,
        "approved_on": approved_date,
        "source": source_str,
        "educational_disclaimer": disclaimer_str,
        "metadata": updated_metadata,
        "references": draft.get("references", []),
        "protocols": draft.get("protocols", [])
    }

    # Escribir data/protocols.json de manera determinista con salto de línea final
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Promoción completada con éxito. Archivo de salida: {output_path}")

if __name__ == "__main__":
    main()
