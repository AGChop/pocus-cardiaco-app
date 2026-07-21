# Metodología de Prioridad Clínica de Visualización de Mediciones

## 1. Objetivo
El objetivo de este documento es definir y estructurar los criterios para el orden de visualización de las mediciones ecocardiográficas dentro de la aplicación **POCUS Cardíaco**. Se busca facilitar al personal clínico de primera línea el acceso rápido a los parámetros más relevantes durante evaluaciones críticas.

## 2. Alcance
Esta metodología se aplica exclusivamente al banco de mediciones del aplicativo, clasificando y ordenando las 101 mediciones clínicas registradas en el sistema.

## 3. Población Adulta
El alcance clínico de los parámetros está delimitado de forma estricta a la **población adulta**. Las escalas, valores de referencia y prioridades definidos no deben aplicarse a pacientes pediátricos.

## 4. Ámbitos Clínicos Incluidos
La priorización está pensada para dar soporte en entornos de alta demanda y decisiones inmediatas:
*   Medicina Interna (hospitalización y consulta).
*   Urgencias / Emergencias.
*   Unidad de Cuidado Intensivo (UCI).
*   Evaluaciones rápidas en escenarios de shock, disnea aguda o inestabilidad hemodinámica (Evaluación Cardíaca Focalizada - FoCUS).

## 5. Diferencia entre Frecuencia y Prioridad Clínica
Es fundamental diferenciar la *frecuencia de uso real* de la *prioridad clínica de visualización*:
*   **Frecuencia:** Representa cuántas veces se realiza físicamente una medición en la práctica diaria a nivel mundial. Por tanto, clasificar un parámetro en Nivel 1 **no significa que tenga una "frecuencia mundial demostrada" de uso**, sino que su visualización es prioritaria en escenarios críticos.
*   **Prioridad clínica de visualización:** Es el orden lógico y razonado en el que se presentan las variables al usuario en la interfaz para optimizar la toma de decisiones básicas. Primero se muestran los parámetros del núcleo básico que responden a preguntas de vida o muerte (p. ej., colapso de cavidades o volumen de derrame), seguidos de parámetros cuantitativos complementarios (Doppler tisular, volumetrías), y finalmente los estudios avanzados o de ecocardiografía integral.

## 6. Descripción de los Cuatro Niveles

### Nivel 1 — Núcleo POCUS (basic)
Mediciones o evaluaciones fundamentalmente cualitativas o semicuantitativas que responden a preguntas diagnósticas inmediatas y binarias de extrema gravedad.
*   **Ejemplos:** Presencia de dilatación del VD (relación VD/VI > 1.0), diámetro y colapso inspiratorio de la VCI en respiración espontánea.

### Nivel 2 — POCUS Extendido (extended)
Mediciones cuantitativas específicas que aportan precisión y mayor sensibilidad al estudio pero requieren técnica Doppler (pulsado, continuo o tisular) y una correcta alineación del haz de ultrasonido.
*   **Ejemplos:** Mediciones como FEVI cuantitativa (Simpson biplano), TAPSE, velocidad tisular s' del VD, EPSS, estimación de presiones pulmonares (PASP), velocidades transmitrales de llenado (E, A) y la relación E/e' promedio.

### Nivel 3 — Dependiente del Contexto (contextual)
Mediciones y valoraciones que aportan información diagnóstica valiosa en escenarios específicos (p. ej., estenosis aórtica o mitral sospechada, caracterización del grosor de la pared del VD en hipertensión pulmonar crónica, o volumetría de la AI para evaluar cronicidad diastólica), pero que no son de carácter urgente.

### Nivel 4 — Avanzado o Ecocardiografía Integral (advanced)
Parámetros que requieren un alto nivel de entrenamiento, trazados complejos en múltiples planos, cálculos de software específicos (como speckle tracking) o ecocardiografía 3D.
*   **Ejemplos:** Strain longitudinal global (GLS), fracción de eyección del VD en 3D, resistencias vasculares sistémicas calculadas (RVS) y el área del orificio regurgitante efectivo (EROA) mediante PISA.

## 7. Criterios de Clasificación
Para ubicar cada parámetro en un nivel específico, se evaluaron individualmente los siguientes criterios:
1.  Presencia en currículos básicos de FoCUS.
2.  Utilidad para responder una pregunta clínica inmediata (p. ej., taponamiento, disfunción VI grave).
3.  Aplicabilidad en shock y parada.
4.  Aplicabilidad en disnea aguda.
5.  Aplicabilidad en inestabilidad hemodinámica.
6.  Rapidez y simplicidad de adquisición.
7.  Reproducibilidad del parámetro.
8.  Dependencia de la calidad de la ventana ecográfica.
9.  Sensibilidad a la alineación del haz de ultrasonido (dependencia del del ángulo).
10. Necesidad de Doppler (color, pulsado, continuo o tisular).
11. Requerimiento de cálculos matemáticos derivados.
12. Necesidad de software propietario o especializado.
13. Nivel de entrenamiento requerido por el operador.
14. Ámbito de aplicación (general vs. contextual de patología).
15. Riesgo de interpretación aislada incorrecta.
16. Necesidad de integrar múltiples parámetros antes de concluir.

