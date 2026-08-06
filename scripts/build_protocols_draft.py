import json
import os
import sys

def main():
    # Rutas relativas
    windows_path = "data/windows.json"
    measurements_path = "data/measurements.json"
    output_path = "data/protocols.draft.json"

    # Cargar datos existentes para validación
    if not os.path.exists(windows_path):
        print(f"Error: {windows_path} no existe.")
        sys.exit(1)
    if not os.path.exists(measurements_path):
        print(f"Error: {measurements_path} no existe.")
        sys.exit(1)

    with open(windows_path, "r", encoding="utf-8") as f:
        windows = json.load(f)
    with open(measurements_path, "r", encoding="utf-8") as f:
        measurements = json.load(f)

    valid_window_ids = {w["id"] for w in windows}
    valid_measurement_ids = {m["id"] for m in measurements}

    # Definir datos del borrador del protocolo RUSH
    draft_data = {
        "metadata": {
            "title": "Borrador de Protocolos Clínicos POCUS",
            "version": "0.1.0",
            "status": "pending-clinical-review",
            "scope": "Ultrasonido en el punto de atención (POCUS) para la evaluación de pacientes en estado crítico.",
            "intended_audience": "Residentes y médicos en formación en Medicina de Urgencias, Medicina Crítica y Medicina Interna.",
            "protocol_count": 1,
            "generated_on": "2026-07-21",
            "disclaimer": "Esta es una herramienta educativa y de consulta rápida. El examen RUSH complementa y no sustituye la valoración clínica exhaustiva ni el ecocardiograma formal. Los hallazgos ecográficos no deben interpretarse de forma aislada, y la realización del ultrasonido no debe retrasar las maniobras de reanimación cardiopulmonar o hemodinámica. Un resultado negativo en el protocolo no excluye por sí solo todas las posibles causas de choque."
        },
        "references": [
            {
                "id": "ref_perera_2010",
                "citation": "Perera P, Mailhot T, Riley D, Mandavia D. The RUSH exam: Rapid Ultrasound in SHock in the evaluation of the critically ill. Emergency Medicine Clinics of North America. 2010;28(1):29-56, vii.",
                "pmid": "19945597",
                "doi": "10.1016/j.emc.2009.09.010"
            },
            {
                "id": "ref_seif_2012",
                "citation": "Seif D, Perera P, Mailhot T, Riley D, Mandavia D. Bedside Ultrasound in Resuscitation and the Rapid Ultrasound in Shock Protocol. Critical Care Research and Practice. 2012;2012:503254.",
                "pmcid": "PMC3485910",
                "doi": "10.1155/2012/503254"
            },
            {
                "id": "ref_atkinson_2016",
                "citation": "Atkinson P, Bowra J, Milne J, et al. International Federation for Emergency Medicine Consensus Statement: Sonography in hypotension and cardiac arrest (SHoC). Canadian Journal of Emergency Medicine. 2017;19(6):459-470.",
                "doi": "10.1017/cem.2016.394"
            }
        ],
        "protocols": [
            {
                "id": "rush",
                "name_es": "Protocolo RUSH",
                "name_en": "RUSH Protocol",
                "acronym": "RUSH",
                "clinical_context": "Evaluación rápida y sistemática de pacientes con choque o hipotensión de etiología no clara.",
                "purpose": "Ayudar a diferenciar las etiologías principales del estado de choque (hipovolémico, distributivo, cardiogénico y obstructivo) a través de una exploración ecográfica protocolizada.",
                "target_population": "Pacientes adultos críticamente enfermos con hipotensión sistólica sostenida (<90 mmHg) o signos clínicos de choque.",
                "prerequisites": "Formación básica en ecocardiografía enfocada y ecografía general en el punto de atención (POCUS).",
                "sequence_note": "La tríada didáctica (Bomba, Tanque y Tuberías) no constituye una secuencia obligatoria e invariable. El orden de adquisición debe adaptarse activamente a la inestabilidad del paciente, la sospecha diagnóstica prioritaria, la presencia de ventanas ecográficas viables y la urgencia de intervenciones salvavidas inmediatas.",
                "integration": "Los hallazgos del protocolo RUSH deben integrarse en el contexto clínico general del paciente. Patrones específicos (ej. hipercontractilidad del VI con colapso de VCI y colapso de cavidades derechas) apoyan hipótesis fisiológicas específicas (ej. shock hipovolémico u obstructivo) pero no sustituyen el diagnóstico definitivo de laboratorio o imagen avanzada.",
                "limitations": "La precisión depende de la ventana acústica, la experiencia del operador y el contexto clínico. RUSH no confirma por sí solo la etiología del choque; los hallazgos pueden ser inespecíficos, coexistir o reflejar enfermedad crónica. Un examen negativo no excluye patología y la evaluación de la VCI y la ecografía de compresión venosa limitada tienen restricciones propias.",
                "safety_and_workflow_notes": "Integrar los hallazgos con la historia, exploración física, signos vitales y respuesta al tratamiento. El examen no debe retrasar la reanimación, las intervenciones salvavidas ni los estudios definitivos cuando estén indicados. Repetir la evaluación ante cambios clínicos.",
                "reference_ids": ["ref_perera_2010", "ref_seif_2012", "ref_atkinson_2016"],
                "review_status": "pending-clinical-review",
                "components": [
                    {
                        "id": "pump",
                        "name_es": "La Bomba (Evaluación cardíaca)",
                        "name_en": "The Pump (Cardiac Evaluation)",
                        "clinical_questions": [
                            "¿Existe derrame pericárdico con signos de repercusión hemodinámica?",
                            "¿Cómo está la función sistólica global del ventrículo izquierdo?",
                            "¿Hay dilatación o signos de sobrecarga del ventrículo derecho?"
                        ],
                        "targets": [
                            "Derrame pericárdico (pequeño, moderado, grande) y colapso de cavidades derechas en diástole.",
                            "Contractilidad global del VI (hiperdinámico, normal, disminuido) y EPSS.",
                            "Relación de diámetros del ventrículo derecho respecto al ventrículo izquierdo (dilatación del VD)."
                        ],
                        "suggested_views": [
                            "Paraesternal eje largo (PLAX)",
                            "Paraesternal eje corto (PSAX)",
                            "Apical cuatro cámaras (A4C)",
                            "Subcostal cuatro cámaras (SC4C)"
                        ],
                        "linked_window_ids": [
                            "plax",
                            "psax",
                            "a4c",
                            "subcostal_4c"
                        ],
                        "linked_measurement_ids": [
                            "derrame_pericardico_pequeno",
                            "derrame_pericardico_moderado",
                            "derrame_pericardico_grande",
                            "fevi",
                            "epss",
                            "diametro_basal_vd",
                            "relacion_vd_vi",
                            "tapse_meas",
                            "s_prima_vd",
                            "colapso_vd_meas"
                        ],
                        "possible_findings": [
                            "Derrame pericárdico con colapso sistólico de la AD o colapso diastólico del VD, hallazgos que apoyan repercusión hemodinámica. El taponamiento es un diagnóstico clínico-hemodinámico y no se determina únicamente por el tamaño del derrame.",
                            "VI hiperdinámico con obliteración sistólica de la cavidad ('kissing papillary muscles'), patrón compatible con bajo llenado o vasodilatación en el contexto apropiado, pero no diagnóstico por sí solo de hipovolemia ni de vasoplejía.",
                            "VI con función sistólica global severamente reducida, hallazgo que puede apoyar un componente cardiogénico del choque cuando concuerda con la evaluación clínica y hemodinámica.",
                            "VD dilatado (relación VD/VI >1,0) con aplanamiento septal o signo de McConnell, compatible con sobrecarga del VD aguda o crónica. Estos hallazgos no diagnostican TEP de forma aislada."
                        ],
                        "interpretation_limits": "Una relación VD/VI elevada de forma aislada no diagnostica embolia pulmonar (debe evaluarse cronicidad e hipertensión pulmonar). La ausencia de derrame pericárdico no excluye otras etiologías obstructivas. Una función sistólica global del ventrículo izquierdo aparentemente preservada o hiperdinámica no excluye por sí sola un choque cardiogénico, por ejemplo cuando existe disfunción aguda del ventrículo derecho, enfermedad valvular aguda o una complicación mecánica. Debe integrarse con el gasto cardiaco, las condiciones de carga y el contexto clínico. Un solo hallazgo no debe utilizarse de forma aislada para determinar la etiología del choque.",
                        "reference_ids": ["ref_perera_2010", "ref_seif_2012"],
                        "quick_reference": {
                            "assess": "Función global del VI, tamaño del VD y derrame pericárdico con colapso de cavidades derechas.",
                            "alerts": "Taponamiento, VI hiperdinámico o severamente deprimido y dilatación aguda del VD."
                        }
                    },
                    {
                        "id": "tank",
                        "name_es": "El Tanque (Evaluación de Volumen)",
                        "name_en": "The Tank (Volume Evaluation)",
                        "clinical_questions": [
                            "¿Cómo se comporta el diámetro y colapsabilidad de la vena cava inferior?",
                            "¿Hay signos ecográficos de congestión pulmonar o neumotórax?",
                            "¿Existe líquido libre intraperitoneal o derrame pleural?"
                        ],
                        "targets": [
                            "Diámetro y colapsabilidad/distensibilidad de la VCI en ventilación espontánea o mecánica.",
                            "Pulmón y pleura: presencia de líneas A, líneas B (patrón alveolar/intersticial) y deslizamiento pleural (sliding).",
                            "Espacios dependientes del abdomen (Morison, esplenorrenal, subvesical) para líquido libre."
                        ],
                        "suggested_views": [
                            "Subcostal eje largo de VCI (SC-VCI)",
                            "Ventanas pulmonares anteriores y laterales",
                            "Ventanas abdominales del FAST (cuadrante superior derecho, izquierdo y pelvis)"
                        ],
                        "linked_window_ids": [
                            "subcostal_ivc"
                        ],
                        "linked_measurement_ids": [
                            "diametro_vci_meas",
                            "colapsabilidad_vci_meas",
                            "distensibilidad_vci_meas",
                            "vci_pletorica_meas"
                        ],
                        "possible_findings": [
                            "VCI pequeña y marcadamente colapsable, hallazgo que puede apoyar presión auricular derecha baja en el contexto apropiado; no determina por sí solo la volemia ni la respuesta a fluidos.",
                            "En respiración espontánea, VCI >2,1 cm con colapso inspiratorio <50 %, patrón que sugiere presión auricular derecha elevada. Estos umbrales no deben trasladarse directamente a ventilación mecánica.",
                            "Ausencia de deslizamiento pleural con patrón de líneas A, hallazgo que aumenta la sospecha de neumotórax pero tiene diagnósticos diferenciales. La identificación de un punto pulmonar ('lung point') aumenta la especificidad.",
                            "Múltiples líneas B bilaterales y difusas, indicativas de síndrome intersticial. Por sí solas no distinguen edema cardiogénico de SDRA u otras causas.",
                            "Líquido libre intraperitoneal en el espacio hepatorrenal, esplenorrenal o la pelvis. La ecografía no determina por sí sola su naturaleza ni su causa."
                        ],
                        "interpretation_limits": "La evaluación de la VCI debe integrarse con otros parámetros. El diámetro y la colapsabilidad aislados no definen con precisión la volemia ni predicen la respuesta a fluidos en todos los pacientes (especialmente bajo ventilación mecánica o en presencia de presiones intratorácicas elevadas). Una VCI pequeña no obliga por sí sola a infundir líquidos, y una VCI dilatada no confirma congestión o taponamiento de forma aislada.",
                        "reference_ids": ["ref_perera_2010", "ref_seif_2012"],
                        "quick_reference": {
                            "assess": "VCI, patrón pulmonar y pleural, y líquido libre intraperitoneal.",
                            "alerts": "Depleción o congestión marcada, neumotórax, edema pulmonar o SDRA y líquido libre intraperitoneal."
                        }
                    },
                    {
                        "id": "pipes",
                        "name_es": "Las Tuberías (Evaluación Vascular)",
                        "name_en": "The Pipes (Vascular Evaluation)",
                        "clinical_questions": [
                            "¿Hay evidencia de aneurisma o disección en la aorta abdominal?",
                            "¿Existe trombosis venosa profunda (TVP) en las extremidades inferiores?"
                        ],
                        "targets": [
                            "Aorta abdominal en sus segmentos proximal, medio y distal.",
                            "Vena femoral común y vena poplítea mediante ecografía de compresión en 2 puntos."
                        ],
                        "suggested_views": [
                            "Barrido de aorta abdominal desde epigastrio hasta la bifurcación ilíaca",
                            "Eje transversal de vasos femorales y poplíteos"
                        ],
                        "linked_window_ids": [],
                        "linked_measurement_ids": [],
                        "possible_findings": [
                            "Aorta abdominal >3 cm, medida de pared externa a pared externa, compatible con aneurisma; un colgajo íntimal visible es preocupante por disección. Un examen POCUS negativo no excluye patología aórtica.",
                            "Falta de compresibilidad completa de una vena profunda, indicativa de trombosis. La ecografía de compresión limitada no establece por sí sola la antigüedad del trombo y puede omitir segmentos no examinados."
                        ],
                        "interpretation_limits": "Una evaluación limitada o negativa no excluye por completo la existencia de TVP en otros segmentos venosos. La imposibilidad de visualizar la aorta abdominal (por ejemplo, debido a gas intestinal excesivo) no excluye la presencia de un aneurisma. La ausencia de TVP detectada no descarta una embolia pulmonar en curso. El protocolo RUSH no sustituye a los estudios diagnósticos vasculares definitivos (como angiotomografía o ecografía dúplex completa).",
                        "reference_ids": ["ref_perera_2010", "ref_seif_2012"],
                        "quick_reference": {
                            "assess": "Aorta abdominal y compresibilidad de las venas femoral común y poplítea.",
                            "alerts": "Aneurisma o disección aórtica y TVP proximal."
                        }
                    }
                ]
            }
        ]
    }

    # Validar IDs vinculados
    for protocol in draft_data["protocols"]:
        for component in protocol["components"]:
            # Validar ventanas
            for w_id in component["linked_window_ids"]:
                if w_id not in valid_window_ids:
                    print(f"Error de validación: El ID de ventana '{w_id}' en el componente '{component['id']}' no existe en {windows_path}")
                    sys.exit(1)
            # Validar mediciones
            for m_id in component["linked_measurement_ids"]:
                if m_id not in valid_measurement_ids:
                    print(f"Error de validación: El ID de medición '{m_id}' en el componente '{component['id']}' no existe en {measurements_path}")
                    sys.exit(1)

    # Generar JSON de salida consistente
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(draft_data, f, indent=2, ensure_ascii=False)

    print(f"Borrador generado con éxito en {output_path}")

if __name__ == "__main__":
    main()
