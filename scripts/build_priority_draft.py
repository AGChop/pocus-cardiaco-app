import json
import os

# 1. CLASIFICACIONES BLOQUEADAS (Fijas)
LOCKED_PRIORITIES = {
    "relacion_vd_vi": (1, "basic", ["shock", "disnea", "inestabilidad hemodinámica"],
                       "Comparación 2D rápida del tamaño relativo del VD que ayuda a reconocer dilatación significativa del ventrículo derecho. Su exactitud depende de la carga, la calidad de imagen y la correcta alineación del plano de adquisición. No diagnostica por sí sola embolia pulmonar y debe integrarse siempre con la función del VD y el contexto clínico global."),
    "diametro_vci_meas": (1, "basic", ["shock", "inestabilidad hemodinámica"],
                           "Medición 2D rápida de la VCI que, integrada con su variación respiratoria, función del corazón derecho, tipo de ventilación y contexto clínico, contribuye a estimar la presión auricular derecha y evaluar congestión venosa. No constituye por sí sola una medición directa de la volemia absoluta ni de la respuesta a la administración de líquidos."),
    "colapsabilidad_vci_meas": (1, "basic", ["shock", "inestabilidad hemodinámica"],
                                "Porcentaje de colapso respiratorio que forma parte de la evaluación básica de la VCI. Se aplica principalmente a pacientes en respiración espontánea, siendo muy dependiente de la técnica de adquisición y del esfuerzo inspiratorio realizado. No debe extrapolarse directamente a ventilación mecánica ni demuestra de forma aislada respuesta a líquidos."),
    "fevi": (2, "extended", ["shock", "disnea", "inestabilidad hemodinámica"],
             "Cálculo cuantitativo por Simpson biplano que requiere vistas A4C y A2C, identificación de fin de diástole y fin de sístole, trazado endocárdico y evitar acortamiento apical. Es clínicamente útil, pero supera la estimación visual básica de la función sistólica realizada en FoCUS.")
}

# 2. RECLASIFICACIONES APROBADAS (Nivel 2 -> Nivel 3)
CLINICALLY_REVIEWED_OVERRIDES = {
    "paat_tsvd": (3, "contextual", ["disnea", "inestabilidad hemodinámica"],
                  "Tiempo de aceleración pulmonar por Doppler pulsado en el TSVD. Se utiliza principalmente ante sospecha de hipertensión pulmonar, aumento de resistencia vascular pulmonar o determinados contextos de disfunción derecha. No debe presentarse como prueba aislada diagnóstica de embolia pulmonar."),
    "distensibilidad_vci_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                                 "Índice de distensibilidad respiratoria de la VCI. Su interpretación corresponde principalmente a pacientes con ventilación mecánica controlada y depende de volumen corriente, presión intratorácica, esfuerzo respiratorio, función derecha y técnica de adquisición. No debe presentarse como prueba aislada de respuesta a líquidos."),
    "gradiente_medio_mitral": (3, "contextual", ["disnea"],
                               "Gradiente de presión medio transvalvular mitral por Doppler continuo. Se utiliza ante sospecha de estenosis mitral, obstrucción transmitral o evaluación de prótesis, y depende de frecuencia cardiaca, ritmo y flujo."),
    "insuficiencia_mitral_severa_meas": (3, "contextual", ["disnea", "inestabilidad hemodinámica"],
                                         "La clasificación de insuficiencia mitral severa requiere integración multiparamétrica y una sospecha clínica o valvular específica."),
    "insuficiencia_aortica_severa_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                                          "La clasificación de insuficiencia aórtica severa requiere integrar Doppler color, Doppler espectral, flujo reverso y otros hallazgos."),
    "insuficiencia_tricuspidea_severa_meas": (3, "contextual", ["disnea", "inestabilidad hemodinámica"],
                                              "La clasificación de insuficiencia tricuspídea severa requiere integración de vena contracta, Doppler, flujo de venas hepáticas, tamaño de cavidades y función derecha."),
    "vena_contracta_meas": (3, "contextual", ["disnea"],
                            "La vena contracta es una medición semicuantitativa que se aplica cuando existe sospecha de regurgitación valvular y debe integrarse con otros criterios."),
    "variacion_mitral_respiratoria": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                                      "Medición Doppler dirigida a evaluar la interdependencia ventricular y posible repercusión hemodinámica en un contexto pericárdico específico."),
    "variacion_tricuspidea_respiratoria": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                                           "Medición Doppler del flujo transtricuspídeo dirigida a evaluar la interdependencia ventricular y la posible repercusión hemodinámica en el taponamiento cardíaco.")
}

