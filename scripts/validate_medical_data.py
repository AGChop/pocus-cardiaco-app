import json
import os
import sys

def load_json(filename):
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        print(f"Error crítico: No existe el archivo {filepath}")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_data():
    errors = []
    
    # Cargar archivos
    sections = load_json("sections.json")
    measurements = load_json("measurements.json")
    glossary = load_json("glossary.json")
    abbreviations = load_json("abbreviations.json")
    classifications = load_json("classifications.json")
    unit_warnings = load_json("unit_warnings.json")
    references = load_json("references.json")
    
    print("--- INICIANDO VALIDACIÓN DE DATOS MÉDICOS ---")
    
    # 1. Verificar secciones (deben ser exactamente 12)
    if len(sections) != 12:
        errors.append(f"Se esperaban exactamente 12 secciones, pero se encontraron {len(sections)}.")
        
    section_ids = set()
    section_slugs = set()
    section_numbers = set()
    
    for sec in sections:
        sec_id = sec.get("id")
        sec_num = sec.get("number")
        sec_slug = sec.get("slug")
        
        # Unicidad de IDs de sección
        if sec_id in section_ids:
            errors.append(f"ID de sección duplicado: {sec_id}")
        section_ids.add(sec_id)
        
        # Unicidad de números
        if sec_num in section_numbers:
            errors.append(f"Número de sección duplicado: {sec_num}")
        section_numbers.add(sec_num)
        
        # Unicidad de slugs
        if sec_slug in section_slugs:
            errors.append(f"Slug de sección duplicado: {sec_slug}")
        section_slugs.add(sec_slug)
        
        # Campos obligatorios
        if not sec.get("title") or not sec.get("short_title"):
            errors.append(f"Sección {sec_id} tiene título o título corto vacío.")
            
        # Advertencias obligatorias en secciones específicas (5, 6, 7, 8, 11, 12)
        warn_sections = {5, 6, 7, 8, 11, 12}
        if sec_num in warn_sections and not sec.get("clinical_warning"):
            errors.append(f"Falta advertencia de seguridad crítica obligatoria en la sección {sec_num} ({sec_id}).")

    # 2. Verificar mediciones
    measurement_ids = set()
    for meas in measurements:
        meas_id = meas.get("id")
        # Unicidad de IDs
        if meas_id in measurement_ids:
            errors.append(f"ID de medición duplicado: {meas_id}")
        measurement_ids.add(meas_id)
        
        # Campos obligatorios
        if not meas.get("measurement"):
            errors.append(f"Medición {meas_id} tiene nombre vacío.")
            
        # Relación de sección válida
        sec_id = meas.get("section_id")
        if sec_id not in section_ids:
            errors.append(f"Medición {meas_id} referencia a section_id inexistente: {sec_id}")
            
        # Orden y páginas válidas
        if "order" not in meas:
            errors.append(f"Medición {meas_id} no tiene el campo 'order'.")
            
        page = meas.get("source_page")
        if not page or not (1 <= page <= 18):
            errors.append(f"Medición {meas_id} tiene una página de origen inválida: {page}")
            
        # Aliases
        if not isinstance(meas.get("aliases"), list):
            errors.append(f"El campo 'aliases' de la medición {meas_id} debe ser una lista.")
            
        # Fórmulas de RVP: verificar que no use TSVI / LVOT en la fórmula
        if meas_id == "rvp_ecografica":
            formula = meas.get("formula_or_method", "")
            interpretation = meas.get("interpretation_limitations", "")
            if "TSVI" in formula or "LVOT" in formula:
                errors.append("ERROR DE SEGURIDAD CLÍNICA: La fórmula de RVP ecográfica menciona incorrectamente TSVI/LVOT.")
            if "TSVD" not in formula and "RVOT" not in formula:
                errors.append("La fórmula de RVP ecográfica debe mencionar TSVD/RVOT como fuente del VTI.")
            if "VTI del TSVD" not in interpretation and "VTI del TSVD/RVOT" not in interpretation:
                errors.append("La interpretación de la RVP ecográfica debe aclarar la precaución de usar VTI del TSVD y no del TSVI.")

    # 3. Verificar glosario
    glossary_ids = set()
    for gloss in glossary:
        gloss_id = gloss.get("id")
        if gloss_id in glossary_ids:
            errors.append(f"ID de glosario duplicado: {gloss_id}")
        glossary_ids.add(gloss_id)
        
        if not gloss.get("term") or not gloss.get("definition"):
            errors.append(f"Término de glosario {gloss_id} tiene nombre o definición vacíos.")
            
        page = gloss.get("source_page")
        if not page or not (1 <= page <= 18):
            errors.append(f"Término {gloss_id} tiene una página de origen inválida: {page}")
            
        if not isinstance(gloss.get("aliases"), list):
            errors.append(f"El campo 'aliases' del término {gloss_id} debe ser una lista.")
            
        # Verificar enlaces relacionados de glosario -> mediciones
        for rel_id in gloss.get("related_measurement_ids", []):
            if rel_id not in measurement_ids:
                errors.append(f"Enlace roto: el término {gloss_id} apunta a la medición inexistente '{rel_id}'.")

    # 4. Verificar enlaces de mediciones -> glosario
    for meas in measurements:
        meas_id = meas.get("id")
        for rel_id in meas.get("related_glossary_ids", []):
            if rel_id not in glossary_ids:
                errors.append(f"Enlace roto: la medición {meas_id} apunta al término de glosario inexistente '{rel_id}'.")

    # Reportar resultados
    if errors:
        print("\n--- ERRORES ENCONTRADOS ---")
        for err in errors:
            print(f"- {err}")
        print(f"\nSe encontraron {len(errors)} errores en la validación de datos médicos.")
        sys.exit(1)
    else:
        print("\nValidación médica estructural completada sin errores.")
        sys.exit(0)

if __name__ == "__main__":
    validate_data()