## 8. Método Utilizado para Ordenar dentro de cada Sección
El ordenamiento se realiza de forma jerárquica y consecutiva dentro de cada una de las 12 secciones clínicas originales (se descarta el agrupamiento por ventanas acústicas):
1.  **Evaluación cualitativa fundamental:** Métodos de inspección visual rápida.
2.  **Medición básica o semicuantitativa:** Mediciones de adquisición directa.
3.  **Medición cuantitativa extendida:** Estudios Doppler o con técnicas específicas.
4.  **Hallazgos contextuales:** Parámetros secundarios.
5.  **Cálculos o técnicas avanzadas:** Derivados y fórmulas complejas.
6.  El índice `display_order` se inicializa en 1 al inicio de cada sección clínica real de la base de datos (`data/sections.json`) y se incrementa secuencialmente de 1 en 1 sin vacíos ni duplicados.
7.  Una medición puede conservar el primer lugar (`display_order: 1`) dentro de su sección clínica aunque sea clasificada en el Nivel 2, si es la medición de mayor prioridad disponible en esa sección (por ejemplo, la FEVI en la sección del ventrículo izquierdo).

## 9. precisiones de Criterio Clínico Aplicadas

### Ventrículo Izquierdo
*   **FEVI:** Clasificada en el **Nivel 2 (POCUS extendido)** debido a que la entrada original representa el cálculo formal cuantitativo mediante la regla de Simpson biplano (basada en volúmenes telediastólico y telesistólico medidos en vistas A4C y A2C, requiriendo contorno endocárdico preciso y evitar acortamiento apical). Esto supera técnicamente la simple estimación visual cualitativa rápida ('eyeballing') contemplada en FoCUS.
*   **EPSS:** Clasificado en el **Nivel 2 (POCUS extendido)**. Funciona como un sustituto indirecto de la FEVI y no debe anteponerse a la valoración visual global del VI. Su exactitud puede alterarse ante valvulopatías mitrales o asincronías.

### Ventrículo Derecho e Hipertensión Pulmonar
*   **Relación VD/VI:** Clasificada en el **Nivel 1 (Núcleo POCUS)** como herramienta de descarte rápido de dilatación aguda/severa del VD en el paciente con inestabilidad hemodinámica severa. Se documenta que no diagnostica por sí sola una etiología específica (como TEP) y requiere valoración clínica.
*   **TAPSE:** Clasificado en el **Nivel 2 (POCUS extendido)** al tratarse de una medición lineal cuantitativa. Su uso no debe sustituir la valoración cualitativa e integrada del tamaño y función global del VD.

### Vena Cava Inferior y Presión Auricular
*   **Diámetro y colapso de la VCI:** Clasificados en el **Nivel 1 (Núcleo POCUS)** para ventilación espontánea.
*   **Presión AD estimada:** Clasificada en el **Nivel 2 (POCUS extendido)** al requerir la extrapolación mediante rangos y mediciones.
*   **VCI pletórica:** Clasificada en el **Nivel 2** como un hallazgo de sospecha activa de taponamiento.
*   *Nota metodológica:* Se indica explícitamente que la VCI no constituye por sí sola una medición directa de la volemia ni de la respuesta a fluidos y debe evaluarse en conjunto con la ventilación y la función del VD.

### Derrame Pericárdico y Taponamiento
*   **Presencia o ausencia de derrame (estimación visual):** Clasificada en el **Nivel 1**.
*   **Categorías de tamaño (pequeño/moderado/grande) y colapsos de AD/VD:** Clasificados en el **Nivel 2 (POCUS extendido)** al requerir mediciones exactas y correlación temporal fina (sístole/diástole).
*   **Movimiento pendular:** Clasificado en el **Nivel 3 (Dependiente del contexto)**.
*   *Nota metodológica:* Se documenta explícitamente que los signos ecográficos de repercusión hemodinámica deben integrarse entre sí y con el contexto clínico; ninguno debe presentarse de manera aislada como diagnóstico definitivo de taponamiento pericárdico.

## 10. Fuentes Científicas Completas
La priorización y el marco metodológico se fundamentan exclusivamente en las siguientes recomendaciones oficiales y guías de consenso vigentes (verificadas):

