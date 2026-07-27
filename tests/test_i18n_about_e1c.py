import os
import json
import re
import pytest

def get_function_body(content, func_name):
    pattern = rf"^    (?:async\s+)?{func_name}\s*\(.*?\n(.*?)(?=^    (?:async\s+)?[a-zA-Z0-9_]+\s*\(|^\S|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None

def test_new_translation_keys_e1c():
    path = "data/translations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", {})

    new_keys = {
        "label.about_app_description": {
            "es": "es una aplicación web y PWA educativa, diseñada exclusivamente como una herramienta de consulta rápida y banco de mediciones.",
            "en": "is an educational web application and PWA designed exclusively as a quick-reference tool and measurement database."
        },
        "label.about_training_objective": {
            "es": "Tiene como objetivo apoyar en la formación de médicos generales, residentes de especialidades médicas (Medicina Interna, Anestesiología, Urgencias, Cuidado Crítico) y estudiantes durante la adquisición de competencias en ultrasonido clínico enfocado en el punto de atención (POCUS).",
            "en": "Its purpose is to support the training of general physicians, residents in medical specialties (Internal Medicine, Anesthesiology, Emergency Medicine, and Critical Care), and students as they develop competencies in focused point-of-care ultrasound (POCUS)."
        },
        "label.about_development_prefix": {
            "es": "Esta aplicación fue desarrollada y revisada por médicos internistas del",
            "en": "This application was developed and reviewed by internal medicine physicians at"
        },
        "label.about_development_course": {
            "es": "para el curso de POCUS del",
            "en": "for the POCUS course in the"
        },
        "label.about_internal_medicine_program": {
            "es": "Posgrado de Medicina Interna de la Universidad de Costa Rica (UCR)",
            "en": "Internal Medicine Residency Program at the University of Costa Rica (UCR)"
        },
        "label.about_source_prefix": {
            "es": "Toda la información médica está compilada de manera estricta del documento fuente oficial",
            "en": "All medical information has been compiled strictly from the official source document"
    },
        "label.about_source_suffix": {
            "es": "revisado en Julio de 2026, sin alteraciones de los rangos o unidades.",
            "en": "revised in July 2026, without altering any ranges or units."
        }
    }

    assert len(new_keys) == 7

    for key, val in new_keys.items():
        assert key in translations, f"Missing translation key: {key}"
        assert translations[key]["es"] == val["es"]
        assert translations[key]["en"] == val["en"]
        assert isinstance(translations[key]["es"], str) and translations[key]["es"].strip() != ""
        assert isinstance(translations[key]["en"], str) and translations[key]["en"].strip() != ""


def test_router_render_about_e1c():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    body = get_function_body(content, "renderAbout")
    assert body is not None, "Function renderAbout body not found"

    # 1. escapeHTML defined locally
    assert "const escapeHTML =" in body

    # 2. Uses all 7 keys
    keys = [
        "label.about_app_description",
        "label.about_training_objective",
        "label.about_development_prefix",
        "label.about_development_course",
        "label.about_internal_medicine_program",
        "label.about_source_prefix",
        "label.about_source_suffix"
    ]
    for key in keys:
        assert key in body

    # 3. Uses I18n.translate("app.name")
    assert 'I18n.translate("app.name")' in body

    # 4. Uses I18n.translate("label.about_title")
    assert 'I18n.translate("label.about_title")' in body

    # 5. Escapes the translated text
    assert 'escapeHTML(I18n.translate("label.about_title"))' in body

    # 6. Checks tags structure
    assert '<strong>${escapeHTML(I18n.translate("app.name"))}</strong>' in body
    assert '<strong>Hospital San Rafael de Alajuela (HSRA)</strong>' in body
    assert '<strong>${escapeHTML(I18n.translate("label.about_internal_medicine_program"))}</strong>' in body
    assert '<em>Mediciones POCUS Cardiaco Adultos - Glosario</em>' in body

    # 7. No raw Spanish paragraphs pre-existing in router.js
    removed_phrases = [
        "es una aplicación web y PWA educativa, diseñada exclusivamente como una herramienta de consulta rápida y banco de mediciones.",
        "Tiene como objetivo apoyar en la formación de médicos generales",
        "Esta aplicación fue desarrollada y revisada por médicos internistas del",
        "Toda la información médica está compilada de manera estricta del documento fuente oficial"
    ]
    for phrase in removed_phrases:
        assert phrase not in body

    # 8. No manual language switch ternaries in renderAbout
    assert "I18n.getLanguage()" not in body


def test_clinical_brand_and_terms_preservation_e1c():
    path = "assets/js/router.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    body = get_function_body(content, "renderAbout")
    assert body is not None

    # Exact invariant strings in renderAbout HTML
    assert "Hospital San Rafael de Alajuela (HSRA)" in body
    assert "Mediciones POCUS Cardiaco Adultos - Glosario" in body
    assert "POCUS" in body
    assert 'I18n.translate("label.about_internal_medicine_program")' in body

    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)["translations"]

    program = translations["label.about_internal_medicine_program"]

    assert "UCR" in program["es"]
    assert "UCR" in program["en"]
    assert "Universidad de Costa Rica" in program["es"]
    assert "University of Costa Rica" in program["en"]


def test_cache_config_e1c():
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c" in content
    assert "./assets/js/router.js" in content
    assert "./data/translations.json" in content


def test_protection_minset_measurements_e1c():
    # Verify min set, measurements, protocols, classifications etc. are unmodified
    with open("data/minimum_pocus_set.json", "r", encoding="utf-8") as f:
        min_set = json.load(f)
    assert len(min_set) == 10

    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101

    with open("data/protocols.json", "r", encoding="utf-8") as f:
        protocols = json.load(f)["protocols"]
    assert len(protocols) == 1
    assert protocols[0]["id"] == "rush"

    # E1B Keys Verification
    with open("data/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)["translations"]

    assert translations["label.cutoff_point"]["es"] == "Punto de corte"
    assert translations["label.cutoff_point"]["en"] == "Cutoff value"
    assert translations["label.abbreviations_list_title"]["es"] == "Lista de abreviaturas"
    assert translations["label.abbreviations_list_title"]["en"] == "Abbreviations"
    assert translations["app.name"]["es"] == "LOCUS POCUS"
    assert translations["app.name"]["en"] == "LOCUS POCUS"
