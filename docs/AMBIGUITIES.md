# Registro de Ambigüedades y Decisiones Clínicas

**Proyecto:** POCUS Cardíaco - Glosario y banco de mediciones
**Fecha:** 19 de julio de 2026
**Última actualización:** 23 de agosto de 2026

Este documento registra los puntos dudosos o con solapamiento identificados en el PDF de referencia clínica, la decisión adoptada para la aplicación y la fundamentación correspondiente.

---

## 1. Rango de FEVI Normal vs. Hiperdinámica [RESOLVIDO]
* **Dato dudoso:** Rango normal de FEVI (53-73%) frente a FEVI Hiperdinámica (>70-75%).
* **Página del PDF:** Página 4 (Tabla VI) y Página 11 (Sección 13: Clasificaciones).
* **Motivo de la duda:** Existe una zona de superposición entre el límite superior normal (73%) y el inicio del rango hiperdinámico (>70-75%).
* **Decisión de diseño educativo y clínico:**
  * Se definieron los intervalos de referencia de sístole del VI basándose en el método de Simpson biplano (hombres 52–72%; mujeres 54–74%).
  * Se incorporó una nota aclaratoria explícita: superar el límite superior de referencia no establece por sí solo un estado hiperdinámico y debe interpretarse en relación con la calidad de imagen, método y contexto hemodinámico del paciente.
  * No se implementó ninguna lógica de clasificación diagnóstica automática para la hiperdinamia.
* **Fundamento científico & Referencias:** Lang RM, et al. *Recommendations for Chamber Quantification* (ASE/EACVI 2015).
* **Revisor clínico y fecha:** AGChop (23 de agosto de 2026).
* **Aclaración expresa:** Esta revisión corresponde a la gobernanza clínica interna del proyecto y no constituye aprobación institucional de la CCSS.

---

## 2. Rango Gris en GLS (Strain Longitudinal Global) [RESOLVIDO]
* **Dato dudoso:** GLS normal de -18% a -22%, y "menos negativo que -16%" como anormal.
* **Página del PDF:** Página 4 (Sección 1: GLS del VI).
* **Motivo de la duda:** ¿Qué ocurre con un valor de -17%? Queda en una "zona gris" no explícitamente cubierta por las dos reglas.
* **Decisión de diseño educativo y clínico:**
  * Se clarificaron los intervalos: normal cuando es más negativo que −18% (p. ej. −19%), limítrofe/borderline entre −16% y −18% (p. ej. −17%), y anormal cuando es menos negativo que −16% (p. ej. −15%).
  * Se añadió una advertencia educativa sobre la variabilidad de software y fabricante, recomendando el uso de la misma plataforma para seguimientos longitudinales.
* **Fundamento científico & Referencias:** Thomas JD, et al. *Clinical Applications of Strain Echocardiography: A Clinical Consensus Statement from the ASE and EACVI* (JASE 2025). DOI: 10.1016/j.echo.2025.07.007.
* **Revisor clínico y fecha:** AGChop (23 de agosto de 2026).
* **Aclaración expresa:** Esta revisión corresponde a la gobernanza clínica interna del proyecto y no constituye aprobación institucional de la CCSS.

---

## 3. Límite Inferior de FEVI en Hombres y Mujeres [RESOLVIDO]
* **Dato dudoso:** FEVI normal 53-73%, pero "límite inferior: hombres 52%, mujeres 54%".
* **Página del PDF:** Página 4 (Sección 1: FEVI).
* **Motivo de la duda:** El rango general es 53-73%, pero el límite inferior varía 1% por sexo.
* **Decisión de diseño educativo y clínico:**
  * Se actualizaron los campos bilingües de la medición `fevi` para reflejar los límites específicos del Simpson biplano por sexo (hombres 52–72%; mujeres 54–74%), eliminando la simplificación previa y conservando la población de referencia adulta.
* **Fundamento científico & Referencias:** Lang RM, et al. *Recommendations for Chamber Quantification* (ASE/EACVI 2015).
* **Revisor clínico y fecha:** AGChop (23 de agosto de 2026).
* **Aclaración expresa:** Esta revisión corresponde a la gobernanza clínica interna del proyecto y no constituye aprobación institucional de la CCSS.

---

## 4. Clasificación Gradual de la Disfunción Diastólica [RESOLVIDO]
* **Dato dudoso:** El documento no incluye un diagrama de flujo o algoritmo rígido para los grados I, II y III de disfunción diastólica.
* **Página del PDF:** Página 6 (Sección 5: Función diastólica).
* **Motivo de la duda:** Los clínicos noveles suelen buscar clasificaciones rápidas de grados de disfunción diastólica.
* **Decisión de diseño educativo y clínico:**
  * Se ratificó el enfoque puramente consultivo. La aplicación no automatiza clasificaciones de grados ni estimaciones de presión de llenado a partir de variables aisladas.
  * Se incorporó una limitación multiparamétrica común bilingüe a todos los 11 parámetros diastólicos, advirtiendo que ninguna variable aislada diagnostica o gradúa la disfunción diastólica ni estima presiones de llenado por sí sola, requiriendo un abordaje multiparamétrico.
* **Fundamento científico & Referencias:** Nagueh SF, et al. *Recommendations for the Evaluation of Left Ventricular Diastolic Function* (ASE Task Force 2025).
* **Revisor clínico y fecha:** AGChop (23 de agosto de 2026).
* **Aclaración expresa:** Esta revisión corresponde a la gobernanza clínica interna del proyecto y no constituye aprobación institucional de la CCSS.
