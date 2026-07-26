import os
import json
import re
import pytest

def test_new_translation_keys_e1b():
    path = "data/translations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    translations = data.get("translations", {})
    
    new_keys = {
        "error.windows_load_title": {
            "es": "Error al cargar las ventanas",
            "en": "Error loading echocardiographic windows"
        },
        "error.windows_load_text": {
            "es": "Lo sentimos, no pudimos cargar la lista de ventanas ecocardiográficas. Por favor, intente nuevamente más tarde.",
            "en": "Sorry, we could not load the list of echocardiographic windows. Please try again later."
        },
        "error.window_detail_load_title": {
            "es": "Error al cargar la información",
            "en": "Error loading information"
        },
        "error.window_detail_load_text": {
            "es": "No se pudo cargar la información de la ventana ecocardiográfica.",
            "en": "The echocardiographic window information could not be loaded."
        },
        "nav.back_to_windows": {
            "es": "Volver a Ventanas",
            "en": "Back to Windows"
        },
        "error.protocols_load_title": {
            "es": "Error al cargar los protocolos",
            "en": "Error loading protocols"
        },
        "error.protocols_load_text": {
            "es": "Lo sentimos, no pudimos cargar la lista de protocolos POCUS. Por favor, intente nuevamente más tarde.",
            "en": "Sorry, we could not load the POCUS protocol list. Please try again later."
        },
        "label.protocol_guide_completed": {
            "es": "Ha completado la guía de componentes",
            "en": "You have completed the component guide"
        },
        "label.abbreviations_list_title": {
            "es": "Lista de abreviaturas",
            "en": "Abbreviations"
        },
        "label.practical_classifications": {
            "es": "Clasificaciones Prácticas",
            "en": "Practical Classifications"
        },
        "label.cutoff_point": {
            "es": "Punto de corte",
            "en": "Cutoff value"
        },
        "label.note": {
            "es": "Nota",
            "en": "Note"
        },
        "label.cited_on_pdf_page": {
            "es": "Citado en Página {page} del PDF.",
            "en": "Cited on page {page} of the PDF."
        },
        "label.editorial_note": {
            "es": "Nota editorial",
            "en": "Editorial note"
        },
        "label.editorial_note_text": {
            "es": "Los valores de referencia pueden variar entre guías, laboratorios, equipos y poblaciones. Para decisiones clínicas definitivas debe consultarse la publicación primaria y el protocolo institucional vigente.",
            "en": "Reference values may vary among guidelines, laboratories, equipment, and populations. For definitive clinical decisions, the primary publication and the current institutional protocol should be consulted."
        },
        "nav.back_to_quizzes": {
            "es": "Volver a Cuestionarios",
            "en": "Back to Quizzes"
        },
        "error.quiz_unavailable_title": {
            "es": "Cuestionario no disponible",
            "en": "Quiz unavailable"
        },
        "error.quiz_unavailable_text": {
            "es": "El cuestionario solicitado no está disponible o su formato no es válido.",
            "en": "The requested quiz is unavailable or its format is invalid."
        },
        "nav.back_to_list": {
            "es": "Volver a la lista",
            "en": "Back to the list"
        }
    }
    
    assert len(new_keys) == 19
    
    for key, val in new_keys.items():
        assert key in translations, f"Missing translation key: {key}"
        assert translations[key]["es"] == val["es"]
        assert translations[key]["en"] == val["en"]
        assert isinstance(translations[key]["es"], str) and translations[key]["es"].strip() != ""
        assert isinstance(translations[key]["en"], str) and translations[key]["en"].strip() != ""