1.  **Spencer KT, Kimura BJ, Korcarz CE, et al.** *Focused Cardiac Ultrasound: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2013;26(6):567-581. DOI: [10.1016/j.echo.2013.04.001](https://doi.org/10.1016/j.echo.2013.04.001).
2.  **Via G, Hussain A, Wells M, et al.** *International Evidence-Based Recommendations for Focused Cardiac Ultrasound (FoCUS).* Journal of the American Society of Echocardiography. 2014;27(7):683.e1-683.e33. DOI: [10.1016/j.echo.2014.05.001](https://doi.org/10.1016/j.echo.2014.05.001).
3.  **Lang RM, Badano LP, Mor-Avi V, et al.** *Recommendations for Chamber Quantification: Guidelines from the American Society of Echocardiography and the European Association of Cardiovascular Imaging.* Journal of the American Society of Echocardiography. 2015;28(1):1-39.e14. DOI: [10.1016/j.echo.2014.10.003](https://doi.org/10.1016/j.echo.2014.10.003).
4.  **Mukherjee M, Rudski LG, et al.** *Guidelines for the Echocardiographic Assessment of the Right Heart in Adults and Special Considerations in Pulmonary Hypertension: Recommendations from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2025;38(3):141-186. DOI: [10.1016/j.echo.2025.01.006](https://doi.org/10.1016/j.echo.2025.01.006). (Guía vigente principal).
5.  **Rudski LG, Lai WW, Afilalo J, et al.** *Guidelines for the Echocardiographic Assessment of the Right Heart in Adults: A Report from the American Society of Echocardiography.* Journal of the American Society of Echocardiography. 2010;23(7):685-713. DOI: [10.1016/j.echo.2010.05.010](https://doi.org/10.1016/j.echo.2010.05.010). (Antecedente histórico).
6.  **Nagueh SF, Smiseth OA, Appleton CP, et al.** *Recommendations for the Evaluation of Left Ventricular Diastolic Function by Echocardiography: An Update from the American Society of Echocardiography and the European Association of Cardiovascular Imaging.* Journal of the American Society of Echocardiography. 2016;29(4):277-314. DOI: [10.1016/j.echo.2016.01.011](https://doi.org/10.1016/j.echo.2016.01.011).
7.  **Adler Y, Charron P, Imazio M, et al.** *Echocardiographic assessment of pericardial effusion and cardiac tamponade.* European Heart Journal. 2015;36(42):2921–2964. DOI: [10.1093/eurheartj/ehv317](https://doi.org/10.1093/eurheartj/ehv317).

## 11. Limitaciones
*   La priorización representa una síntesis de consenso diseñada para agilizar la lectura, no una regla rígida de exclusión de parámetros.
*   En pacientes con mala ventana acústica, parámetros teóricamente prioritarios pueden requerir el uso de métodos alternativos del Nivel 2 o 3.
*   La clasificación y priorización de las mediciones no sustituye de ninguna manera la formación académica formal ni la evaluación ecocardiográfica integral del paciente en el punto de atención (POCUS).
*   Todas las mediciones deben interpretarse de manera obligatoria dentro de su contexto clínico e integradas con el resto de parámetros fisiológicos y ecocardiográficos del paciente.

## 12. Riesgo de Subjetividad
La categorización está alineada con currículos internacionales establecidos (como el syllabus de FoCUS de la EACVI). No obstante, la asignación interna fina entre parámetros del mismo nivel conserva un margen de criterio operativo que debe ser revisado y adaptado localmente.

## 13. Necesidad de Revisión Médica
Este documento y el borrador de prioridades adjunto (`measurement-priority.draft.json`) constituyen una propuesta técnica sujeta a revisión, debate y aprobación por el comité médico o el especialista responsable del protocolo clínico antes de su paso a producción.

## 14. Procedimiento para Aprobar o Modificar una Clasificación
1.  **Revisión:** El comité médico evalúa el borrador de prioridades.
2.  **Modificación:** Cualquier cambio consensuado en un parámetro o nivel se edita en la estructura del borrador.
3.  **Aprobación:** Una vez aprobado, el borrador se convierte en el archivo oficial `measurement-priority.json` para controlar el orden en la interfaz.

## 15. Fecha de Revisión
*   **Última revisión metodológica:** 20 de Julio de 2026.

## 16. Estado del Documento
*   **Estado:** Borrador de propuesta (Draft-2).
*   **Fase:** Fase 3A (Auditoría Científica).

## 17. Advertencia de Control de Interfaz
> [!WARNING]
> Este documento y el archivo `measurement-priority.draft.json` representan una propuesta organizativa independiente. **Actualmente no controlan ni modifican el orden de visualización de los parámetros en la interfaz de la aplicación.** El orden visible del Banco de Mediciones permanece intacto y fiel a la secuencia original en `data/measurements.json` hasta la aprobación final de la Fase 3B.
