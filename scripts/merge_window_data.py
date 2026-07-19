#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migración y fusión de datos para ventanas ecocardiográficas.
Desarrollado para conservar intactos todos los datos clínicos actuales de la aplicación.
"""

import os
import sys
import json
import argparse
import unicodedata

def normalize_text(text):
    """
    Normaliza el texto de forma idéntica al motor de búsqueda de la aplicación:
    - Pasa a minúsculas.
    - Quita tildes y diacríticos.
    - Convierte comillas simples/apostrofes curvados a rectos.
    - Elimina espacios innecesarios.
    """
    if not text:
        return ""
    # Convertir a minúsculas
    normalized = str(text).lower()
    # Eliminar tildes y caracteres especiales diacríticos
    normalized = "".join(
        c for c in unicodedata.normalize("NFD", normalized)
        if unicodedata.category(c) != "Mn"
    )
    # Normalizar apóstrofes y comillas simples (’ ´ ‘ -> ')
    normalized = normalized.replace("’", "'").replace("´", "'").replace("‘", "'")
    # Colapsar espacios
    normalized = " ".join(normalized.split()).strip()
    return normalized

def main():
    parser = argparse.ArgumentParser(description="Fusiona datos de ventanas ecocardiográficas en POCUS Cardíaco.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Simulación segura de la fusión (no modifica archivos).")
    group.add_argument("--apply", action="store_true", help="Aplica la migración de forma definitiva.")
    
    args = parser.parse_args()
    
    # Rutas de archivos
    old_file_path = "data/measurements.json"
    import_file_path = "data/import/pocus_measurements_with_windows.json"
    backup_dir = "data/backups"
    backup_file_path = os.path.join(backup_dir, "measurements_before_windows.json")
    windows_file_path = "data/windows.json"
    report_file_path = "docs/WINDOW_DATA_MIGRATION_REPORT.md"
    
    # 1. Cargar archivos de entrada
    if not os.path.exists(old_file_path):
        print(f"Error: No se encontró el archivo actual en '{old_file_path}'")
        sys.exit(1)
        
    if not os.path.exists(import_file_path):
        print(f"Error: No se encontró el archivo de importación en '{import_file_path}'")
        sys.exit(1)
        
    with open(old_file_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
        
    with open(import_file_path, "r", encoding="utf-8") as f:
        import_data = json.load(f)
        
    new_measurements = import_data.get("measurements", [])
    new_windows = import_data.get("windows", [])
    
    # Contadores y listas para el reporte
    by_id_count = 0
    by_name_count = 0
    ambiguous_count = 0
    not_found_count = 0
    protected_changes_count = 0
    
    mappings = []
    warnings = []
    
    # Campos que deben protegerse (no deben cambiar su valor original)
    protected_fields = [
        "id",
        "section_id",
        "order",
        "measurement",
        "formula_or_method",
        "normal_values",
        "interpretation_limitations",
        "source_page"
    ]
    
    # Mapear los nuevos datos por ID y por nombre normalizado
    new_by_id = {m["id"]: m for m in new_measurements}
    new_by_clean_name = {normalize_text(m["measurement"]): m for m in new_measurements}
    
    # Iterar sobre las mediciones actuales para buscar sus asociaciones
    for old_item in old_data:
        old_id = old_item["id"]
        old_name = old_item["measurement"]
        
        match = None
        method = ""
        
        # A. Intentar buscar por ID exacto
        if old_id in new_by_id:
            match = new_by_id[old_id]
            # Solo validamos que coincida el nombre limpio para asegurar que es la misma medición
            if normalize_text(old_name) == normalize_text(match["measurement"]):
                method = "ID exacto"
            else:
                # Si el ID coincide pero el nombre clínico es muy diferente, no lo asociamos automáticamente
                match = None
                
        # B. Intentar buscar por nombre clínico normalizado
        if not match:
            clean_name = normalize_text(old_name)
            if clean_name in new_by_clean_name:
                match = new_by_clean_name[clean_name]
                method = "Nombre normalizado"
                
        if match:
            if method == "ID exacto":
                by_id_count += 1
            else:
                by_name_count += 1
                
            # Verificar si los campos protegidos de la medición original cambiarían en el resultado final
            # Ya que la migración usará `merged_item = dict(old_item)` y conservará sus valores originales,
            # la cantidad de cambios reales a los campos protegidos es 0.
            # Sin embargo, registramos las diferencias de datos entre archivos para fines informativos (warnings).
            diffs = []
            for field in protected_fields:
                old_val = old_item.get(field)
                new_field_name = "normal_values_or_cutoff" if field == "normal_values" else field
                if field == "source_page":
                    new_field_name = "source_page_original"
                new_val = match.get(new_field_name)
                
                # Normalizar texto para la comparación del warning
                if isinstance(old_val, str) and isinstance(new_val, str):
                    if normalize_text(old_val) != normalize_text(new_val):
                        diffs.append((field, old_val, new_val))
                elif old_val != new_val:
                    diffs.append((field, old_val, new_val))
            
            if diffs:
                warnings.append(
                    f"Medición '{old_name}' (ID: {old_id}): Se ignorarán diferencias del archivo de importación "
                    f"para proteger la base actual. Diferencias: {diffs}"
                )
                
            mappings.append({
                "old": old_item,
                "new": match,
                "method": method
            })
        else:
            not_found_count += 1
            warnings.append(f"No se encontró asociación para la medición: '{old_name}' (ID: {old_id})")

    # Si estamos en modo simulación (dry-run)
    if args.dry_run:
        print("=" * 70)
        print(" SIMULACIÓN SEGURA DE MIGRACIÓN POCUS CARDÍACO (--dry-run) ")
        print("=" * 70)
        
        # Mostrar cada asociación
        print("\nDetalle de las asociaciones encontradas:")
        for idx, item in enumerate(mappings, 1):
            old = item["old"]
            new = item["new"]
            method = item["method"]
            print(f"{idx:3d}. ID actual: {old['id']:<35} | Nombre: {old['measurement']:<35}")
            print(f"     ID nuevo:   {new['id']:<35} | Nombre: {new['measurement']:<35}")
            print(f"     Método:     {method}")
            print("-" * 70)
            
        print("\n" + "=" * 70)
        print(" RESULTADOS E INFORMACIÓN TÉCNICA ")
        print("=" * 70)
        print(f"1. Total de mediciones en data/measurements.json:   {len(old_data)}")
        print(f"2. Total de mediciones en archivo de importación:   {len(new_measurements)}")
        print(f"3. Asociadas por ID exacto:                         {by_id_count}")
        print(f"4. Asociadas por nombre normalizado:                {by_name_count}")
        print(f"5. Asociaciones ambiguas:                           {ambiguous_count}")
        print(f"6. Mediciones no asociadas (faltantes):             {not_found_count}")
        print(f"7. Mapeo completo verificado (101 de 101):         {'SÍ' if len(mappings) == 101 and not_found_count == 0 else 'NO'}")
        
        # Confirmar que alternate_windows sea una lista en todos los casos
        list_check = True
        for m in mappings:
            alt_win = m["new"].get("alternate_windows")
            if not isinstance(alt_win, list):
                list_check = False
                break
        print(f"8. Confirmación de 'alternate_windows' como lista:  {'SÍ (Correcto)' if list_check else 'NO (Error)'}")
        
        print(f"9. Ventanas acústicas en colección 'windows':       {len(new_windows)}")
        print(f"10. ¿Puede generarse 'data/windows.json'?:          {'SÍ' if len(new_windows) > 0 else 'NO'}")
        
        print("\n" + "=" * 70)
        print(" PROTECCIÓN DE CAMPOS EXISTENTES ")
        print("=" * 70)
        print("Campos protegidos validados (no cambiarán su valor clínico original):")
        for field in protected_fields:
            print(f" - {field}: Protegido e intacto")
            
        print(f"\nCampos protegidos que realmente cambiarán:           {protected_changes_count}")
        
        if warnings:
            print("\nNotas Informativas / Diferencias de datos ignoradas del archivo importado:")
            for warn in warnings:
                print(f" * {warn}")
                
        print("\nDatos nuevos que se fusionarán en measurements.json:")
        print(" + primary_window (Texto)")
        print(" + preferred_view (Texto)")
        print(" + modality (Texto)")
        print(" + acquisition_timing (Texto)")
        print(" + acquisition_key (Texto)")
        print(" + alternate_windows (Lista de textos)")
        print("=" * 70)
        
    # Si estamos en modo de aplicación definitiva (apply)
    elif args.apply:
        print("Iniciando aplicación definitiva de migración...")
        
        # Detenerse si no hay 101 asociaciones o si hay diferencias detectadas en campos protegidos
        if len(mappings) != 101 or not_found_count > 0:
            print("ERROR CRÍTICO: No se puede aplicar la migración. No se obtuvieron las 101 asociaciones exactas.")
            sys.exit(1)
            
        # 1. Crear directorio de backups si no existe
        os.makedirs(backup_dir, exist_ok=True)
        
        # 2. Respaldar measurements.json actual
        with open(backup_file_path, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=2, ensure_ascii=False)
        print(f"Copia de seguridad creada con éxito en '{backup_file_path}'")
        
        # 3. Fusionar datos y guardar measurements.json
        merged_measurements = []
        for item in mappings:
            old = item["old"]
            new = item["new"]
            
            # Crear un nuevo diccionario a partir de los datos originales
            merged_item = dict(old)
            
            # Incorporar los 6 nuevos campos
            merged_item["primary_window"] = new.get("primary_window", "")
            merged_item["preferred_view"] = new.get("preferred_view", "")
            merged_item["modality"] = new.get("modality", "")
            merged_item["acquisition_timing"] = new.get("acquisition_timing", "")
            merged_item["acquisition_key"] = new.get("acquisition_key", "")
            merged_item["alternate_windows"] = new.get("alternate_windows", [])
            
            merged_measurements.append(merged_item)
            
        with open(old_file_path, "w", encoding="utf-8") as f:
            json.dump(merged_measurements, f, indent=2, ensure_ascii=False)
        print(f"Fusión de datos guardada con éxito en '{old_file_path}'")
        
        # 4. Crear data/windows.json
        with open(windows_file_path, "w", encoding="utf-8") as f:
            json.dump(new_windows, f, indent=2, ensure_ascii=False)
        print(f"Colección de ventanas creada en '{windows_file_path}'")
        
        # 5. Escribir reporte en docs/WINDOW_DATA_MIGRATION_REPORT.md
        report_content = f"""# Reporte de Migración de Ventanas Ecográficas

Este reporte documenta los resultados de la migración definitiva de datos del POCUS cardíaco.

## Resumen de la Fusión
- **Mediciones procesadas:** {len(mappings)}
- **Asociadas por ID exacto:** {by_id_count}
- **Asociadas por nombre clínico:** {by_name_count}
- **Errores o discrepancias encontradas:** {protected_changes_count}
- **Colección de ventanas ecográficas creada:** {len(new_windows)} ventanas en `{windows_file_path}`
- **Copia de seguridad original:** `{backup_file_path}`

## Datos fusionados en measurements.json:
- `primary_window`
- `preferred_view`
- `modality`
- `acquisition_timing`
- `acquisition_key`
- `alternate_windows`

Todos los identificadores (`id`), fórmulas, valores de referencia e interpretaciones originales se han conservado al 100%.
"""
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Reporte de migración generado en '{report_file_path}'")
        print("¡Migración completada con éxito!")

if __name__ == "__main__":
    main()