def get_function_body(content, func_name):
    # Match the method declaration at 4 spaces indentation
    pattern = rf"^    (?:async\s+)?{func_name}\s*\(.*?\n(.*?)(?=^    (?:async\s+)?[a-zA-Z0-9_]+\s*\(|^\S|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def test_router_visible_messages_e1b():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    render_funcs = [
        "renderWindowsList",
        "renderWindowDetail",
        "renderProtocolsList",
        "renderAbbreviations",
        "renderClassifications",
        "renderReferences",
        "renderQuizFlow",
        "renderAbout"
    ]
    
    bodies = {f: get_function_body(content, f) for f in render_funcs}
    
    # renderWindowsList
    assert bodies["renderWindowsList"] is not None
    assert "error.windows_load_title" in bodies["renderWindowsList"]
    assert "error.windows_load_text" in bodies["renderWindowsList"]
    assert "nav.windows" in bodies["renderWindowsList"]
    assert "isEs" not in bodies["renderWindowsList"]
    assert "Ventanas Ecocardiográficas" not in bodies["renderWindowsList"]
    
    # renderWindowDetail
    assert bodies["renderWindowDetail"] is not None
    assert "error.window_detail_load_title" in bodies["renderWindowDetail"]
    assert "error.window_detail_load_text" in bodies["renderWindowDetail"]
    assert "nav.back_to_windows" in bodies["renderWindowDetail"]
    
    # renderProtocolsList
    assert bodies["renderProtocolsList"] is not None
    assert "error.protocols_load_title" in bodies["renderProtocolsList"]
    assert "error.protocols_load_text" in bodies["renderProtocolsList"]
    
    # RUSH guide completion in renderProtocolDetail
    proto_detail_body = get_function_body(content, "renderProtocolDetail")
    assert proto_detail_body is not None
    assert "label.protocol_guide_completed" in proto_detail_body
    assert "Ha completado la guía de componentes:" not in proto_detail_body
    
    # renderAbbreviations
    assert bodies["renderAbbreviations"] is not None
    assert "label.abbreviations_list_title" in bodies["renderAbbreviations"]
    assert "Lista de " not in bodies["renderAbbreviations"]
    
    # renderClassifications
    assert bodies["renderClassifications"] is not None
    assert "label.practical_classifications" in bodies["renderClassifications"]
    assert "label.cutoff_point" in bodies["renderClassifications"]
    assert "label.note" in bodies["renderClassifications"]
    assert "isEs" not in bodies["renderClassifications"]
    
    # renderReferences
    assert bodies["renderReferences"] is not None
    assert "label.cited_on_pdf_page" in bodies["renderReferences"]
    assert "label.editorial_note" in bodies["renderReferences"]
    assert "label.editorial_note_text" in bodies["renderReferences"]
    assert "Citado en Página" not in bodies["renderReferences"]
    assert "Nota editorial" not in bodies["renderReferences"]
    assert "${escapeHTML(r.citation)}" in bodies["renderReferences"]
    
    # renderQuizFlow
    assert bodies["renderQuizFlow"] is not None
    assert "nav.back_to_quizzes" in bodies["renderQuizFlow"]
    assert "error.quiz_unavailable_title" in bodies["renderQuizFlow"]
    assert "error.quiz_unavailable_text" in bodies["renderQuizFlow"]
    assert "nav.back_to_list" in bodies["renderQuizFlow"]
    assert "Volver a Cuestionarios" not in bodies["renderQuizFlow"]
    
    # renderAbout paragraphs MUST be localized (updated for E1C)
    assert bodies["renderAbout"] is not None
    assert 'I18n.translate("app.name")' in bodies["renderAbout"]
    assert 'I18n.translate("label.about_title")' in bodies["renderAbout"]
    assert 'I18n.translate("label.about_app_description")' in bodies["renderAbout"]
    assert 'I18n.translate("label.about_training_objective")' in bodies["renderAbout"]
    assert 'I18n.translate("label.about_development_prefix")' in bodies["renderAbout"]
    assert 'I18n.translate("label.about_source_prefix")' in bodies["renderAbout"]

    assert "es una aplicación web y PWA educativa, diseñada exclusivamente como una herramienta de consulta rápida y banco de mediciones." not in bodies["renderAbout"]
    assert "Tiene como objetivo apoyar en la formación de médicos generales" not in bodies["renderAbout"]
    assert "Esta aplicación fue desarrollada y revisada por médicos internistas" not in bodies["renderAbout"]
    assert "Toda la información médica está compilada de manera estricta del documento fuente oficial" not in bodies["renderAbout"]
    assert "Acerca de" in content or "label.about_title" in content


def test_router_security_e1b():
    path = "assets/js/router.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    def check_escape_before_try(func_name):
        body = get_function_body(content, func_name)
        assert body is not None, f"Function {func_name} body not found"
        assert "const escapeHTML" in body, f"escapeHTML not declared in {func_name}"
        if "try {" in body:
            escape_idx = body.find("const escapeHTML")
            try_idx = body.find("try {")
            assert escape_idx < try_idx, f"escapeHTML is not declared before try block in {func_name}"

    check_escape_before_try("renderWindowsList")
    check_escape_before_try("renderWindowDetail")
    check_escape_before_try("renderProtocolsList")
    check_escape_before_try("renderReferences")
    check_escape_before_try("renderQuizFlow")

    assert "step.components_names.map(name => escapeHTML(name)).join(\", \")" in content


def test_cache_and_precache_e1b():
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b" in content
    assert "./assets/js/router.js" in content
    assert "./data/translations.json" in content
    assert "./assets/images/locus_pocus_branding.png" in content
    assert "./assets/icons/locus-pocus-icon-192.png" in content
    assert "caches.match('./assets/icons/locus-pocus-icon-192.png')" in content


def test_clinical_data_protection_e1b():
    with open("data/minimum_pocus_set.json", "r", encoding="utf-8") as f:
        min_set = json.load(f)
    assert len(min_set) == 10
    for item in min_set:
        assert "es" in item["skill"]
        assert "en" in item["skill"]
        
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101
    for m in measurements:
        assert "es" in m["measurement"]
        assert "en" in m["measurement"]
        
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols = json.load(f)["protocols"]
    assert len(protocols) == 1
    assert protocols[0]["id"] == "rush"
    
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)["translations"]
    assert translations["app.name"]["es"] == "LOCUS POCUS"
    assert translations["app.name"]["en"] == "LOCUS POCUS"
