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
    protocols = draft.get("protocols", [])
    if len(protocols) < 1:
        print("Error: El borrador debe tener al menos un protocolo.")
        sys.exit(1)

    proto_ids = [p.get("id") for p in protocols]
    if len(proto_ids) != len(set(proto_ids)):
        print("Error: Existen IDs de protocolo duplicados.")
        sys.exit(1)

    # Validar que existan al menos rush y fate
    if "rush" not in proto_ids or "fate" not in proto_ids:
        print(f"Error: Deben existir al menos los protocolos 'rush' y 'fate'. Encontrados: {proto_ids}")
        sys.exit(1)

    # Validar invariantes específicos de RUSH
    rush_proto = next(p for p in protocols if p.get("id") == "rush")
    rush_components = rush_proto.get("components", [])
    if len(rush_components) != 3:
        print("Error: RUSH debe tener exactamente 3 componentes.")
        sys.exit(1)
    rush_comp_ids = [c.get("id") for c in rush_components]
    if rush_comp_ids != ["pump", "tank", "pipes"]:
        print(f"Error: Componentes de RUSH incorrectos: {rush_comp_ids}")
        sys.exit(1)

    # Validar invariantes específicos de FATE
    fate_proto = next(p for p in protocols if p.get("id") == "fate")
    fate_components = fate_proto.get("components", [])
    if len(fate_components) != 4:
        print("Error: FATE debe tener exactamente 4 componentes.")
        sys.exit(1)
    fate_comp_ids = [c.get("id") for c in fate_components]
    if fate_comp_ids != ["subcostal_4c", "apical_4c", "parasternal", "pleural"]:
        print(f"Error: Componentes de FATE incorrectos: {fate_comp_ids}")
        sys.exit(1)

    ref_ids = [r.get("id") for r in draft.get("references", [])]
    if len(ref_ids) != len(set(ref_ids)):
        print("Error: Existen IDs de referencias duplicados.")
        sys.exit(1)

    ref_set = set(ref_ids)

    # Validaciones para todos los protocolos
    for protocol in protocols:
        p_id = protocol.get("id")
        components = protocol.get("components", [])
        comp_ids = [c.get("id") for c in components]

        if len(comp_ids) != len(set(comp_ids)):
            print(f"Error: Componentes duplicados en protocolo '{p_id}'.")
            sys.exit(1)

        for ref_id in protocol.get("reference_ids", []):
            if ref_id not in ref_set:
                print(f"Error: La referencia general '{ref_id}' en protocolo '{p_id}' no existe.")
                sys.exit(1)

        for comp in components:
            c_id = comp.get("id")
            for ref_id in comp.get("reference_ids", []):
                if ref_id not in ref_set:
                    print(f"Error: La referencia del componente '{ref_id}' en '{p_id}.{c_id}' no existe.")
                    sys.exit(1)

            for w_id in comp.get("linked_window_ids", []):
                if w_id not in valid_window_ids:
                    print(f"Error: ID de ventana vinculada '{w_id}' en '{p_id}.{c_id}' no existe en windows.json.")
                    sys.exit(1)

            for m_id in comp.get("linked_measurement_ids", []):
                if m_id not in valid_measurement_ids:
                    print(f"Error: ID de medición vinculada '{m_id}' en '{p_id}.{c_id}' no existe en measurements.json.")
                    sys.exit(1)

        for fld in ["sequence_note", "limitations", "safety_and_workflow_notes"]:
            if fld not in protocol:
                print(f"Error: Falta {fld} en el protocolo '{p_id}'.")
                sys.exit(1)

        for comp in components:
            if "interpretation_limits" not in comp:
                print(f"Error: El componente '{comp.get('id')}' en '{p_id}' no tiene 'interpretation_limits'.")
                sys.exit(1)

    json_str = json.dumps(draft, ensure_ascii=False)
    if "El Bombo" in json_str:
        print("Error: Se detectó el término no deseado 'El Bombo'.")
        sys.exit(1)

    # Validar nombres de componentes fijos RUSH
    pump_comp = next(c for c in rush_components if c.get("id") == "pump")
    if pump_comp.get("name_es") != "La Bomba (Evaluación cardíaca)":
        print(f"Error: El nombre en español del componente pump de RUSH no es correcto: {pump_comp.get('name_es')}")
        sys.exit(1)

    if "Referencia_RUSH_Editor.pdf" in json_str:
        print("Error: Referencia ficticia 'Referencia_RUSH_Editor.pdf' detectada.")
        sys.exit(1)

    for protocol in protocols:
        p_id = protocol.get("id")
        if "source_document" in protocol or "source_page" in protocol:
            print(f"Error: source_document o source_page ficticios en el protocolo '{p_id}'.")
            sys.exit(1)
        for comp in protocol.get("components", []):
            if "source_document" in comp or "source_page" in comp:
                print(f"Error: source_document o source_page ficticios en el componente '{comp.get('id')}' de '{p_id}'.")
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

    # Validar protocolos en i18n
    i18n_protocols = i18n.get("protocols", {})
    for protocol in protocols:
        p_id = protocol.get("id")
        if p_id not in i18n_protocols:
            print(f"Error i18n: Falta el protocolo '{p_id}' en el catálogo.")
            sys.exit(1)

        i18n_proto = i18n_protocols[p_id]
        proto_fields = [
            "clinical_context", "purpose", "target_population", "prerequisites",
            "sequence_note", "integration", "limitations", "safety_and_workflow_notes"
        ]
        for pf in proto_fields:
            val = i18n_proto.get(pf)
            if not val or not val.strip():
                print(f"Error i18n: protocols.{p_id}.{pf} falta o está vacío.")
                sys.exit(1)

        # Validar componentes en i18n para este protocolo
        components = protocol.get("components", [])
        comp_ids = [c.get("id") for c in components]
        i18n_components = i18n_proto.get("components", {})

        for key in i18n_components.keys():
            if key not in comp_ids:
                print(f"Error i18n: Componente desconocido '{key}' en las traducciones del protocolo '{p_id}'.")
                sys.exit(1)

        for comp in components:
            c_id = comp["id"]
            if c_id not in i18n_components:
                print(f"Error i18n: Falta el componente '{c_id}' en las traducciones del protocolo '{p_id}'.")
                sys.exit(1)

            i18n_comp = i18n_components[c_id]

            il_val = i18n_comp.get("interpretation_limits")
            if not il_val or not il_val.strip():
                print(f"Error i18n: El componente '{c_id}' en '{p_id}' no tiene interpretation_limits traducido.")
                sys.exit(1)

            list_fields = ["clinical_questions", "targets", "suggested_views", "possible_findings"]
            for lf in list_fields:
                draft_list = comp.get(lf, [])
                i18n_list = i18n_comp.get(lf, [])

                if len(draft_list) != len(i18n_list):
                    print(f"Error i18n: Mismatch de tamaño en '{lf}' para el componente '{c_id}' de '{p_id}'. Borrador: {len(draft_list)}, Traducción: {len(i18n_list)}")
                    sys.exit(1)

                for idx, (es_item, en_item) in enumerate(zip(draft_list, i18n_list)):
                    if not en_item or not en_item.strip():
                        print(f"Error i18n: La traducción inglesa en '{lf}' índice {idx} para '{p_id}.{c_id}' está vacía.")
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
        p_id = p["id"]
        i18n_proto = i18n_protocols[p_id]
        i18n_components = i18n_proto.get("components", {})
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
                        elif ck == "quick_reference":
                            bc[ck] = {
                                "assess": {
                                    "es": cv["assess"],
                                    "en": i18n_c["quick_reference"]["assess"]
                                },
                                "alerts": {
                                    "es": cv["alerts"],
                                    "en": i18n_c["quick_reference"]["alerts"]
                                }
                            }
                        else:
                            bc[ck] = cv
                    bilingual_comps.append(bc)
                bp["components"] = bilingual_comps
            else:
                bp[k] = v
        bilingual_protocols.append(bp)
    # Promoción estricta de protocolos aprobados (review_status == "approved-for-app-use")
    promoted_protocols = [p for p in bilingual_protocols if p.get("review_status") == "approved-for-app-use"]
    updated_metadata["protocol_count"] = len(promoted_protocols)

    # Filtrar referencias para protocols.json
    promoted_ref_ids = set()
    for p in promoted_protocols:
        promoted_ref_ids.update(p.get("reference_ids", []))
        for comp in p.get("components", []):
            promoted_ref_ids.update(comp.get("reference_ids", []))

    filtered_references = [r for r in draft.get("references", []) if r["id"] in promoted_ref_ids]

    final_data = {
        "status": status_str,
        "version": version_str,
        "approved_on": approved_date,
        "source": source_str,
        "educational_disclaimer": bilingual_ed_disclaimer,
        "metadata": updated_metadata,
        "references": filtered_references,
        "protocols": promoted_protocols
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Generación de data/protocols.beta.json (solo public-beta)
    beta_protocols = [p for p in bilingual_protocols if p.get("publication_status") == "public-beta"]
    beta_ref_ids = set()
    for p in beta_protocols:
        beta_ref_ids.update(p.get("reference_ids", []))
        for comp in p.get("components", []):
            beta_ref_ids.update(comp.get("reference_ids", []))

    beta_references = [r for r in draft.get("references", []) if r["id"] in beta_ref_ids]

    beta_metadata = updated_metadata.copy()
    beta_metadata["protocol_count"] = len(beta_protocols)
    beta_metadata["status"] = "public-beta"
    if "approved_on" in beta_metadata:
        del beta_metadata["approved_on"]

    beta_data = {
        "status": "public-beta",
        "version": version_str,
        "source": source_str,
        "educational_disclaimer": bilingual_ed_disclaimer,
        "metadata": beta_metadata,
        "references": beta_references,
        "protocols": beta_protocols
    }

    beta_output_path = "data/protocols.beta.json"
    with open(beta_output_path, "w", encoding="utf-8") as f:
        json.dump(beta_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Promoción completada con éxito. Archivo de salida: {output_path} y {beta_output_path}")

if __name__ == "__main__":
    main()
