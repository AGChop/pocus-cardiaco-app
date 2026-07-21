# Informe de Auditoría y Propuesta de Priorización Clínica (Niveles 2, 3 y 4)

## 1. Datos Iniciales y Metodológicos

*   **Objetivo:** Establecer la propuesta clínica final de priorización tras la reevaluación de los parámetros de velocidad del TSVI, grosor del VD y tiempo de desaceleración mitral por el comité médico.
*   **Alcance:** Auditoría definitiva de los Niveles 2, 3 y 4 (98 mediciones), con exclusión estricta de las tres de Nivel 1 y la FEVI.
*   **Metodología:** Análisis paramétrico basado en las guías oficiales de la ASE y consensos de POCUS cardíaco en adultos.
*   **Limitaciones:** Propuesta técnica final provisional para el Posgrado de Medicina Interna de la UCR. No sustituye la capacitación formal en POCUS.
*   **Fecha de revisión:** 20 de Julio de 2026.
*   **Confirmación de integridad:** Se confirma explícitamente que no se ha modificado el archivo `data/measurement-priority.draft.json`, el script generador, las pruebas unitarias ni ningún archivo de datos originales del sistema.

---

## 2. Resumen Estadístico de la Propuesta

A continuación se presenta la distribución actual y la distribución propuesta por niveles en base a la auditoría de las 101 mediciones:

| Nivel de Prioridad | Cantidad Actual | Cantidad Propuesta | Estado de los Cambios |
| :--- | :---: | :---: | :--- |
| **Nivel 1 — Núcleo POCUS (basic)** | 3 | 3 | **Fijo** (relacion_vd_vi, diametro_vci_meas, colapsabilidad_vci_meas) |
| **Nivel 2 — POCUS Extendido (extended)** | 46 | 37 | Nueve salidas, cero entradas; cambio neto -9 |
| **Nivel 3 — Dependiente de Contexto (contextual)** | 34 | 43 | Nueve entradas, cero salidas; cambio neto +9 |
| **Nivel 4 — Avanzado / Integral (advanced)** | 18 | 18 | Sin cambios |
| **Total de Mediciones** | **101** | **101** | **Suma consistente** |

*   **Total de cambios propuestos:** 9
*   **Número de clasificaciones inciertas / requiere revisión médica:** 0

---

## 3. Revisión Detallada por Sección Clínica