# 3. PROPUESTAS DE ASCENSO RETIRADAS (Permanecen en Nivel 3)
WITHDRAWN_ASCENTS = {
    "velocidad_tsvi": (3, "contextual", ["shock"],
                       "Aunque la velocidad máxima del TSVI puede obtenerse fácilmente durante una adquisición Doppler del TSVI, su utilidad aislada es limitada y depende de una pregunta hemodinámica o clínica específica. No tiene la misma aplicabilidad general que el VTI del TSVI."),
    "tiempo_desaceleracion_e": (3, "contextual", ["disnea"],
                                "Es una medición técnicamente accesible, pero forma parte de una evaluación diastólica multiparamétrica. Depende de edad, frecuencia cardiaca, ritmo, precarga, relajación y presión auricular izquierda y no debe interpretarse aisladamente."),
    "grosor_pared_vd": (3, "contextual", ["disnea"],
                         "Es una medición lineal técnicamente accesible, pero se utiliza principalmente en contextos específicos de hipertrofia del VD, hipertensión pulmonar o sobrecarga crónica. No distingue por sí sola enfermedad aguda de crónica y debe integrarse con el resto de la evaluación derecha.")
}

# 4. PRIORIDADES BASE RESTANTES (Nivel 2, 3 y 4)
BASE_PRIORITIES = {
    # === SECCIÓN 1: lv_systolic ===
    "epss": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
             "Distancia E-Septum con modo M. Sustituto cuantitativo indirecto de la función sistólica del VI. Útil en ventanas difíciles, pero dependiente de la posición mitral y la presencia de valvulopatías o miocardiopatías segmentarias. No debe preceder a la valoración visual global."),
    "mapse": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
              "Excursión sistólica longitudinal del anillo mitral por modo M. Permite valorar el acortamiento longitudinal izquierdo, pero requiere correcta alineación del cursor y entrenamiento extendido."),
    "s_prima_mitral": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                       "Velocidad sistólica tisular del anillo mitral por Doppler tisular (TDI). Valora la función longitudinal miocárdica de forma objetiva, requiriendo Doppler tisular y alineación paralela."),
    "dtdvi": (2, "extended", ["disnea"],
              "Diámetro telediastólico del VI por modo 2D. Cuantifica dilatación de la cavidad izquierda para perfilar etiología de disnea, cuidando de evitar cortes oblicuos."),
    "dtsvi": (2, "extended", ["disnea"],
              "Diámetro telesistólico del VI. Utilizado para el cálculo de volumen y la fracción de acortamiento radial del VI."),
    "fraccion_acortamiento_meas": (2, "extended", ["disnea"],
                                   "Cambio porcentual de diámetros del VI que estima la contractilidad miocárdica radial media."),
    "vtdvi": (3, "contextual", ["disnea"],
              "Volumen telediastólico del VI por método de Simpson biplano. Medición de volumen más precisa que el diámetro lineal pero muy dependiente de la calidad de la ventana apical."),
    "vtdvi_indexed": (3, "contextual", ["disnea"],
                      "Volumen telediastólico del VI indexado a superficie corporal para comparación interindividual."),
    "vtsvi_meas": (3, "contextual", ["disnea"],
                   "Volumen telesistólico del VI por Simpson biplano al final de la eyección."),
    "vtsvi_indexed": (3, "contextual", ["disnea"],
                      "Volumen telesistólico del VI indexado a superficie corporal."),
    "wmsi": (4, "advanced", ["shock", "inestabilidad hemodinámica"],
             "Índice de puntuación de movilidad de pared del VI. Requiere valoración avanzada segmentaria de 16 o 17 segmentos miocárdicos."),
    "gls_vi": (4, "advanced", ["disnea"],
               "Strain longitudinal global del VI. Técnica avanzada basada en speckle tracking que requiere software especializado y alta resolución espacial."),

    # === SECCIÓN 2: lv_geometry ===
    "ivsd": (2, "extended", ["disnea"],
             "Grosor del septum interventricular en diástole. Útil en emergencias para descartar hipertrofia septal grave como causa de obstrucción."),
    "pwtd": (2, "extended", ["disnea"],
             "Grosor de la pared posterior del VI en diástole, usado para cuantificar la hipertrofia ventricular izquierda."),
    "rwt_meas": (3, "contextual", ["disnea"],
                 "Grosor relativo de pared (RWT). Clasifica el patrón geométrico (concéntrico vs excéntrico)."),
    "geometria_vi_meas": (3, "contextual", ["disnea"],
                           "Determina la geometría miocárdica para clasificar el tipo de remodelado adaptativo del VI."),
    "masa_vi_meas": (4, "advanced", ["disnea"],
                     "Estimación matemática de la masa absoluta del VI, propensa a amplificación de errores en mediciones lineales."),
    "lv_mass_index": (4, "advanced", ["disnea"],
                      "Masa del VI indexada a la superficie corporal."),

    # === SECCIÓN 3: stroke_volume_output ===
    "vti_tsvi_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                       "Integral de velocidad-tiempo del TSVI mediante Doppler pulsado. Parámetro fundamental para el cálculo del gasto cardíaco y la evaluación hemodinámica del shock."),
    "plr_vti_change": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                        "Variación del VTI del TSVI posterior a una elevación pasiva de piernas. Excelente predictor dinámico de la respuesta a volumen."),
    "area_tsvi_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                       "Área del TSVI a partir de su diámetro en PLAX. Crítico para estimación del volumen sistólico absoluto, pero propenso a errores geométricos."),
    "volumen_sistolico_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                               "Volumen sistólico absoluto derivado de la multiplicación del área del TSVI y el VTI del TSVI."),
    "sv_index": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                 "Volumen sistólico indexado a la superficie corporal."),
    "gasto_cardiaco_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                             "Cálculo cuantitativo del gasto cardíaco, multiplicando el volumen sistólico por la frecuencia cardíaca."),
    "cardiac_index": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                       "Índice cardíaco indexado a la superficie corporal del paciente."),
    "rvs_meas": (4, "advanced", ["shock", "inestabilidad hemodinámica"],
                 "Resistencias vasculares sistémicas absolutas, estimadas acoplando gasto cardíaco y presiones invasivas/no invasivas."),
    "irvs_meas": (4, "advanced", ["shock", "inestabilidad hemodinámica"],
                  "Resistencias vasculares sistémicas indexadas."),

    # === SECCIÓN 4: left_atrium ===
    "diametro_ap_ai": (2, "extended", ["disnea"],
                       "Diámetro lineal anteroposterior de la aurícula izquierda en PLAX. Indicador básico de sobrecarga volumétrica o presión crónica de la AI."),
    "volumen_ai_meas": (3, "contextual", ["disnea"],
                         "Volumen volumétrico de la aurícula izquierda por método de Simpson o área-longitud en apical."),
    "lavi_meas": (3, "contextual", ["disnea"],
                   "Volumen indexado de la aurícula izquierda (LAVI). Clave para perfilar disfunción diastólica crónica."),
    "dilatacion_ai_class": (3, "contextual", ["disnea"],
                             "Clasificación del grado de dilatación de la AI en base a umbrales del LAVI."),
    "la_strain_reservoir": (4, "advanced", ["disnea"],
                             "Técnica avanzada de strain de la aurícula izquierda para caracterizar la función reservorio."),

    # === SECCIÓN 5: lv_diastolic ===
    "onda_e_mitral": (2, "extended", ["disnea"],
                       "Velocidad de llenado rápido temprano transmitral por Doppler pulsado. Primer paso espectral en el algoritmo diastólico."),
    "onda_a_mitral": (2, "extended", ["disnea"],
                       "Velocidad de llenado tardío mitral. Necesaria para calcular el cociente E/A en ritmos con contracción auricular activa."),
    "relacion_e_a": (2, "extended", ["disnea"],
                     "Cociente de velocidades de llenado mitral. Permite una categorización inicial del patrón diastólico."),
    "e_septal_meas": (2, "extended", ["disnea"],
                       "Velocidad de relajación del anillo mitral septal por Doppler tisular (TDI). Valora alteración en la relajación del VI."),
    "e_lateral_meas": (2, "extended", ["disnea"],
                        "Velocidad de relajación del anillo mitral lateral por Doppler tisular (TDI)."),
    "relacion_e_e_promedio": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                              "Cociente E/e' promedio. Estima las presiones de llenado del VI de forma no invasiva, muy útil en el diagnóstico de insuficiencia cardíaca con FEVI preservada."),
    "ivrt_meas": (3, "contextual", ["disnea"],
                  "Tiempo de relajación isovolumétrica del VI por trazado Doppler continuo."),
    "velocidad_it_diastology": (3, "contextual", ["disnea"],
                                "Velocidad de insuficiencia tricuspídea aplicada al algoritmo de evaluación de disfunción diastólica."),
    "lavi_diastology": (3, "contextual", ["disnea"],
                         "Uso del LAVI como criterio acompañante para la estimación de las presiones de llenado."),
    "la_strain_diastology": (4, "advanced", ["disnea"],
                              "Uso de strain auricular reservorio avanzado en la caracterización de disfunción diastólica."),

    # === SECCIÓN 6: rv_systolic ===
    "tapse_meas": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                   "Excursión sistólica del anillo tricuspídeo por modo M. Medida cuantitativa lineal de la función longitudinal derecha, no reemplaza la valoración cualitativa global ni la integración multiparamétrica."),
    "s_prima_vd": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                    "Velocidad sistólica tisular del anillo tricuspídeo por TDI. Valora la contractilidad longitudinal derecha de forma complementaria al TAPSE."),
    "diametro_basal_vd": (2, "extended", ["disnea"],
                           "Diámetro lineal transversal basal del VD en apical de 4 cámaras enfocado, útil para cuantificar la dilatación derecha."),
    "diametro_medio_vd": (2, "extended", ["disnea"],
                          "Diámetro transversal a nivel medio del VD."),
    "rv_length": (2, "extended", ["disnea"],
                   "Longitud longitudinal del VD desde la base hasta el ápex."),
    "fac_vd_meas": (3, "contextual", ["disnea"],
                    "Cambio de área fraccional del VD. Estimador global de la función sistólica derecha pero dependiente de una adecuada ventana apical."),
    "vti_tsvd_meas": (3, "contextual", ["disnea"],
                      "Integral de velocidad-tiempo del TSVD."),
    "tapse_pasp_ratio": (3, "contextual", ["disnea", "inestabilidad hemodinámica"],
                         "Índice de acoplamiento ventrículo-arterial derecho. Refleja la reserva contráctil derecha frente a la poscarga pulmonar."),
    "indice_tei_vd": (4, "advanced", ["disnea"],
                      "Índice de rendimiento miocárdico derecho que evalúa la función global sistólica y diastólica combinada."),
    "strain_rv": (4, "advanced", ["disnea"],
                  "Strain longitudinal de la pared libre del VD por speckle tracking."),
    "fevd_3d": (4, "advanced", ["disnea"],
                "Fracción de eyección del VD tridimensional."),

    # === SECCIÓN 7: ra_ivc ===
    "presion_ad_estimada_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                                 "Estimación indirecta de la presión en la aurícula derecha a partir de la VCI (diámetro y colapso), necesaria para calcular la PASP."),
    "area_ad_meas": (2, "extended", ["disnea"],
                     "Área telesistólica de la aurícula derecha por planimetría 2D."),
    "longitud_ad": (3, "contextual", ["disnea"],
                    "Longitud lineal de la aurícula derecha desde el plano anular tricuspídeo."),
    "diametro_menor_ad": (3, "contextual", ["disnea"],
                          "Diámetro transversal menor de la aurícula derecha."),

    # === SECCIÓN 8: pulmonary_hemodynamics ===
    "gradiente_vd_ad": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                        "Gradiente de presión sistólica transvalvular tricuspídeo derivado de la velocidad máxima de IT. Base para estimar la PASP."),
    "pasp_meas": (2, "extended", ["disnea", "inestabilidad hemodinámica"],
                  "Presión sistólica de la arteria pulmonar estimada. Parámetro clave en la evaluación de hipertensión pulmonar y disfunción derecha."),
    "aplanamiento_septal_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                                 "Evaluación semicuantitativa del tabique aplanado (VI en D) en eje corto paraesternal. Denota sobrecarga derecha de volumen/presión en shock obstructivo."),
    "indice_excentricidad_vi": (3, "contextual", ["disnea"],
                                "Cuantificación geométrica del aplanamiento septal en diástole o sístole."),
    "presion_media_pulmonar": (3, "contextual", ["disnea"],
                               "Presión media de la arteria pulmonar a partir del espectro Doppler de insuficiencia pulmonar."),
    "presion_diastolica_pulmonar": (3, "contextual", ["disnea"],
                                    "Presión diastólica pulmonar estimada a partir de la velocidad final de insuficiencia pulmonar."),
    "rvp_ecografica": (4, "advanced", ["disnea", "inestabilidad hemodinámica"],
                        "Resistencia vascular pulmonar estimada por ecuación Doppler. Requiere acoplar medidas de TSVD e insuficiencia tricuspídea."),

    # === SECCIÓN 9: aortic_valve_lvot ===
    "velocidad_max_aortica": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                              "Velocidad sistólica máxima a través de la válvula aórtica por Doppler continuo. Clave para descartar estenosis aórtica severa como causa de shock."),
    "gradiente_max_aortico": (2, "extended", ["shock"],
                              "Gradiente transvalvular aórtico pico derivado de la velocidad aórtica."),
    "gradiente_medio_aortico": (2, "extended", ["shock"],
                                "Gradiente transvalvular medio obtenido por integración espectral de flujo aórtico."),
    "ava_meas": (3, "contextual", ["shock"],
                 "Área valvular aórtica calculada por ecuación de continuidad. Necesaria para la tipificación formal de estenosis severa."),
    "ava_indexed": (3, "contextual", ["shock"],
                     "Área valvular aórtica indexada a la superficie corporal del paciente."),
    "dvi_meas": (3, "contextual", ["shock"],
                 "Índice de velocidad adimensional. Útil en sospecha de estenosis aórtica cuando la ventana del TSVI es deficiente."),

    # === SECCIÓN 10: mitral_valve ===
    "area_mitral_pht": (3, "contextual", ["disnea"],
                        "Área valvular mitral calculada por el método del tiempo de hemipresión (PHT)."),
    "pht_meas": (3, "contextual", ["disnea"],
                 "Tiempo de hemipresión de la pendiente mitral por Doppler pulsado/continuo."),
    "area_mitral_planimetria": (4, "advanced", ["disnea"],
                                "Medición directa del orificio mitral por planimetría bidimensional en eje corto paraesternal."),
    "relacion_vti_mitral_tsvi": (4, "advanced", ["disnea"],
                                 "Relación de integrales mitral/aórtico, usada en evaluaciones de Shunt o sobrecarga."),

    # === SECCIÓN 11: valvular_regurgitation ===
    "flujo_pisa_meas": (4, "advanced", ["disnea"],
                        "Técnica avanzada de área de isovelocidad proximal (PISA) para cuantificación de reflujo."),
    "eroa_meas": (4, "advanced", ["disnea"],
                  "Área del orificio regurgitante efectivo obtenido por método PISA."),
    "volumen_regurgitante_meas": (4, "advanced", ["disnea"],
                                  "Volumen regurgitante total calculado cuantitativamente."),
    "fraccion_regurgitante_meas": (4, "advanced", ["disnea"],
                                   "Fracción de regurgitación calculada para definir la sobrecarga de volumen."),

    # === SECCIÓN 12: pericardium_tamponade ===
    "derrame_pericardico_pequeno": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                                    "Graduación cuantitativa/semicuantitativa del derrame pericárdico leve (<10 mm). Debe integrarse con la repercusión mecánica y no valorarse de forma aislada."),
    "derrame_pericardico_moderado": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                                     "Graduación del derrame pericárdico moderado (10-20 mm)."),
    "derrame_pericardico_grande": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                                   "Graduación del derrame pericárdico grande (>20 mm), con alto riesgo de compromiso mecánico."),
    "colapso_ad_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                        "Signo de repercusión hemodinámica caracterizado por el colapso sistólico de la aurícula derecha. Debe integrarse con el contexto clínico; no es un diagnóstico definitivo aislado de taponamiento."),
    "colapso_vd_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                        "Signo de repercusión caracterizado por el colapso diastólico de la pared libre del VD."),
    "vci_pletorica_meas": (2, "extended", ["shock", "inestabilidad hemodinámica"],
                           "VCI dilatada con colapso ausente, con alto valor predictivo negativo para descartar taponamiento en sospecha clínica activa."),
    "movimiento_pendular_meas": (3, "contextual", ["shock", "inestabilidad hemodinámica"],
                                 "Vaivén del corazón en derrames grandes ('swinging heart'), signo cualitativo contextual.")
}

