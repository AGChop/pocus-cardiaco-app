# Revisión Clínica del Protocolo RUSH (Borrador)

## Objetivo
Establecer un borrador clínico de datos estructurado, reproducible y verificable del examen RUSH (Rapid Ultrasound in Shock) para servir como fundamento de datos clínicos en la aplicación POCUS Cardíaco.

## Alcance
Este borrador está dirigido al personal médico en formación (residentes y médicos de áreas críticas) como una guía rápida y de consulta en el punto de atención. Abarca la evaluación tridimensional (La Bomba, El Tanque y Las Tuberías) sin proponer diagnósticos automáticos ni sustituir el criterio del operador.

## Fuentes
1. **Perera P, Mailhot T, Riley D, Mandavia D.**
   *The RUSH exam: Rapid Ultrasound in SHock in the evaluation of the critically ill.*
   Emergency Medicine Clinics of North America. 2010.
   **PMID:** 19945597 | **DOI:** 10.1016/j.emc.2009.09.010 | Citation Page: **28(1):29-56, vii.**
2. **Seif D, Perera P, Mailhot T, Riley D, Mandavia D.**
   *Bedside Ultrasound in Resuscitation and the Rapid Ultrasound in Shock Protocol.*
   Critical Care Research and Practice. 2012.
   **PMCID:** PMC3485910 | **DOI:** 10.1155/2012/503254
3. **Atkinson P, Bowra J, Milne J, et al.**
   *International Federation for Emergency Medicine Consensus Statement: Sonography in hypotension and cardiac arrest (SHoC).*
   Canadian Journal of Emergency Medicine.
   **DOI:** 10.1017/cem.2016.394

---

## Esquema del Protocolo

El protocolo se organiza de forma didáctica en la evaluación de tres áreas fisiológicas (La Bomba, El Tanque y Las Tuberías), aunque la secuencia práctica debe ser flexible y adaptarse a la inestabilidad del paciente.

### La Bomba (Pump)
*   **Evaluación:** Enfocada en la presencia de derrame pericárdico, función sistólica del VI y sobrecarga o tamaño del VD.
*   **Límites Clínicos:**
    *   Una relación VD/VI elevada de forma aislada no diagnostica embolia pulmonar (debe valorarse hipertensión pulmonar previa o cronicidad).
    *   La ausencia de derrame pericárdico no excluye choque obstructivo (ej. neumotórax a tensión).
    *   Una función sistólica global del ventrículo izquierdo aparentemente preservada o hiperdinámica no excluye por sí sola un choque cardiogénico, por ejemplo cuando existe disfunción aguda del ventrículo derecho, enfermedad valvular aguda o una complicación mecánica. Debe integrarse con el gasto cardiaco, las condiciones de carga y el contexto clínico.

### El Tanque (Tank)
*   **Evaluación:** Enfocada en el volumen efectivo. Incluye diámetro y colapsabilidad de la VCI, congestión pulmonar (líneas B) o neumotórax (líneas A y deslizamiento), y presencia de líquido libre abdominal.
*   **Límites Clínicos:**
    *   La vena cava inferior de forma aislada no define volemia ni predice con precisión la respuesta a volumen en todos los pacientes (especialmente bajo ventilación mecánica).
    *   Una VCI pequeña no obliga a administrar líquidos, ni una pletórica confirma taponamiento o congestión por sí sola.

### Las Tuberías (Pipes)
*   **Evaluación:** Evaluación de los grandes vasos enfocada en aorta abdominal y la búsqueda de trombosis venosa profunda (TVP).
*   **Límites Clínicos:**
    *   Un examen limitado o negativo no excluye por completo una TVP.
    *   No poder visualizar la aorta (por interposición de gas) no excluye un aneurisma.
    *   El protocolo RUSH no sustituye a los estudios vasculares definitivos (angioTAC, ultrasonido dúplex completo).
    *   **IDs vinculados vacíos:** Las listas de IDs vinculados se mantienen vacías en este borrador de datos clínicos (`linked_window_ids` y `linked_measurement_ids` vacías). Esto se debe a que no se inventaron IDs para forzar una falsa vinculación, reconociendo que la base de datos actual del proyecto está plenamente centrada en POCUS cardíaco y carece de ventanas u hojas de mediciones vasculares abdominales o periféricas. Esta limitación de la base de datos actual no elimina a las Tuberías del alcance del protocolo clínico RUSH; simplemente documenta que no existen IDs preexistentes compatibles para enlazarlos en esta versión.

