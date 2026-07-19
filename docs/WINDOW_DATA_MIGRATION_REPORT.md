# Reporte de Migración de Ventanas Ecográficas

Este reporte documenta los resultados de la migración definitiva de datos del POCUS cardíaco.

## Resumen de la Fusión
- **Mediciones procesadas:** 101
- **Asociadas por ID exacto:** 12
- **Asociadas por nombre clínico:** 89
- **Errores o discrepancias encontradas:** 0
- **Colección de ventanas ecográficas creada:** 12 ventanas en `data/windows.json`
- **Copia de seguridad original:** `data/backups/measurements_before_windows.json`

## Datos fusionados en measurements.json:
- `primary_window`
- `preferred_view`
- `modality`
- `acquisition_timing`
- `acquisition_key`
- `alternate_windows`

Todos los identificadores (`id`), fórmulas, valores de referencia e interpretaciones originales se han conservado al 100%.