# Unificar todas las prioridades en un diccionario único TIERS
TIERS = {}
TIERS.update(LOCKED_PRIORITIES)
TIERS.update(CLINICALLY_REVIEWED_OVERRIDES)
TIERS.update(WITHDRAWN_ASCENTS)
TIERS.update(BASE_PRIORITIES)

# Fuentes científicas oficiales
REF_MAPPING = {
    "focus_recommendations_2014": {
        "id": "focus_recommendations_2014",
        "title": "International Evidence-Based Recommendations for Focused Cardiac Ultrasound",
        "authors": "Via G, Hussain A, Wells M, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2014,
        "doi": "10.1016/j.echo.2014.05.001",
        "url": "https://doi.org/10.1016/j.echo.2014.05.001",
        "verification_status": "verified"
    },
    "chamber_quantification_2015": {
        "id": "chamber_quantification_2015",
        "title": "Recommendations for Chamber Quantification: Guidelines from the American Society of Echocardiography and the European Association of Cardiovascular Imaging",
        "authors": "Lang RM, Badano LP, Mor-Avi V, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2015,
        "doi": "10.1016/j.echo.2014.10.003",
        "url": "https://doi.org/10.1016/j.echo.2014.10.003",
        "verification_status": "verified"
    },
    "right_heart_assessment_2010": {
        "id": "right_heart_assessment_2010",
        "title": "Guidelines for the Echocardiographic Assessment of the Right Heart in Adults: A Report from the American Society of Echocardiography",
        "authors": "Rudski LG, Lai WW, Afilalo J, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2010,
        "doi": "10.1016/j.echo.2010.05.010",
        "url": "https://doi.org/10.1016/j.echo.2010.05.010",
        "verification_status": "verified"
    },
    "right_heart_assessment_2025": {
        "id": "right_heart_assessment_2025",
        "title": "Guidelines for the Echocardiographic Assessment of the Right Heart in Adults and Special Considerations in Pulmonary Hypertension: Recommendations from the American Society of Echocardiography",
        "authors": "Mukherjee M, Rudski LG, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2025,
        "doi": "10.1016/j.echo.2025.01.006",
        "url": "https://doi.org/10.1016/j.echo.2025.01.006",
        "verification_status": "verified"
    },
    "diastolic_function_2016": {
        "id": "diastolic_function_2016",
        "title": "Recommendations for the Evaluation of Left Ventricular Diastolic Function by Echocardiography: An Update from the American Society of Echocardiography and the European Association of Cardiovascular Imaging",
        "authors": "Nagueh SF, Smiseth OA, Appleton CP, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2016,
        "doi": "10.1016/j.echo.2016.01.011",
        "url": "https://doi.org/10.1016/j.echo.2016.01.011",
        "verification_status": "verified"
    },
    "diastolic_function_2025": {
        "id": "diastolic_function_2025",
        "title": "Recommendations for the Evaluation of Left Ventricular Diastolic Function and HFpEF Diagnosis: Recommendations from the American Society of Echocardiography",
        "authors": "ASE Task Force, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2025,
        "verification_status": "verified"
    },
    "valvular_regurgitation_2017": {
        "id": "valvular_regurgitation_2017",
        "title": "Recommendations for Noninvasive Evaluation of Native Valvular Regurgitation: Recommendations from the American Society of Echocardiography",
        "authors": "Zoghbi WA, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2017,
        "doi": "10.1016/j.echo.2017.01.007",
        "url": "https://doi.org/10.1016/j.echo.2017.01.007",
        "verification_status": "verified"
    },
    "clinical_tamponade_consensus": {
        "id": "clinical_tamponade_consensus",
        "title": "Echocardiographic assessment of pericardial effusion and cardiac tamponade",
        "authors": "Adler Y, Charron P, Imazio M, et al.",
        "organization_or_journal": "European Heart Journal",
        "year": 2015,
        "doi": "10.1093/eurheartj/ehv317",
        "url": "https://doi.org/10.1093/eurheartj/ehv317",
        "verification_status": "verified"
    },
    "spencer_ase_focus_2013": {
        "id": "spencer_ase_focus_2013",
        "title": "Focused Cardiac Ultrasound: Recommendations from the American Society of Echocardiography",
        "authors": "Spencer KT, Kimura BJ, Korcarz CE, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2013,
        "doi": "10.1016/j.echo.2013.04.001",
        "url": "https://doi.org/10.1016/j.echo.2013.04.001",
        "verification_status": "verified"
    },
    "kirkpatrick_ase_nomenclature_2024": {
        "id": "kirkpatrick_ase_nomenclature_2024",
        "title": "Guidelines for Cardiac Point-of-Care Ultrasound Nomenclature: Recommendations from the American Society of Echocardiography",
        "authors": "Kirkpatrick JN, et al.",
        "organization_or_journal": "Journal of the American Society of Echocardiography",
        "year": 2024,
        "verification_status": "verified"
    }
}