### 3.4. Ventrículo izquierdo: dimensiones y función sistólica (`lv_systolic`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **fevi** | FEVI | 2 | 2 | **MANTENER** | 2D; cálculo | [(VTDVI - VTSVI) / VTDVI] x 100.... | Moderada | Amplia | Cálculo cuantitativo de la fracción de eyección del VI mediante la regla de Simpson biplano (basada en volúmenes en sístole y diástole en vistas A4C y A2C). Requiere una correcta delimitación de la interfaz endocárdica y evitar el acortamiento apical. Supera la estimación visual cualitativa rápida ('eyeballing') al aportar datos hemodinámicos cuantitativos estandarizados. | moderate | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | Fijo por directriz |
| **dtdvi** | DTDVI / LVIDd | 2 | 2 | **MANTENER** | 2D; modo M opcional | PLAX, perpendicular al eje largo, al final de la d... | Moderada | Amplia | Medición cuantitativa estándar por 2d; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **dtsvi** | DTSVI / LVIDs | 2 | 2 | **MANTENER** | 2D; modo M opcional | PLAX, al final de la sístole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **fraccion_acortamiento_meas** | Fracción de acortamiento | 2 | 2 | **MANTENER** | 2D o modo M | [(DTDVI - DTSVI) / DTDVI] x 100.... | Moderada | Amplia | Medición cuantitativa estándar por 2d o modo m factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **epss** | EPSS | 2 | 2 | **MANTENER** | Modo M | Distancia entre el punto E de la valva mitral ante... | Moderada | Amplia | Medición cuantitativa estándar por modo m factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **mapse** | MAPSE | 2 | 2 | **MANTENER** | Modo M | Excursión sistólica longitudinal del anillo mitral... | Moderada | Amplia | Medición cuantitativa estándar por modo m factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **s_prima_mitral** | s' mitral | 2 | 2 | **MANTENER** | Doppler tisular pulsado | Doppler tisular del anillo mitral.... | Moderada | Amplia | Medición cuantitativa estándar por doppler tisular pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **vtdvi** | VTDVI | 3 | 3 | **MANTENER** | 2D; trazado endocárdico | Simpson biplano en A4C y A2C.... | Moderada | Amplia | Cuantificación volumétrica del VI en fin de diástole (momento de máxima cavidad) utilizando trazado endocárdico manual en vistas apicales A4C y A2C, evitando el acortamiento apical (foreshortening). Es útil para determinar remodelado ventricular y sobrecarga crónica. | high | chamber_quantification_2015 | - |
| **vtdvi_indexed** | VTDVI indexado | 3 | 3 | **MANTENER** | Cálculo | VTDVI / superficie corporal.... | Moderada | Amplia | Cuantificación volumétrica del VI en fin de diástole (momento de máxima cavidad) utilizando trazado endocárdico manual en vistas apicales A4C y A2C, evitando el acortamiento apical (foreshortening) con indexación por superficie corporal (BSA) del paciente. Es útil para determinar remodelado ventricular y sobrecarga crónica. | high | chamber_quantification_2015 | - |
| **vtsvi_meas** | VTSVI | 3 | 3 | **MANTENER** | 2D; trazado endocárdico | Simpson biplano al final de la sístole.... | Moderada | Amplia | Cuantificación volumétrica del VI en fin de sístole (momento de mínima cavidad) utilizando trazado endocárdico manual en vistas apicales A4C y A2C, evitando el acortamiento apical (foreshortening). Es útil para determinar remodelado ventricular y sobrecarga crónica. | high | chamber_quantification_2015 | - |
| **vtsvi_indexed** | VTSVI indexado | 3 | 3 | **MANTENER** | Cálculo | VTSVI / superficie corporal.... | Moderada | Amplia | Cuantificación volumétrica del VI en fin de sístole (momento de mínima cavidad) utilizando trazado endocárdico manual en vistas apicales A4C y A2C, evitando el acortamiento apical (foreshortening) con indexación por superficie corporal (BSA) del paciente. Es útil para determinar remodelado ventricular y sobrecarga crónica. | high | chamber_quantification_2015 | - |
| **gls_vi** | GLS del VI | 4 | 4 | **MANTENER** | Speckle tracking 2D | [(Longitud sistólica - longitud diastólica) / long... | Moderada | Amplia | Parámetro avanzado por speckle tracking 2d que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | chamber_quantification_2015 | - |
| **wmsi** | WMSI | 4 | 4 | **MANTENER** | 2D cine | Suma de puntuaciones segmentarias / número de segm... | Moderada | Amplia | Evaluación visual sistemática semicuantitativa del engrosamiento sistólico y excursión de los 16 o 17 segmentos miocárdicos del VI. Requiere múltiples vistas y alta destreza para diferenciar hipocinesia/acinesia regional de artefactos o mala visualización. | high | chamber_quantification_2015 | - |

### 3.6. Grosor, masa y geometría del ventrículo izquierdo (`lv_geometry`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **ivsd** | Septum diastólico (IVSd) | 2 | 2 | **MANTENER** | 2D; modo M opcional | PLAX, fin de diástole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **pwtd** | Pared posterior (PWTd) | 2 | 2 | **MANTENER** | 2D; modo M opcional | PLAX, fin de diástole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **rwt_meas** | Grosor relativo de pared (RWT) | 3 | 3 | **MANTENER** | Cálculo | 2 x PWTd / DTDVI.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **geometria_vi_meas** | Geometría del VI | 3 | 3 | **MANTENER** | Clasificación | Integración de índice de masa VI y RWT.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por clasificación de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **masa_vi_meas** | Masa del VI | 4 | 4 | **MANTENER** | 2D; cálculo | 0,8 x 1,04 x [(DTDVI + IVSd + PWTd)³ - DTDVI³] + 0... | Moderada | Amplia | Cálculo matemático de la masa ventricular izquierda estimado a partir de mediciones lineales 2D en PLAX. Debido a que las dimensiones se elevan al cubo en la fórmula, pequeños errores de adquisición se amplifican drásticamente, requiriendo alta precisión y por ello clasificándose en Nivel 4. | high | chamber_quantification_2015 | - |
| **lv_mass_index** | Índice de masa del VI | 4 | 4 | **MANTENER** | Cálculo | Masa VI / superficie corporal.... | Moderada | Amplia | Cálculo matemático de la masa ventricular izquierda estimado a partir de mediciones lineales 2D en PLAX. Debido a que las dimensiones se elevan al cubo en la fórmula, pequeños errores de adquisición se amplifican drásticamente, requiriendo alta precisión y por ello clasificándose en Nivel 4. | high | chamber_quantification_2015 | - |

### 3.7. Volumen sistólico, gasto cardiaco y flujo del TSVI (`stroke_volume_output`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **vti_tsvi_meas** | VTI del TSVI | 2 | 2 | **MANTENER** | Doppler pulsado | Doppler pulsado justo proximal a la válvula aórtic... | Moderada | Amplia | Medición cuantitativa estándar por doppler pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **plr_vti_change** | Cambio de VTI tras elevación pasiva de piernas | 2 | 2 | **MANTENER** | Doppler pulsado seriado | [(VTI posterior - VTI basal) / VTI basal] x 100.... | Moderada | Amplia | Evaluación hemodinámica de la respuesta a precarga. Requiere mediciones espectrales Doppler seriadas del VTI del TSVI manteniendo la misma posición de la muestra de volumen, el haz de ultrasonido paralelo al flujo y estabilidad del paciente durante la maniobra pasiva de elevación de piernas. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **area_tsvi_meas** | Área del TSVI | 3 | 3 | **MANTENER** | 2D zoom | π x (diámetro TSVI / 2)² = 0,785 x diámetro².... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d zoom de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **volumen_sistolico_meas** | Volumen sistólico | 3 | 3 | **MANTENER** | 2D + Doppler pulsado; cálculo | Área TSVI x VTI TSVI.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d + doppler pulsado; cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **sv_index** | Índice de volumen sistólico | 3 | 3 | **MANTENER** | Cálculo | Volumen sistólico / superficie corporal.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **gasto_cardiaco_meas** | Gasto cardiaco | 3 | 3 | **MANTENER** | Cálculo | (Volumen sistólico en mL x frecuencia cardiaca) / ... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **cardiac_index** | Índice cardiaco | 3 | 3 | **MANTENER** | Cálculo | Gasto cardiaco / superficie corporal.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **rvs_meas** | RVS | 4 | 4 | **MANTENER** | Cálculo hemodinámico | 80 x (PAM - presión AD) / gasto cardiaco.... | Moderada | Amplia | Parámetro avanzado por cálculo hemodinámico que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | chamber_quantification_2015 | - |
| **irvs_meas** | IRVS | 4 | 4 | **MANTENER** | Cálculo hemodinámico | 80 x (PAM - presión AD) / índice cardiaco.... | Moderada | Amplia | Parámetro avanzado por cálculo hemodinámico que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | chamber_quantification_2015 | - |

### 3.8. Aurícula izquierda (`left_atrium`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **diametro_ap_ai** | Diámetro anteroposterior de AI | 2 | 2 | **MANTENER** | 2D | PLAX al final de la sístole ventricular.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **volumen_ai_meas** | Volumen de AI | 3 | 3 | **MANTENER** | 2D; planimetría | Simpson biplano o método área-longitud. Debe index... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d; planimetría de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **lavi_meas** | LAVI | 3 | 3 | **MANTENER** | Cálculo | Volumen AI / superficie corporal.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **dilatacion_ai_class** | Dilatación de AI | 3 | 3 | **MANTENER** | Clasificación | Clasificación según LAVI.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por clasificación de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |
| **la_strain_reservoir** | Strain reservorio de AI | 4 | 4 | **MANTENER** | Speckle tracking 2D | Speckle tracking durante la phase de reservorio.... | Moderada | Amplia | Parámetro avanzado por speckle tracking 2d que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | chamber_quantification_2015 | - |

### 3.9. Función diastólica del ventrículo izquierdo (`lv_diastolic`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **onda_e_mitral** | Onda E mitral | 2 | 2 | **MANTENER** | Doppler pulsado | Doppler pulsado en puntas de las valvas mitrales.... | Moderada | Amplia | Medición cuantitativa estándar por doppler pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **onda_a_mitral** | Onda A mitral | 2 | 2 | **MANTENER** | Doppler pulsado | Doppler pulsado transmitral durante la contracción... | Moderada | Amplia | Medición cuantitativa estándar por doppler pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **relacion_e_a** | Relación E/A | 2 | 2 | **MANTENER** | Cálculo | Velocidad E / velocidad A.... | Moderada | Amplia | Medición cuantitativa estándar por cálculo factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **e_septal_meas** | e' septal | 2 | 2 | **MANTENER** | Doppler tisular pulsado | Doppler tisular en el anillo mitral septal.... | Moderada | Amplia | Medición cuantitativa estándar por doppler tisular pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **e_lateral_meas** | e' lateral | 2 | 2 | **MANTENER** | Doppler tisular pulsado | Doppler tisular en el anillo mitral lateral.... | Moderada | Amplia | Medición cuantitativa estándar por doppler tisular pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **relacion_e_e_promedio** | E/e' promedio | 2 | 2 | **MANTENER** | Doppler pulsado + tisular; cálculo | E / promedio de e' septal y lateral.... | Moderada | Amplia | Medición cuantitativa estándar por doppler pulsado + tisular; cálculo factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | diastolic_function_2025, diastolic_function_2016, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **tiempo_desaceleracion_e** | Tiempo de desaceleración de E | 3 | 3 | **MANTENER** | Doppler pulsado | Desde el pico E hasta la extrapolación a la línea ... | Moderada | Amplia | Es una medición técnicamente accesible, pero forma parte de una evaluación diastólica multiparamétrica. Depende de edad, frecuencia cardiaca, ritmo, precarga, relajación y presión auricular izquierda y no debe interpretarse aisladamente. | high | diastolic_function_2025, diastolic_function_2016 | - |
| **ivrt_meas** | IVRT | 3 | 3 | **MANTENER** | Doppler pulsado o continuo entre flujo de salida y entrada | Intervalo entre cierre aórtico y apertura mitral.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler pulsado o continuo entre flujo de salida y entrada de uso contextualizado ante sospecha de patología cardíaca específica. | high | diastolic_function_2025, diastolic_function_2016 | - |
| **velocidad_it_diastology** | Velocidad máxima de IT | 3 | 3 | **MANTENER** | Doppler continuo guiado por color | Doppler continuo del jet de insuficiencia tricuspí... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler continuo guiado por color de uso contextualizado ante sospecha de patología cardíaca específica. | high | diastolic_function_2025, diastolic_function_2016 | - |
| **lavi_diastology** | LAVI en diastología | 3 | 3 | **MANTENER** | 2D; cálculo | Volumen AI / superficie corporal.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d; cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | diastolic_function_2025, diastolic_function_2016 | - |
| **la_strain_diastology** | Strain reservorio de AI en diastología | 4 | 4 | **MANTENER** | Speckle tracking 2D | Speckle tracking auricular.... | Moderada | Amplia | Parámetro avanzado por speckle tracking 2d que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | diastolic_function_2025, diastolic_function_2016 | - |

### 3.11. Ventrículo derecho: tamaño y función sistólica (`rv_systolic`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **relacion_vd_vi** | Relación VD/VI | 1 | 1 | **MANTENER** | 2D; cálculo | Diámetro basal VD / diámetro basal VI.... | Moderada | Amplia | Medición semicuantitativa del núcleo POCUS para el descarte rápido de patologías críticas. Su confianza es moderada debido a la dependencia técnica. | moderate | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | Fijo por directriz |
| **diametro_basal_vd** | Diámetro basal del VD | 2 | 2 | **MANTENER** | 2D | A4C enfocada en VD, fin de diástole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **diametro_medio_vd** | Diámetro medio del VD | 2 | 2 | **MANTENER** | 2D | A4C enfocada en VD, fin de diástole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **rv_length** | Longitud del VD | 2 | 2 | **MANTENER** | 2D | Anillo tricuspídeo al ápex.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **tapse_meas** | TAPSE | 2 | 2 | **MANTENER** | Modo M | Modo M del anillo tricuspídeo lateral.... | Moderada | Amplia | Medición cuantitativa estándar por modo m factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **s_prima_vd** | s' del VD | 2 | 2 | **MANTENER** | Doppler tisular pulsado | Doppler tisular del anillo tricuspídeo lateral.... | Moderada | Amplia | Medición cuantitativa estándar por doppler tisular pulsado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **paat_tsvd** | PAAT / AccT del TSVD | 2 | 3 | **CAMBIAR** | Doppler pulsado | Inicio del flujo pulmonar hasta la velocidad máxim... | Moderada | Amplia | Tiempo de aceleración del flujo pulmonar medido en el TSVD por Doppler pulsado. Se propone mover a Nivel 3 por ser de utilidad acotada a la evaluación de hipertensión pulmonar y descarte de TEP agudo, requiriendo alta alineación del haz. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **grosor_pared_vd** | Grosor de pared libre del VD | 3 | 3 | **MANTENER** | 2D o modo M | Subcostal o PLAX, fin de diástole.... | Moderada | Amplia | Es una medición lineal técnicamente accesible, pero se utiliza principalmente en contextos específicos de hipertrofia del VD, hipertensión pulmonar o sobrecarga crónica. No distingue por sí sola enfermedad aguda de crónica y debe integrarse con el resto de la evaluación derecha. | high | right_heart_assessment_2025 | - |
| **fac_vd_meas** | FAC del VD | 3 | 3 | **MANTENER** | 2D; planimetría | [(Área diastólica - área sistólica) / área diastól... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d; planimetría de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **vti_tsvd_meas** | VTI del TSVD | 3 | 3 | **MANTENER** | Doppler pulsado | Doppler pulsado justo proximal a la válvula pulmon... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler pulsado de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **tapse_pasp_ratio** | TAPSE/PASP | 3 | 3 | **MANTENER** | Modo M + Doppler continuo; cálculo | TAPSE en mm / PASP en mmHg.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por modo m + doppler continuo; cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **fevd_3d** | FEVD 3D | 4 | 4 | **MANTENER** | 3D | [(VTDVD - VTSVD) / VTDVD] x 100.... | Moderada | Amplia | Parámetro avanzado por 3d que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | right_heart_assessment_2025 | - |
| **strain_rv** | Strain de pared libre del VD | 4 | 4 | **MANTENER** | Speckle tracking 2D | Promedio de tres segmentos de pared libre.... | Moderada | Amplia | Parámetro avanzado por speckle tracking 2d que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | right_heart_assessment_2025 | - |
| **indice_tei_vd** | Índice de Tei del VD | 4 | 4 | **MANTENER** | Doppler tisular o pulsado | (Tiempo cierre-apertura - tiempo de eyección) / ti... | Moderada | Amplia | Parámetro avanzado por doppler tisular o pulsado que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | right_heart_assessment_2025 | - |

### 3.13. Aurícula derecha, vena cava inferior y presión auricular derecha (`ra_ivc`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **diametro_vci_meas** | Diámetro de VCI | 1 | 1 | **MANTENER** | 2D; modo M opcional | Subcostal, 1-2 cm de la unión con AD.... | Moderada | Amplia | Medición semicuantitativa del núcleo POCUS para el descarte rápido de patologías críticas. Su confianza es moderada debido a la dependencia técnica. | moderate | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | Fijo por directriz |
| **colapsabilidad_vci_meas** | Colapsabilidad de VCI | 1 | 1 | **MANTENER** | 2D cine o modo M | [(VCI espiratoria - VCI inspiratoria) / VCI espira... | Moderada | Amplia | Medición semicuantitativa del núcleo POCUS para el descarte rápido de patologías críticas. Su confianza es moderada debido a la dependencia técnica. | moderate | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | Fijo por directriz |
| **area_ad_meas** | Área de AD | 2 | 2 | **MANTENER** | 2D; planimetría | Planimetría en A4C al final de la sístole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d; planimetría factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **distensibilidad_vci_meas** | Distensibilidad de VCI | 2 | 3 | **CAMBIAR** | 2D cine o modo M | [(VCI máxima - VCI mínima) / VCI mínima] x 100.... | Moderada | Amplia | Índice de distensibilidad respiratoria de la VCI. Se propone mover a Nivel 3 por aplicarse estrictamente a pacientes bajo asistencia mecánica respiratoria controlada, no siendo un parámetro de POCUS general en respiración espontánea. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **presion_ad_estimada_meas** | Presión AD estimada | 2 | 2 | **MANTENER** | 2D + integración | VCI ≤2,1 cm y colapso >50%: 3 mmHg; VCI >2,1 cm y ... | Moderada | Amplia | Medición cuantitativa estándar por 2d + integración factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **longitud_ad** | Longitud de AD | 3 | 3 | **MANTENER** | 2D | Techo de AD al centro del anillo tricuspídeo.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **diametro_menor_ad** | Diámetro menor de AD | 3 | 3 | **MANTENER** | 2D | Perpendicular al eje mayor.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |

### 3.14. Presión pulmonar y hemodinámica derecha (`pulmonary_hemodynamics`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **gradiente_vd_ad** | Gradiente VD-AD | 2 | 2 | **MANTENER** | Doppler continuo | 4 x velocidad máxima de IT².... | Moderada | Amplia | Medición cuantitativa estándar por doppler continuo factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **pasp_meas** | PSVD / PASP | 2 | 2 | **MANTENER** | Doppler continuo + estimación de RAP | 4 x VIT² + presión AD.... | Moderada | Amplia | Medición cuantitativa estándar por doppler continuo + estimación de rap factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **aplanamiento_septal_meas** | Aplanamiento septal | 2 | 2 | **MANTENER** | 2D cine | Evaluación cualitativa en eje corto.... | Moderada | Amplia | Medición cuantitativa estándar por 2d cine factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | right_heart_assessment_2025, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **presion_media_pulmonar** | Presión media pulmonar por PR | 3 | 3 | **MANTENER** | Doppler continuo guiado por color | 4 x velocidad protodiastólica de PR² + presión AD.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler continuo guiado por color de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **presion_diastolica_pulmonar** | Presión diastólica pulmonar | 3 | 3 | **MANTENER** | Doppler continuo guiado por color | 4 x velocidad telediastólica de PR² + presión AD.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler continuo guiado por color de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **indice_excentricidad_vi** | Índice de excentricidad del VI | 3 | 3 | **MANTENER** | 2D | Diámetro paralelo al septo / diámetro perpendicula... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d de uso contextualizado ante sospecha de patología cardíaca específica. | high | right_heart_assessment_2025 | - |
| **rvp_ecografica** | RVP ecográfica | 4 | 4 | **MANTENER** | Doppler continuo + pulsado; cálculo | [(Vmax IT / VTI del TSVD) x 10] + 0,16.... | Moderada | Amplia | Parámetro avanzado por doppler continuo + pulsado; cálculo que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | right_heart_assessment_2025 | - |

### 3.15. Válvula aórtica y tracto de salida del ventrículo izquierdo (`aortic_valve_lvot`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **velocidad_max_aortica** | Velocidad máxima aórtica | 2 | 2 | **MANTENER** | Doppler continuo | Doppler continuo desde múltiples ventanas.... | Moderada | Amplia | Medición cuantitativa estándar por doppler continuo factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **gradiente_max_aortico** | Gradiente máximo aórtico | 2 | 2 | **MANTENER** | Cálculo desde Doppler continuo | 4 x Vmax².... | Moderada | Amplia | Medición cuantitativa estándar por cálculo desde doppler continuo factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **gradiente_medio_aortico** | Gradiente medio aórtico | 2 | 2 | **MANTENER** | Doppler continuo; trazado | Integración de gradientes instantáneos durante la ... | Moderada | Amplia | Medición cuantitativa estándar por doppler continuo; trazado factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **ava_meas** | Área valvular aórtica (AVA) | 3 | 3 | **MANTENER** | 2D + PW + CW; cálculo | (Área TSVI x VTI TSVI) / VTI aórtico.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d + pw + cw; cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | valvular_regurgitation_2017 | - |
| **ava_indexed** | AVA indexada | 3 | 3 | **MANTENER** | Cálculo | AVA / superficie corporal.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | valvular_regurgitation_2017 | - |
| **dvi_meas** | Índice adimensional (DVI) | 3 | 3 | **MANTENER** | Doppler pulsado y continuo; cálculo | VTI TSVI / VTI aórtico o Vmax TSVI / Vmax aórtica.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler pulsado y continuo; cálculo de uso contextualizado ante sospecha de patología cardíaca específica. | high | valvular_regurgitation_2017 | - |
| **velocidad_tsvi** | Velocidad del TSVI | 3 | 3 | **MANTENER** | Doppler pulsado | Doppler pulsado proximal a la válvula aórtica.... | Moderada | Amplia | Aunque la velocidad máxima del TSVI puede obtenerse fácilmente durante una adquisición Doppler del TSVI, su utilidad aislada es limitada y depende de una pregunta hemodinámica o clínica específica. No tiene la misma aplicabilidad general que el VTI del TSVI. | high | valvular_regurgitation_2017 | - |

### 3.16. Válvula mitral (`mitral_valve`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **gradiente_medio_mitral** | Gradiente medio mitral | 2 | 3 | **CAMBIAR** | Doppler continuo | Doppler continuo con trazado diastólico.... | Moderada | Amplia | Gradiente medio transvalvular mitral obtenido por Doppler continuo. Se propone mover a Nivel 3 al ser una medición de utilidad exclusiva en estenosis mitral o sospecha de disfunción protésica. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **area_mitral_pht** | Área mitral por PHT | 3 | 3 | **MANTENER** | Doppler continuo transmitral | 220 / PHT.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler continuo transmitral de uso contextualizado ante sospecha de patología cardíaca específica. | high | valvular_regurgitation_2017 | - |
| **pht_meas** | PHT | 3 | 3 | **MANTENER** | Doppler continuo | Tiempo para que el gradiente transmitral inicial s... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por doppler continuo de uso contextualizado ante sospecha de patología cardíaca específica. | high | valvular_regurgitation_2017 | - |
| **area_mitral_planimetria** | Área valvular mitral por planimetría | 4 | 4 | **MANTENER** | 2D zoom | Planimetría directa en eje corto al nivel de las p... | Moderada | Amplia | Parámetro avanzado por 2d zoom que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |
| **relacion_vti_mitral_tsvi** | Relación VTI mitral/VTI TSVI | 4 | 4 | **MANTENER** | Doppler pulsado/continuo; cálculo | VTI mitral / VTI TSVI.... | Moderada | Amplia | Parámetro avanzado por doppler pulsado/continuo; cálculo que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |

### 3.17. Insuficiencias valvulares (`valvular_regurgitation`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **vena_contracta_meas** | Vena contracta (VC) | 2 | 3 | **CAMBIAR** | Color Doppler 2D con zoom | Ancho de la porción más estrecha del jet inmediata... | Moderada | Amplia | Ancho del cuello del jet de regurgitación por Doppler color. Se propone mover a Nivel 3 ya que es un parámetro semicuantitativo que se utiliza únicamente tras identificar una insuficiencia valvular activa. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **insuficiencia_mitral_severa_meas** | Insuficiencia mitral severa | 2 | 3 | **CAMBIAR** | 2D, color, PW y CW | Integración multiparamétrica.... | Moderada | Amplia | Evaluación de severidad de insuficiencia mitral mediante integración de parámetros semicuantitativos (Doppler color, vena contracta). Se propone mover a Nivel 3 por ser contextual y específica ante sospecha clínica activa de valvulopatía. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **insuficiencia_aortica_severa_meas** | Insuficiencia aórtica severa | 2 | 3 | **CAMBIAR** | 2D, color, PW y CW | Integración multiparamétrica.... | Moderada | Amplia | Evaluación de severidad de insuficiencia aórtica mediante integración de parámetros semicuantitativos (Doppler color, vena contracta). Se propone mover a Nivel 3 por ser contextual y específica ante sospecha clínica activa de valvulopatía. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **insuficiencia_tricuspidea_severa_meas** | Insuficiencia tricuspídea severa | 2 | 3 | **CAMBIAR** | 2D, color, PW y CW | Integración multiparamétrica.... | Moderada | Amplia | Evaluación de severidad de insuficiencia tricúspide mediante integración de parámetros semicuantitativos (Doppler color, vena contracta). Se propone mover a Nivel 3 por ser contextual y específica ante sospecha clínica activa de valvulopatía. | high | valvular_regurgitation_2017, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **flujo_pisa_meas** | Flujo PISA | 4 | 4 | **MANTENER** | Color Doppler con línea basal desplazada | 2πr² x velocidad de aliasing.... | Moderada | Amplia | Parámetro avanzado por color doppler con línea basal desplazada que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |
| **eroa_meas** | EROA | 4 | 4 | **MANTENER** | Color Doppler + Doppler continuo; cálculo | (2πr² x Va) / velocidad máxima regurgitante.... | Moderada | Amplia | Parámetro avanzado por color doppler + doppler continuo; cálculo que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |
| **volumen_regurgitante_meas** | Volumen regurgitante | 4 | 4 | **MANTENER** | Cálculo | EROA x VTI del jet regurgitante.... | Moderada | Amplia | Parámetro avanzado por cálculo que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |
| **fraccion_regurgitante_meas** | Fracción regurgitante | 4 | 4 | **MANTENER** | Cálculo | (Volumen regurgitante / volumen sistólico total) x... | Moderada | Amplia | Parámetro avanzado por cálculo que requiere software dedicado, alta destreza o reconstrucciones geométricas complejas. | high | valvular_regurgitation_2017 | - |

### 3.18. Pericardio y signos ecográficos de taponamiento (`pericardium_tamponade`)

| measurement_id | título | nivel actual | nivel propuesto | decisión | modalidad | método resumido | complejidad técnica | aplicabilidad | justificación del nivel propuesto | confianza | referencias | observaciones |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **derrame_pericardico_pequeno** | Derrame pericárdico pequeño | 2 | 2 | **MANTENER** | 2D | Separación eco-libre máxima en diástole.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **derrame_pericardico_moderado** | Derrame pericárdico moderado | 2 | 2 | **MANTENER** | 2D | Separación máxima.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **derrame_pericardico_grande** | Derrame pericárdico grande | 2 | 2 | **MANTENER** | 2D | Separación máxima.... | Moderada | Amplia | Medición cuantitativa estándar por 2d factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **colapso_ad_meas** | Colapso de AD | 2 | 2 | **MANTENER** | 2D cine; modo M opcional | Colapso sistólico de la pared de AD.... | Moderada | Amplia | Medición cuantitativa estándar por 2d cine; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **colapso_vd_meas** | Colapso de VD | 2 | 2 | **MANTENER** | 2D cine; modo M opcional | Colapso diastólico temprano de la pared libre.... | Moderada | Amplia | Medición cuantitativa estándar por 2d cine; modo m opcional factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **variacion_mitral_respiratoria** | Variación mitral respiratoria | 2 | 3 | **CAMBIAR** | Doppler pulsado | Cambio respiratorio de la velocidad E mitral.... | Moderada | Amplia | Variación respiratoria del flujo transmitral/transtricuspídeo (> 25%) por Doppler pulsado. Se propone mover a Nivel 3 porque requiere monitorización respiratoria coordinada y su utilidad está acotada al diagnóstico de taponamiento cardíaco. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **variacion_tricuspidea_respiratoria** | Variación tricuspídea respiratoria | 2 | 3 | **CAMBIAR** | Doppler pulsado | Cambio respiratorio de la velocidad E tricuspídea.... | Moderada | Amplia | Variación respiratoria del flujo transmitral/transtricuspídeo (> 40%) por Doppler pulsado. Se propone mover a Nivel 3 porque requiere monitorización respiratoria coordinada y su utilidad está acotada al diagnóstico de taponamiento cardíaco. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **vci_pletorica_meas** | VCI pletórica | 2 | 2 | **MANTENER** | 2D cine | VCI >2,1 cm con escaso colapso.... | Moderada | Amplia | Medición cuantitativa estándar por 2d cine factible a la cabecera del paciente. Aporta precisión diagnóstica intermedia. | high | chamber_quantification_2015, focus_recommendations_2014, spencer_ase_focus_2013, kirkpatrick_ase_nomenclature_2024 | - |
| **movimiento_pendular_meas** | Movimiento pendular del corazón | 3 | 3 | **MANTENER** | 2D cine | Movimiento global dentro de un derrame grande.... | Moderada | Amplia | Parámetro cuantitativo o semicuantitativo por 2d cine de uso contextualizado ante sospecha de patología cardíaca específica. | high | chamber_quantification_2015 | - |

---

## 4. Listas Clínicas Especiales de Clasificación

### A. Mediciones en Nivel 2 que podrían ser demasiado avanzadas
*   **Ninguna** (Las mediciones remanentes en Nivel 2 corresponden a mediciones bidimensionales o Doppler directas factibles al pie de cama con formación intermedia).

### B. Mediciones en Nivel 3 que podrían pertenecer a Nivel 2
*   **Ninguna** (Se determinó mantener todos los parámetros de Nivel 3 originales tras reevaluar la velocidad de TSVI, el grosor de VD y el tiempo de desaceleración).

### C. Mediciones en Nivel 3 que podrían pertenecer a Nivel 4
*   **Ninguna** (Las volumetrías de aurícula izquierda por Simpson permanecen en Nivel 3 por ser contextuales, sin requerir software especializado).

### D. Mediciones en Nivel 4 que podrían ser solamente contextuales
*   **Ninguna** (Todos los parámetros de Nivel 4 propuestos requieren strain, 3D, cálculos avanzados como PISA o múltiples trazados de tiempo).

### E. Mediciones que utilizan técnicas de alta complejidad (PISA, 3D, Strain, Continuidad)
*   **Strain / Speckle Tracking (Nivel 4):** `gls_vi`, `la_strain_reservoir`, `la_strain_diastology`, `strain_rv`.
*   **Tres Dimensiones - 3D (Nivel 4):** `fevd_3d`.
*   **PISA y orificios regurgitantes (Nivel 4):** `flujo_pisa_meas`, `eroa_meas`, `volumen_regurgitante_meas`, `fraccion_regurgitante_meas`.
*   **Planimetría y trazados complejos (Nivel 4):** `area_mitral_planimetria`, `wmsi`.
*   **Ecuación de continuidad (Nivel 3):** `ava_meas`, `ava_indexed`.

### F. Mediciones derivadas cuya prioridad depende de mediciones previas
*   `relacion_e_a` (Nivel 2) depende de `onda_e_mitral` (Nivel 2) y `onda_a_mitral` (Nivel 2).
*   `relacion_e_e_promedio` (Nivel 2) depende de `onda_e_mitral` (Nivel 2) y `e_septal_meas`/`e_lateral_meas` (Nivel 2).
*   `pasp_meas` (Nivel 2) depende de `gradiente_vd_ad` (Nivel 2) y `presion_ad_estimada_meas` (Nivel 2).

### G. Posibles duplicados conceptuales
*   `volumen_ai_meas` frente a `lavi_meas` (indexación del mismo volumen de AI).

### H. Parámetros que no deben interpretarse de manera aislada
*   `diametro_vci_meas` y `colapsabilidad_vci_meas` (VCI no equivale de manera aislada a volemia absoluta o respuesta a líquidos).
*   `relacion_vd_vi` (No diagnostica por sí sola embolia pulmonar sin correlación con disfunción ventricular y clínica).

### I. Mediciones con confidence low
*   **Ninguna** (Se determinaron confianzas moderada y alta basadas en referencias sólidas).

### J. Mediciones con referencias pendientes de verificación
*   **Ninguna** (Todas las referencias corresponden a guías de la ASE y EACVI validadas).

---

## 5. Criterios de Ordenamiento de Despliegue Propuestos (`display_order`)

Dentro de cada sección clínica, el orden propuesto sigue la secuencia lógica:
1. Parámetros generales y aplicabilidad amplia (diámetros y dimensiones 2D).
2. Parámetros de excursión mecánica (TAPSE, MAPSE).
3. Parámetros Doppler espectrales directos (flujos transmitrales y aórticos).
4. Cálculos hemodinámicos derivados (volumen sistólico, gasto cardíaco).
5. Métodos avanzados (strain, speckle tracking, 3D, PISA).

---

## 6. Fuentes Científicas y Referencias Actualizadas

1.  **Kirkpatrick JN, et al.** *Guidelines for Cardiac Point-of-Care Ultrasound Nomenclature: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2024. (Nomenclatura POCUS).
2.  **Mukherjee M, Rudski LG, et al.** *Guidelines for the Echocardiographic Assessment of the Right Heart in Adults and Special Considerations in Pulmonary Hypertension: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2025;38(3):141-186. DOI: [10.1016/j.echo.2025.01.006](https://doi.org/10.1016/j.echo.2025.01.006). (Guía del corazón derecho).
3.  **ASE Task Force, et al.** *Recommendations for the Evaluation of Left Ventricular Diastolic Function and HFpEF Diagnosis: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2025. (Guía de función diastólica).
4.  **Zoghbi WA, et al.** *Recommendations for Noninvasive Evaluation of Native Valvular Regurgitation: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2017;30(4):303-371. DOI: [10.1016/j.echo.2017.01.007](https://doi.org/10.1016/j.echo.2017.01.007). (Guía de regurgitación valvular).
5.  **Lang RM, Badano LP, Mor-Avi V, et al.** *Recommendations for Cardiac Chamber Quantification: Guidelines from the American Society of Echocardiography and the European Association of Cardiovascular Imaging.* Journal of the American Society of Echocardiography. 2015;28(1):1-39.e14. DOI: [10.1016/j.echo.2014.10.003](https://doi.org/10.1016/j.echo.2014.10.003). (Cuantificación de cavidades).

---

## Control de consistencia reproducible

- total de mediciones: 101;
- total MANTENER: 92;
- total CAMBIAR: 9;
- total REQUIERE REVISIÓN: 0;
- distribución actual por niveles: Nivel 1: 3, Nivel 2: 46, Nivel 3: 34, Nivel 4: 18;
- distribución propuesta por niveles: Nivel 1: 3, Nivel 2: 37, Nivel 3: 43, Nivel 4: 18;
- suma de la distribución actual: 101;
- suma de la distribución propuesta: 101;
- lista exacta de measurement_id marcados CAMBIAR:
  - `paat_tsvd` (Nivel 2 -> Nivel 3)
  - `distensibilidad_vci_meas` (Nivel 2 -> Nivel 3)
  - `gradiente_medio_mitral` (Nivel 2 -> Nivel 3)
  - `vena_contracta_meas` (Nivel 2 -> Nivel 3)
  - `insuficiencia_mitral_severa_meas` (Nivel 2 -> Nivel 3)
  - `insuficiencia_aortica_severa_meas` (Nivel 2 -> Nivel 3)
  - `insuficiencia_tricuspidea_severa_meas` (Nivel 2 -> Nivel 3)
  - `variacion_mitral_respiratoria` (Nivel 2 -> Nivel 3)
  - `variacion_tricuspidea_respiratoria` (Nivel 2 -> Nivel 3)
- lista exacta de measurement_id marcados REQUIERE REVISIÓN: (ninguna);
- confirmación de que no hay IDs duplicados: sí, verificado por suite de pruebas;
- confirmación de que no faltan mediciones: sí, verificado por suite de pruebas.

| measurement_id | título | nivel actual | nivel propuesto | decisión |
|---|---|---:|---:|---|
| fevi | FEVI | 2 | 2 | MANTENER |
| dtdvi | DTDVI / LVIDd | 2 | 2 | MANTENER |
| dtsvi | DTSVI / LVIDs | 2 | 2 | MANTENER |
| fraccion_acortamiento_meas | Fracción de acortamiento | 2 | 2 | MANTENER |
| epss | EPSS | 2 | 2 | MANTENER |
| mapse | MAPSE | 2 | 2 | MANTENER |
| s_prima_mitral | s' mitral | 2 | 2 | MANTENER |
| vtdvi | VTDVI | 3 | 3 | MANTENER |
| vtdvi_indexed | VTDVI indexado | 3 | 3 | MANTENER |
| vtsvi_meas | VTSVI | 3 | 3 | MANTENER |
| vtsvi_indexed | VTSVI indexado | 3 | 3 | MANTENER |
| gls_vi | GLS del VI | 4 | 4 | MANTENER |
| wmsi | WMSI | 4 | 4 | MANTENER |
| ivsd | Septum diastólico (IVSd) | 2 | 2 | MANTENER |
| pwtd | Pared posterior (PWTd) | 2 | 2 | MANTENER |
| rwt_meas | Grosor relativo de pared (RWT) | 3 | 3 | MANTENER |
| geometria_vi_meas | Geometría del VI | 3 | 3 | MANTENER |
| masa_vi_meas | Masa del VI | 4 | 4 | MANTENER |
| lv_mass_index | Índice de masa del VI | 4 | 4 | MANTENER |
| vti_tsvi_meas | VTI del TSVI | 2 | 2 | MANTENER |
| plr_vti_change | Cambio de VTI tras elevación pasiva de piernas | 2 | 2 | MANTENER |
| area_tsvi_meas | Área del TSVI | 3 | 3 | MANTENER |
| volumen_sistolico_meas | Volumen sistólico | 3 | 3 | MANTENER |
| sv_index | Índice de volumen sistólico | 3 | 3 | MANTENER |
| gasto_cardiaco_meas | Gasto cardiaco | 3 | 3 | MANTENER |
| cardiac_index | Índice cardiaco | 3 | 3 | MANTENER |
| rvs_meas | RVS | 4 | 4 | MANTENER |
| irvs_meas | IRVS | 4 | 4 | MANTENER |
| diametro_ap_ai | Diámetro anteroposterior de AI | 2 | 2 | MANTENER |
| volumen_ai_meas | Volumen de AI | 3 | 3 | MANTENER |
| lavi_meas | LAVI | 3 | 3 | MANTENER |
| dilatacion_ai_class | Dilatación de AI | 3 | 3 | MANTENER |
| la_strain_reservoir | Strain reservorio de AI | 4 | 4 | MANTENER |
| onda_e_mitral | Onda E mitral | 2 | 2 | MANTENER |
| onda_a_mitral | Onda A mitral | 2 | 2 | MANTENER |
| relacion_e_a | Relación E/A | 2 | 2 | MANTENER |
| e_septal_meas | e' septal | 2 | 2 | MANTENER |
| e_lateral_meas | e' lateral | 2 | 2 | MANTENER |
| relacion_e_e_promedio | E/e' promedio | 2 | 2 | MANTENER |
| tiempo_desaceleracion_e | Tiempo de desaceleración de E | 3 | 3 | MANTENER |
| ivrt_meas | IVRT | 3 | 3 | MANTENER |
| velocidad_it_diastology | Velocidad máxima de IT | 3 | 3 | MANTENER |
| lavi_diastology | LAVI en diastología | 3 | 3 | MANTENER |
| la_strain_diastology | Strain reservorio de AI en diastología | 4 | 4 | MANTENER |
| relacion_vd_vi | Relación VD/VI | 1 | 1 | MANTENER |
| diametro_basal_vd | Diámetro basal del VD | 2 | 2 | MANTENER |
| diametro_medio_vd | Diámetro medio del VD | 2 | 2 | MANTENER |
| rv_length | Longitud del VD | 2 | 2 | MANTENER |
| tapse_meas | TAPSE | 2 | 2 | MANTENER |
| s_prima_vd | s' del VD | 2 | 2 | MANTENER |
| paat_tsvd | PAAT / AccT del TSVD | 2 | 3 | CAMBIAR |
| grosor_pared_vd | Grosor de pared libre del VD | 3 | 3 | MANTENER |
| fac_vd_meas | FAC del VD | 3 | 3 | MANTENER |
| vti_tsvd_meas | VTI del TSVD | 3 | 3 | MANTENER |
| tapse_pasp_ratio | TAPSE/PASP | 3 | 3 | MANTENER |
| fevd_3d | FEVD 3D | 4 | 4 | MANTENER |
| strain_rv | Strain de pared libre del VD | 4 | 4 | MANTENER |
| indice_tei_vd | Índice de Tei del VD | 4 | 4 | MANTENER |
| diametro_vci_meas | Diámetro de VCI | 1 | 1 | MANTENER |
| colapsabilidad_vci_meas | Colapsabilidad de VCI | 1 | 1 | MANTENER |
| area_ad_meas | Área de AD | 2 | 2 | MANTENER |
| distensibilidad_vci_meas | Distensibilidad de VCI | 2 | 3 | CAMBIAR |
| presion_ad_estimada_meas | Presión AD estimada | 2 | 2 | MANTENER |
| longitud_ad | Longitud de AD | 3 | 3 | MANTENER |
| diametro_menor_ad | Diámetro menor de AD | 3 | 3 | MANTENER |
| gradiente_vd_ad | Gradiente VD-AD | 2 | 2 | MANTENER |
| pasp_meas | PSVD / PASP | 2 | 2 | MANTENER |
| aplanamiento_septal_meas | Aplanamiento septal | 2 | 2 | MANTENER |
| presion_media_pulmonar | Presión media pulmonar por PR | 3 | 3 | MANTENER |
| presion_diastolica_pulmonar | Presión diastólica pulmonar | 3 | 3 | MANTENER |
| indice_excentricidad_vi | Índice de excentricidad del VI | 3 | 3 | MANTENER |
| rvp_ecografica | RVP ecográfica | 4 | 4 | MANTENER |
| velocidad_max_aortica | Velocidad máxima aórtica | 2 | 2 | MANTENER |
| gradiente_max_aortico | Gradiente máximo aórtico | 2 | 2 | MANTENER |
| gradiente_medio_aortico | Gradiente medio aórtico | 2 | 2 | MANTENER |
| ava_meas | Área valvular aórtica (AVA) | 3 | 3 | MANTENER |
| ava_indexed | AVA indexada | 3 | 3 | MANTENER |
| dvi_meas | Índice adimensional (DVI) | 3 | 3 | MANTENER |
| velocidad_tsvi | Velocidad del TSVI | 3 | 3 | MANTENER |
| gradiente_medio_mitral | Gradiente medio mitral | 2 | 3 | CAMBIAR |
| area_mitral_pht | Área mitral por PHT | 3 | 3 | MANTENER |
| pht_meas | PHT | 3 | 3 | MANTENER |
| area_mitral_planimetria | Área valvular mitral por planimetría | 4 | 4 | MANTENER |
| relacion_vti_mitral_tsvi | Relación VTI mitral/VTI TSVI | 4 | 4 | MANTENER |
| vena_contracta_meas | Vena contracta (VC) | 2 | 3 | CAMBIAR |
| insuficiencia_mitral_severa_meas | Insuficiencia mitral severa | 2 | 3 | CAMBIAR |
| insuficiencia_aortica_severa_meas | Insuficiencia aórtica severa | 2 | 3 | CAMBIAR |
| insuficiencia_tricuspidea_severa_meas | Insuficiencia tricuspídea severa | 2 | 3 | CAMBIAR |
| flujo_pisa_meas | Flujo PISA | 4 | 4 | MANTENER |
| eroa_meas | EROA | 4 | 4 | MANTENER |
| volumen_regurgitante_meas | Volumen regurgitante | 4 | 4 | MANTENER |
| fraccion_regurgitante_meas | Fracción regurgitante | 4 | 4 | MANTENER |
| derrame_pericardico_pequeno | Derrame pericárdico pequeño | 2 | 2 | MANTENER |
| derrame_pericardico_moderado | Derrame pericárdico moderado | 2 | 2 | MANTENER |
| derrame_pericardico_grande | Derrame pericárdico grande | 2 | 2 | MANTENER |
| colapso_ad_meas | Colapso de AD | 2 | 2 | MANTENER |
| colapso_vd_meas | Colapso de VD | 2 | 2 | MANTENER |
| variacion_mitral_respiratoria | Variación mitral respiratoria | 2 | 3 | CAMBIAR |
| variacion_tricuspidea_respiratoria | Variación tricuspídea respiratoria | 2 | 3 | CAMBIAR |
| vci_pletorica_meas | VCI pletórica | 2 | 2 | MANTENER |
| movimiento_pendular_meas | Movimiento pendular del corazón | 3 | 3 | MANTENER |