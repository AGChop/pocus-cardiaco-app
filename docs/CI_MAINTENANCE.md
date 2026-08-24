# Mantenimiento de la Integración Continua (CI)

Este documento detalla el funcionamiento, la estructura y el mantenimiento del workflow de validación y pruebas automatizadas en GitHub Actions.

## ¿Cuándo se ejecuta la CI?

El workflow de CI (`.github/workflows/ci.yml`) se ejecuta de manera automática bajo las siguientes condiciones:
1. En cada **Pull Request** dirigido a la rama `main`.
2. En cada **push** directo a la rama `main`.

El workflow cuenta con políticas de **concurrencia** con cancelación automática, lo que significa que si se realiza un nuevo empuje (push) a una PR mientras una ejecución anterior está activa, la ejecución anterior se cancelará para ahorrar minutos de cómputo.

## ¿Qué valida la CI?

El job principal se llama `Tests and data validation` y realiza los siguientes pasos:
1. **Validación de Sintaxis JSON**: Comprueba que todos los archivos `.json` ubicados en `data/` sean documentos estructurados válidos y puedan ser analizados sin errores.
2. **Validación de Regeneración de Datos**:
   - Para evitar modificar directamente los archivos clínicos versionados dentro del espacio de trabajo, la CI crea un directorio temporal (`tmp_ci/data/`).
   - Copia los insumos fuente en dicho directorio y ejecuta los scripts de generación (`build_priority_draft.py`, `promote_measurement_priority.py`, `build_protocols_draft.py`, y `promote_protocols.py`) utilizando el contexto del directorio temporal.
   - Finalmente, realiza una comparación byte por byte (`diff -u`) entre los artefactos resultantes y los correspondientes archivos versionados en la rama:
     - `data/measurement-priority.draft.json`
     - `data/measurement-priority.json`
     - `data/protocols.draft.json`
     - `data/protocols.json`
     - `data/protocols.beta.json`
     Si se detecta cualquier diferencia o desalineación, el workflow fallará inmediatamente.
3. **Ejecución de Pruebas**: Ejecuta la suite de pruebas unitarias y de integración (incluyendo pruebas sobre Headless Chrome) mediante Pytest (`PYTHONPATH=. python -m pytest -q`).
4. **Estado del Repositorio**: Ejecuta `git diff --exit-code` para asegurar que el pipeline no ensucie el espacio de trabajo ni deje archivos modificados sin registrar.

## Actualizaciones de Entorno y Dependencias

- **Versión de Python**: El workflow utiliza Python `3.13`. Para cambiar la versión de Python, actualice el campo `python-version` en el archivo `.github/workflows/ci.yml`.
- **Caché**: Se utiliza la acción oficial `actions/setup-python@v6` con el parámetro `cache: "pip"` para acelerar la descarga e instalación de paquetes.
- **Acciones (GitHub Actions)**: Se emplean versiones modernas y seguras de las acciones oficiales (`actions/checkout@v6` y `actions/setup-python@v6`).
- **Navegador Chrome**: Para las pruebas de interfaz que requieren Headless Chrome en el runner de Ubuntu, el pipeline localiza dinámicamente el ejecutable de Chrome (o Chromium) disponible en el sistema y exporta su ubicación mediante la variable de entorno `CHROME_PATH`.

## Protección de la Rama Principal (`main`)

Para garantizar que ningún cambio de código o de datos clínicos rompa la aplicación, se debe configurar una regla de protección de rama (Ruleset) en GitHub para `main` que:
1. Exija la aprobación de Pull Requests antes de fusionar.
2. Requiera que el check de estado **`Tests and data validation`** finalice con éxito antes de permitir el merge.