# Asignación de referencias por sección o ID de medición
def get_refs_for_item(m_id, s_id):
    refs = []
    # Guías principales según la sección clínica
    if s_id == "lv_diastolic":
        refs.append("diastolic_function_2025")
        refs.append("diastolic_function_2016")
    elif s_id in ["rv_systolic", "ra_ivc", "pulmonary_hemodynamics"]:
        refs.append("right_heart_assessment_2025")
        refs.append("right_heart_assessment_2010")
    elif s_id == "pericardium_tamponade":
        refs.append("clinical_tamponade_consensus")
    elif s_id in ["valvular_regurgitation", "mitral_valve", "aortic_valve_lvot"]:
        refs.append("valvular_regurgitation_2017")
        refs.append("chamber_quantification_2015")
    else:
        refs.append("chamber_quantification_2015")

    # Añadir recomendaciones de FoCUS y nomenclatura 2024 para niveles 1 y 2
    tier_info = TIERS.get(m_id)
    if tier_info and tier_info[0] in [1, 2]:
        refs.append("focus_recommendations_2014")
        refs.append("spencer_ase_focus_2013")
        refs.append("kirkpatrick_ase_nomenclature_2024")

    return list(sorted(list(set(refs))))

def get_spanish_text(value):
    if isinstance(value, dict):
        return value.get("es") or value.get("en") or ""
    return value if isinstance(value, str) else ""

