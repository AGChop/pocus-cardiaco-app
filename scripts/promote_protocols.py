import json
import os
import sys

def main():
    draft_path = "data/protocols.draft.json"
    i18n_path = "data/protocols.i18n.json"
    windows_path = "data/windows.json"
    measurements_path = "data/measurements.json"
    output_path = "data/protocols.json"

    # 1. Leer data/protocols.draft.json y data/protocols.i18n.json
    if not os.path.exists(draft_path):
        print(f"Error: {draft_path} no existe.")
        sys.exit(1)
    if not os.path.exists(i18n_path):
        print(f"Error: {i18n_path} no existe.")
        sys.exit(1)
    if not os.path.exists(windows_path):
        print(f"Error: {windows_path} no existe.")
        sys.exit(1)
    if not os.path.exists(measurements_path):
        print(f"Error: {measurements_path} no existe.")
        sys.exit(1)

    with open(draft_path, "r", encoding="utf-8") as f:
        draft = json.load(f)
    with open(i18n_path, "r", encoding="utf-8") as f:
        i18n = json.load(f)
    with open(windows_path, "r", encoding="utf-8") as f:
        windows = json.load(f)
    with open(measurements_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    valid_window_ids = {w["id"] for w in windows}
    valid_measurement_ids = {m["id"] for m in measurements}

    # 2. Validaciones básicas del borrador
    if len(draft.get("protocols", [])) != 1:
        print("Error: No existe exactamente un protocolo en el draft.")
        sys.exit(1)

    protocol = draft["protocols"][0]
    proto_id = protocol.get("id")
    if proto_id != "rush":
        print("Error: El protocolo no tiene el ID 'rush'.")
        sys.exit(1)

    components = protocol.get("components", [])
    if len(components) != 3:
        print("Error: No existen exactamente tres componentes.")
        sys.exit(1)

    comp_ids = [c.get("id") for c in components]
    if comp_ids != ["pump", "tank", "pipes"]:
        print(f"Error: Los componentes no son pump, tank y pipes. Encontrados: {comp_ids}")
        sys.exit(1)

    if len(comp_ids) != len(set(comp_ids)):
        print("Error: Existen IDs de componentes duplicados.")
        sys.exit(1)

    ref_ids = [r.get("id") for r in draft.get("references", [])]
    if len(ref_ids) != len(set(ref_ids)):
        print("Error: Existen IDs de referencias duplicados.")
        sys.exit(1)

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

    for comp in components:
        for w_id in comp.get("linked_window_ids", []):
            if w_id not in valid_window_ids:
                print(f"Error: ID de ventana vinculada '{w_id}' no existe en windows.json.")
                sys.exit(1)

    for comp in components:
        for m_id in comp.get("linked_measurement_ids", []):
            if m_id not in valid_measurement_ids:
                print(f"Error: ID de medición vinculada '{m_id}' no existe en measurements.json.")
                sys.exit(1)

    if "disclaimer" not in draft.get("metadata", {}):
        print("Error: Falta el disclaimer en metadata.")
        sys.exit(1)

    for fld in ["sequence_note", "limitations", "safety_and_workflow_notes"]:
        if fld not in protocol:
            print(f"Error: Falta {fld} en el protocolo.")
            sys.exit(1)

    for comp in components:
        if "interpretation_limits" not in comp:
            print(f"Error: El componente '{comp.get('id')}' no tiene 'interpretation_limits'.")
            sys.exit(1)

    json_str = json.dumps(draft, ensure_ascii=False)
    if "El Bombo" in json_str:
        print("Error: Se detectó el término no deseado 'El Bombo'.")
        sys.exit(1)

    pump_comp = next(c for c in components if c.get("id") == "pump")
    if pump_comp.get("name_es") != "La Bomba (Evaluación cardíaca)":
        print(f"Error: El nombre en español del componente pump no es correcto: {pump_comp.get('name_es')}")
        sys.exit(1)

    if "Referencia_RUSH_Editor.pdf" in json_str:
        print("Error: Referencia ficticia 'Referencia_RUSH_Editor.pdf' detectada.")
        sys.exit(1)

    if "source_document" in protocol or "source_page" in protocol:
        print("Error: source_document o source_page ficticios en el protocolo.")
        sys.exit(1)
    for comp in components:
        if "source_document" in comp or "source_page" in comp:
            print(f"Error: source_document o source_page ficticios en el componente '{comp.get('id')}'.")
            sys.exit(1)

    # 3. Validar catálogo de traducción data/protocols.i18n.json
    if i18n.get("source_language") != "es":
        print("Error i18n: El source_language debe ser 'es'.")
        sys.exit(1)
    if i18n.get("target_language") != "en":
        print("Error i18n: El target_language debe ser 'en'.")
        sys.exit(1)

    # Validar existencia y no vacuidad de disclaimer general en i18n
    bilingual_ed_disclaimer = i18n.get("educational_disclaimer")
    if not isinstance(bilingual_ed_disclaimer, dict):
        print("Error i18n: educational_disclaimer debe ser un objeto.")
        sys.exit(1)
    for lang in ["es", "en"]:
        val = bilingual_ed_disclaimer.get(lang)
        if not val or not isinstance(val, str) or not val.strip():
            print(f"Error i18n: educational_disclaimer.{lang} falta o está vacío.")
            sys.exit(1)

    # Validar metadatos en i18n
    i18n_meta = i18n.get("metadata", {})
    for meta_field in ["title", "scope", "intended_audience", "disclaimer"]:
        val = i18n_meta.get(meta_field)
        if not val or not val.strip():
            print(f"Error i18n: metadata.{meta_field} falta o está vacío.")
            sys.exit(1)

    # Validar protocolo en i18n
    i18n_protocols = i18n.get("protocols", {})
    if proto_id not in i18n_protocols:
        print(f"Error i18n: Falta el protocolo '{proto_id}' en el catálogo.")
        sys.exit(1)

    i18n_proto = i18n_protocols[proto_id]
    proto_fields = [
        "clinical_context", "purpose", "target_population", "prerequisites",
        "sequence_note", "integration", "limitations", "safety_and_workflow_notes"
    ]
    for pf in proto_fields:
        val = i18n_proto.get(pf)
        if not val or not val.strip():
            print(f"Error i18n: protocols.{proto_id}.{pf} falta o está vacío.")
            sys.exit(1)

    # Validar componentes en i18n
    i18n_components = i18n_proto.get("components", {})

    # Comprobar componentes sobrantes en i18n
    for key in i18n_components.keys():
        if key not in comp_ids:
            print(f"Error i18n: Componente desconocido '{key}' en las traducciones.")
            sys.exit(1)

    for comp in components:
        c_id = comp["id"]
        if c_id not in i18n_components:
            print(f"Error i18n: Falta el componente '{c_id}' en las traducciones.")
            sys.exit(1)

        i18n_comp = i18n_components[c_id]

        # Validar interpretation_limits
        il_val = i18n_comp.get("interpretation_limits")
        if not il_val or not il_val.strip():
            print(f"Error i18n: El componente '{c_id}' no tiene interpretation_limits traducido.")
            sys.exit(1)

        # Validar listas de componentes
        list_fields = ["clinical_questions", "targets", "suggested_views", "possible_findings"]
        for lf in list_fields:
            draft_list = comp.get(lf, [])
            i18n_list = i18n_comp.get(lf, [])

            if len(draft_list) != len(i18n_list):
                print(f"Error i18n: Mismatch de tamaño en '{lf}' para el componente '{c_id}'. Borrador: {len(draft_list)}, Traducción: {len(i18n_list)}")
                sys.exit(1)

            for idx, (es_item, en_item) in enumerate(zip(draft_list, i18n_list)):
                if not en_item or not en_item.strip():
                    print(f"Error i18n: La traducción inglesa en '{lf}' índice {idx} para '{c_id}' está vacía.")
                    sys.exit(1)

    # 4. Combinar e integrar el contenido en formato bilingüe
    approved_date = "2026-07-21"
    version_str = "1.0.0"
    status_str = "approved-for-app-use"
    source_str = "data/protocols.draft.json"

    # metadata bilingüe
    updated_metadata = {}
    for meta_key, es_val in draft.get("metadata", {}).items():
        if meta_key in ["title", "scope", "intended_audience", "disclaimer"]:
            updated_metadata[meta_key] = {
                "es": es_val,
                "en": i18n_meta[meta_key]
            }
        else:
            updated_metadata[meta_key] = es_val

    updated_metadata["version"] = version_str
    updated_metadata["status"] = status_str
    updated_metadata["approved_on"] = approved_date
    updated_metadata["source"] = source_str
    updated_metadata["protocol_count"] = len(draft.get("protocols", []))

    # protocols bilingüe
    bilingual_protocols = []
    for p in draft.get("protocols", []):
        bp = {}
        for k, v in p.items():
            if k in proto_fields:
                bp[k] = {
                    "es": v,
                    "en": i18n_proto[k]
                }
            elif k == "components":
                bilingual_comps = []
                for comp in v:
                    bc = {}
                    c_id = comp["id"]
                    i18n_c = i18n_components[c_id]
                    for ck, cv in comp.items():
                        if ck in ["clinical_questions", "targets", "suggested_views", "possible_findings"]:
                            # Cada elemento de la lista es un objeto bilingüe {"es", "en"}
                            bc[ck] = [
                                {"es": es_item, "en": en_item}
                                for es_item, en_item in zip(cv, i18n_c[ck])
                            ]
                        elif ck == "interpretation_limits":
                            bc[ck] = {
                                "es": cv,
                                "en": i18n_c[ck]
                            }
                        else:
                            bc[ck] = cv
                    bilingual_comps.append(bc)
                bp["components"] = bilingual_comps
            else:
                bp[k] = v
        bilingual_protocols.append(bp)

    # Construir objeto de salida final
    final_data = {
        "status": status_str,
        "version": version_str,
        "approved_on": approved_date,
        "source": source_str,
        "educational_disclaimer": bilingual_ed_disclaimer,
        "metadata": updated_metadata,
        "references": draft.get("references", []),
        "protocols": bilingual_protocols
    }

    # Escribir data/protocols.json de manera determinista con salto de línea final
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Promoción completada con éxito. Archivo de salida: {output_path}")

if __name__ == "__main__":
    main()
