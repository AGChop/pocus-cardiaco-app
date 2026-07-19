# Reporte de Extracción de Datos Médicos

**Proyecto:** POCUS Cardíaco - Glosario y banco de mediciones  
**Fecha:** 19 de julio de 2026  
**Documento Fuente:** `docs/Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf`  
**Destino de Extracción:** `docs/extracted_pdf_text.txt`  

---

## 1. Resumen de la Extracción
El documento de referencia clínica consta de **18 páginas** y se ha extraído exitosamente su texto estructurado usando la herramienta `pypdf` a través de un script en Python.

- **Total de páginas procesadas:** 18
- **Estado de la extracción:** Completa y sin pérdida de caracteres especiales (por ejemplo: `≤`, `≥`, `π`, `²`, `⁻⁵`, `e'`, `s'`).
- **Integridad de datos:** Verificada manualmente página por página contra el PDF original.

---

## 2. Estructura de Secciones Detectada
El documento se divide de manera clara en las siguientes secciones (página 2 del PDF):

| # | Título de la Sección / Contenido | Páginas de Origen |
|---|----------------------------------|-------------------|
| 1 | Ventrículo izquierdo: dimensiones y función sistólica | Página 4 |
| 2 | Grosor, masa y geometría del VI | Página 4 |
| 3 | Volumen sistólico, Gasto cardiaco y Flujo del TSVI | Página 5 |
| 4 | Aurícula izquierda | Página 5 |
| 5 | Función diastólica del VI | Página 6 |
| 6 | Ventrículo derecho: tamaño y función sistólica | Página 7 |
| 7 | Aurícula derecha, VCI y presión AD | Página 7 |
| 8 | Presión pulmonar y hemodinámica derecha | Página 8 |
| 9 | Válvula aórtica y TSVI | Página 9 |
| 10| Válvula mitral | Página 9 |
| 11| Insuficiencias valvulares | Página 10 |
| 12| Pericardio y taponamiento | Página 10 |
| 13| Clasificaciones prácticas | Página 11 |
| 14| Conjunto mínimo para el operador POCUS | Página 11 |
| 15| Lista de abreviaturas | Página 12 |
| 16| Glosario clínico de parámetros | Páginas 13-17 |
| 17| Referencias principales | Página 18 |

---

## 3. Inventario Clínico Inicial
Se identificaron los siguientes elementos esenciales que formarán parte de nuestra base de datos JSON:

### A. Mediciones Clave (Secciones 1 a 12)
- **Ventrículo Izquierdo (VI):** DTDVI, DTSVI, VTDVI, VTDVI indexado, VTSVI, VTSVI indexado, FEVI, Fracción de acortamiento, EPSS, MAPSE, s' mitral, GLS, WMSI (Pág. 4).
- **Grosor y Geometría:** IVSd, PWTd, RWT, Masa VI, Índice de masa VI, Geometría del VI (Pág. 4).
- **Flujos y Gasto:** Área del TSVI, VTI del TSVI, Volumen sistólico, Índice de volumen sistólico, Gasto cardiaco, Índice cardiaco, Cambio de VTI tras elevación pasiva de piernas, RVS, IRVS (Pág. 5).
- **Aurícula Izquierda (AI):** Diámetro AP, Volumen, LAVI, Dilatación AI, Strain reservorio (Pág. 5).
- **Diastología:** Onda E, Onda A, Relación E/A, Tiempo de desaceleración de E, IVRT, e' septal, e' lateral, E/e' promedio, Velocidad máx de IT, LAVI, Strain reservorio (Pág. 6).
- **Ventrículo Derecho (VD):** Diámetro basal, Diámetro medio, Longitud, Relación VD/VI, Grosor de pared libre, TAPSE, s' del VD, FAC, FEVD 3D, Strain de pared libre, Índice de Tei, VTI del TSVD, PAAT/AccT, TAPSE/PASP (Pág. 7).
- **Aurícula Derecha y VCI:** Área AD, Longitud AD, Diámetro menor AD, Diámetro VCI, Colapsabilidad VCI, Distensibilidad VCI, Presión AD estimada (Pág. 7).
- **Presión Pulmonar:** Gradiente VD-AD, PSVD/PASP, Presión media pulmonar por PR, Presión diastólica pulmonar, RVP ecográfica, Índice de excentricidad del VI, Aplanamiento septal (Pág. 8).
- **Válvula Aórtica / TSVI:** Velocidad máx, Gradiente máx, Gradiente medio, AVA, AVA indexada, Índice adimensional (DVI), Velocidad del TSVI (Pág. 9).
- **Válvula Mitral:** Área mitral por planimetría, Área mitral por PHT, Gradiente medio mitral, PHT, Relación VTI mitral/VTI TSVI (Pág. 9).
- **Insuficiencias Valvulares:** Vena contracta, Flujo PISA, EROA, Volumen regurgitante, Fracción regurgitante, IM severa, IA severa, IT severa (Pág. 10).
- **Pericardio y Taponamiento:** Derrame pequeño, moderado y grande, Colapso AD, Colapso VD, Variación mitral respiratoria, Variación tricuspídea respiratoria, VCI pletórica, Movimiento pendular (Pág. 10).

---

## 4. Notas Clínicas y Advertencias de Seguridad Integradas
Se han recopilado las advertencias de seguridad clínica y las notas de la página 3, confirmando su coincidencia exacta con el texto de origen para mostrarlas permanentemente.