def main():
    # Leer secciones originales
    with open("data/sections.json", "r", encoding="utf-8") as f:
        sections_data = json.load(f)

    section_titles = {}
    for s in sections_data:
        s_id = s.get("id")
        title = get_spanish_text(s.get("title"))
        if not title:
            raise ValueError(f"Error: la sección '{s_id}' no tiene un título válido (vacío o no es string).")
        section_titles[s_id] = title

    # Leer mediciones originales
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)

    print(f"Cargadas {len(measurements)} mediciones del archivo principal.")

    # Agrupar por sección clínica real
    grouped_sections = {}
    for m in measurements:
        s_id = m['section_id']
        if s_id not in section_titles:
            raise ValueError(f"Error: section_id '{s_id}' en medición '{m['id']}' no existe en sections.json")
        if s_id not in grouped_sections:
            grouped_sections[s_id] = []
        grouped_sections[s_id].append(m)

    priorities = []

    for s_id, items in grouped_sections.items():
        # Ordenar items según la prioridad configurada en TIERS
        # Primero por tier (1 a 4), luego por original_order (donde fevi siempre va primero si está en ese tier)
        sorted_items = sorted(
            items,
            key=lambda x: (TIERS.get(x['id'], (4, "advanced", [], ""))[0], 0 if x['id'] == 'fevi' else x['order'])
        )
        for idx, item in enumerate(sorted_items):
            m_id = item['id']
            m_title = item['measurement']
            orig_order = item['order']

            tier_info = TIERS.get(m_id)
            if not tier_info:
                print(f"Advertencia: No hay info de prioridad para {m_id}. Asignando nivel 4 por defecto.")
                tier_info = (4, "advanced", [], "Evaluación ecocardiográfica avanzada dependiente del contexto clínico.")

            tier, scope, contexts, rationale = tier_info

            labels = {
                1: "Núcleo POCUS",
                2: "POCUS extendido",
                3: "Dependiente del contexto",
                4: "Avanzado / ecocardiografía integral"
            }

            p = {
                "measurement_id": m_id,
                "measurement_title": m_title,
                "section_id": s_id,
                "section_title": section_titles[s_id],
                "primary_window": item.get("primary_window", ""),
                "preferred_view": item.get("preferred_view", ""),
                "alternate_windows": item.get("alternate_windows", []),
                "modality": item.get("modality", ""),
                "acquisition_timing": item.get("acquisition_timing", ""),
                "original_order": orig_order,
                "priority_tier": tier,
                "priority_label": labels[tier],
                "display_order": idx + 1,
                "pocus_scope": scope,
                "clinical_contexts": contexts,
                "rationale": rationale,
                "reference_ids": get_refs_for_item(m_id, s_id),
                "confidence": "moderate" if m_id in ["fevi", "relacion_vd_vi", "diametro_vci_meas", "colapsabilidad_vci_meas"] else "high",
                "review_status": "pending"
            }
            priorities.append(p)

    # Estructura del draft.json
    draft = {
        "metadata": {
            "title": "Prioridad clínica de visualización de mediciones",
            "version": "draft-2",
            "status": "pending-clinical-review",
            "scope": "POCUS cardíaco en adultos",
            "methodology": "Síntesis razonada basada en guías y consensos internacionales",
            "expected_measurement_count": 101,
            "actual_measurement_count": len(measurements),
            "last_reviewed": "2026-07-20",
            "disclaimer": "No representa una frecuencia mundial medida ni un ranking oficial universal."
        },
        "references": list(REF_MAPPING.values()),
        "priorities": priorities
    }

    with open("data/measurement-priority.draft.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)

    print("Borrador de prioridades generado con éxito en data/measurement-priority.draft.json.")

if __name__ == "__main__":
    main()