---

## Límites de Interpretación y Advertencias Clínicas

1.  **No Diagnósticos Deterministas:** Se prohíben tablas del tipo "hallazgo X = diagnóstico Y". Todo hallazgo debe describirse como "compatible con", "apoya", "aumenta la sospecha" o "debe integrarse con".
2.  **No Retrasar la Reanimación:** La realización del protocolo no debe retrasar la infusión de volumen, fármacos vasoactivos o maniobras de RCP.
3.  **Resultado Negativo:** Un protocolo RUSH completamente negativo no excluye por sí solo todas las causas de choque.
4.  **Procedimientos Invasivos:** El examen no debe retrasar la reanimación ni otras intervenciones salvavidas. Cuando sea necesario un procedimiento invasivo para el cual exista una técnica ecoguiada validada, debe considerarse la guía ecográfica en tiempo real por personal capacitado, siempre que sea factible y no retrase una intervención urgente.

---

## Control de Consistencia e IDs

### Lista de IDs Vinculados
Los siguientes IDs fueron verificados y mapeados exitosamente con las bases de datos existentes:

*   **IDs de Ventanas (`windows.json`):**
    *   `plax` (Paraesternal eje largo)
    *   `psax` (Paraesternal eje corto)
    *   `a4c` (Apical 4 cámaras)
    *   `subcostal_4c` (Subcostal 4 cámaras)
    *   `subcostal_ivc` (Subcostal eje largo de VCI)
*   **IDs de Mediciones (`measurements.json`):**
    *   `derrame_pericardico_pequeno` (Derrame pericárdico pequeño)
    *   `derrame_pericardico_moderado` (Derrame pericárdico moderado)
    *   `derrame_pericardico_grande` (Derrame pericárdico grande)
    *   `fevi` (Fracción de eyección del ventrículo izquierdo)
    *   `epss` (Separación septal del punto E)
    *   `diametro_basal_vd` (Diámetro basal del ventrículo derecho)
    *   `relacion_vd_vi` (Relación VD/VI)
    *   `tapse_meas` (Excursión sistólica del plano del anillo tricuspídeo)
    *   `s_prima_vd` (Velocidad sistólica del anillo tricuspídeo)
    *   `colapso_vd_meas` (Colapso diastólico del VD)
    *   `diametro_vci_meas` (Diámetro de VCI)
    *   `colapsabilidad_vci_meas` (Colapsabilidad de VCI)
    *   `distensibilidad_vci_meas` (Distensibilidad de VCI)
    *   `vci_pletorica_meas` (VCI pletórica)

### IDs que no pudieron vincularse (No existentes en el proyecto)
*   **Ventanas no presentes en `windows.json`:**
    *   `pleural_pulmonar` / `pulmonar` (Evaluación de pleura y parénquima pulmonar).
    *   `aorta_abdominal` (Barrido aórtico abdominal).
    *   `tvp_2_puntos` / `femoral_poplitea` (Compresión en 2 puntos).
*   **Mediciones no presentes en `measurements.json`:**
    *   Medidas específicas de aorta abdominal o diámetros aneurismáticos.
    *   Medidas cuantitativas de compresión de vena femoral/poplítea.
    *   Medidas cuantitativas de líneas B pulmonares o deslizamiento.

### Decisiones que requieren revisión médica
*   Determinar si es conveniente ampliar `windows.json` en fases posteriores para añadir las ventanas extracardiacas (pulmonar, aorta abdominal, TVP 2 puntos).
*   Validar los rangos de colapsabilidad y distensibilidad en pacientes bajo ventilación mecánica invasiva vs. respiración espontánea en el contexto del choque.
