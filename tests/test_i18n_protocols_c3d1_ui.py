import os
import json
import re
import tempfile
import subprocess
import urllib.request
import pytest
from pathlib import Path
from tests.helpers.chrome_runner import run_js_in_chrome as _run_js_in_chrome

def run_js_in_chrome(js_payload):
    try:
        return _run_js_in_chrome(
            js_payload,
            load_windows=True,
            load_measurements=True,
            timeout=20
        )
    except Exception as e:
        pytest.fail(str(e))


def test_translation_keys_structure():
    with open("data/translations.json", "r", encoding="utf-8") as f:
        t = json.load(f)["translations"]

    expected_keys = {
        "label.protocol_sections": {"es": "Secciones del protocolo", "en": "Protocol sections"},
        "label.go_to_step": {"es": "Ir al paso {step}: {title}", "en": "Go to step {step}: {title}"},
        "label.clinical_context": {"es": "Contexto clínico", "en": "Clinical context"},
        "label.target_population": {"es": "Población objetivo", "en": "Target population"},
        "label.acquisition_sequence": {"es": "Secuencia de adquisición", "en": "Acquisition sequence"},
        "label.component_with_name": {"es": "Componente: {name}", "en": "Component: {name}"},
        "label.reminder": {"es": "Recordatorio", "en": "Reminder"},
        "label.reminder_text": {
            "es": "Siempre integre los hallazgos con el contexto clínico del paciente.",
            "en": "Always integrate findings with the patient's clinical context."
        },
        "label.purpose_and_context": {"es": "Propósito y contexto", "en": "Purpose and context"}
    }

    for key, expected_val in expected_keys.items():
        assert key in t, f"Missing key: {key}"
        assert t[key]["es"] == expected_val["es"], f"Mismatch ES for {key}"
        assert t[key]["en"] == expected_val["en"], f"Mismatch EN for {key}"

def test_router_static_analysis():
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    banned_substrings = [
        "Secciones del protocolo",
        "Ir al paso",
        "Contexto clínico",
        "Población objetivo",
        "Secuencia de adquisición",
        "Componente:",
        "Recordatorio:",
        "Propósito y contexto",
        "isEn ? 'Component:'",
        "isEn ? 'Clinical context:'",
        "isEn ? 'Target population:'",
        "isEn ? 'Acquisition sequence:'"
    ]

    clean_content = re.sub(r"//.*", "", content)
    clean_content = re.sub(r"/\*.*?\*/", "", clean_content, flags=re.DOTALL)

    for term in banned_substrings:
        assert term not in clean_content, f"Banned string or ternary still found in router.js: {term}"

def test_d1a_unmodified():
    assert os.path.exists("data/protocols.json")
    assert os.path.exists("data/protocols.i18n.json")
    assert os.path.exists("data/protocols.draft.json")
    assert os.path.exists("scripts/promote_protocols.py")
    assert os.path.exists("tests/test_protocols_runtime.py")
    assert os.path.exists("tests/test_i18n_protocols_c3d1_data.py")

def test_ui_localization_and_elements_headless():
    payload = """
    const container = document.getElementById("app");

    // Resolve dynamic values from actual catalogs
    const windows = await DataLoader.getWindows();
    const plaxObj = windows.find(w => w.id === "plax");

    const measurements = await DataLoader.getMeasurements();
    const feviObj = measurements.find(m => m.id === "fevi");

    // Test 1: Render in Spanish
    I18n.setLanguage("es");
    await Router.renderProtocolDetail(container, "rush");
    const htmlES = container.innerHTML;

    // Check resolveWindowLink and resolveMeasurementLink in ES
    const plaxNameES = I18n.localize(plaxObj.window, "es");
    const feviNameES = I18n.localize(feviObj.measurement, "es");
    const plaxAbbreviationES = I18n.localize(plaxObj.abbreviation, "es");
    const feviAbbreviationES = I18n.localize(feviObj.abbreviation, "es");

    const hasWindowES = htmlES.includes(plaxNameES) && htmlES.includes(plaxAbbreviationES);
    const hasMeasurementES = htmlES.includes(feviNameES) && htmlES.includes(feviAbbreviationES);

    // Check labels in ES
    const hasClinicalContextLabelES = htmlES.includes("Contexto clínico");
    const hasAriaLabelES = htmlES.includes("Secciones del protocolo");
    const hasReminderES = htmlES.includes("Siempre integre los hallazgos con el contexto clínico del paciente.");

    // Check no [object Object], undefined, null
    const noObjectObjES = !htmlES.includes("[object Object]");
    const noUndefinedES = !htmlES.includes("undefined") && !htmlES.includes("null");

    // Test 2: Switch to English
    I18n.setLanguage("en");
    await Router.renderProtocolDetail(container, "rush");
    const htmlEN = container.innerHTML;

    // Check resolveWindowLink and resolveMeasurementLink in EN
    const plaxNameEN = I18n.localize(plaxObj.window, "en");
    const feviNameEN = I18n.localize(feviObj.measurement, "en");
    const plaxAbbreviationEN = I18n.localize(plaxObj.abbreviation, "en");
    const feviAbbreviationEN = I18n.localize(feviObj.abbreviation, "en");

    const hasWindowEN = htmlEN.includes(plaxNameEN) && htmlEN.includes(plaxAbbreviationEN);
    const hasMeasurementEN = htmlEN.includes(feviNameEN) && htmlEN.includes(feviAbbreviationEN);

    // Check labels in EN
    const hasClinicalContextLabelEN = htmlEN.includes("Clinical context");
    const hasAriaLabelEN = htmlEN.includes("Protocol sections");
    const hasReminderEN = htmlEN.includes("Always integrate findings with the patient's clinical context.");

    // Check component names (Pump / La Bomba)
    const hasPumpES = htmlES.includes("La Bomba (Evaluación cardíaca)");
    const hasPumpEN = htmlEN.includes("The Pump (Cardiac Evaluation)");

    const noObjectObjEN = !htmlEN.includes("[object Object]");
    const noUndefinedEN = !htmlEN.includes("undefined") && !htmlEN.includes("null");

    // Test 3: Switch back to Spanish (es -> en -> es sequence verification)
    I18n.setLanguage("es");
    await Router.renderProtocolDetail(container, "rush");
    const htmlESAfter = container.innerHTML;
    const hasPumpESAfter = htmlESAfter.includes("La Bomba (Evaluación cardíaca)");
    const noObjectObjESAfter = !htmlESAfter.includes("[object Object]");

    return {
        hasWindowES, hasMeasurementES, hasClinicalContextLabelES, hasAriaLabelES, hasReminderES, noObjectObjES, noUndefinedES,
        hasWindowEN, hasMeasurementEN, hasClinicalContextLabelEN, hasAriaLabelEN, hasReminderEN, hasPumpES, hasPumpEN, noObjectObjEN, noUndefinedEN,
        hasPumpESAfter, noObjectObjESAfter
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]

    assert data["hasWindowES"], "Window link was not resolved or localized in Spanish"
    assert data["hasMeasurementES"], "Measurement link was not resolved or localized in Spanish"
    assert data["hasClinicalContextLabelES"], "Clinical context label was not found in Spanish"
    assert data["hasAriaLabelES"], "ARIA label was not found or translated to Spanish"
    assert data["hasReminderES"], "Reminder text was not found or translated to Spanish"
    assert data["noObjectObjES"], "HTML in Spanish contains '[object Object]'"
    assert data["noUndefinedES"], "HTML in Spanish contains undefined or null"

    assert data["hasWindowEN"], "Window link was not resolved or localized in English"
    assert data["hasMeasurementEN"], "Measurement link was not resolved or localized in English"
    assert data["hasClinicalContextLabelEN"], "Clinical context label was not found in English"
    assert data["hasAriaLabelEN"], "ARIA label was not found or translated to English"
    assert data["hasReminderEN"], "Reminder text was not found or translated to English"
    assert data["hasPumpES"], "La Bomba not found in Spanish"
    assert data["hasPumpEN"], "The Pump not found in English"
    assert data["noObjectObjEN"], "HTML in English contains '[object Object]'"
    assert data["noUndefinedEN"], "HTML in English contains undefined or null"

    assert data["hasPumpESAfter"], "Interactive guide failed to update back to Spanish name 'La Bomba'"
    assert data["noObjectObjESAfter"], "HTML after switching back to Spanish contains '[object Object]'"

def test_search_localization_and_indexing_headless():
    payload = """
    // Spanish search
    I18n.setLanguage("es");
    const resultsES = await Search.searchGlobal("La Bomba");
    const resultsDeepES = await Search.searchGlobal("tuberías");

    // English search
    I18n.setLanguage("en");
    const resultsEN = await Search.searchGlobal("The Pump");
    const resultsDeepEN = await Search.searchGlobal("Pipes");

    // Check result items content
    const matchPumpES = resultsES.some(r => r.item.id === "rush");
    const matchPumpEN = resultsEN.some(r => r.item.id === "rush");
    const matchDeepES = resultsDeepES.some(r => r.item.id === "rush");
    const matchDeepEN = resultsDeepEN.some(r => r.item.id === "rush");

    // Localize result items
    I18n.setLanguage("es");
    const nameES = I18n.localize({ es: resultsES[0].item.name_es, en: resultsES[0].item.name_en });

    I18n.setLanguage("en");
    const nameEN = I18n.localize({ es: resultsEN[0].item.name_es, en: resultsEN[0].item.name_en });

    return {
        matchPumpES,
        matchPumpEN,
        matchDeepES,
        matchDeepEN,
        nameES,
        nameEN
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]
    assert data["matchPumpES"], "Search failed to match 'La Bomba' in Spanish"
    assert data["matchPumpEN"], "Search failed to match 'The Pump' in English"
    assert data["matchDeepES"], "Search failed to match deep clinical content 'tuberías' in Spanish"
    assert data["matchDeepEN"], "Search failed to match deep clinical content 'Pipes' in English"
    assert "RUSH" in data["nameES"], "Result name in Spanish is not matching RUSH"
    assert "RUSH" in data["nameEN"], "Result name in English is not matching RUSH"

def test_bilingual_assets_and_cache_revision():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v17-c3d1" in content
    assert "./assets/js/i18n.js" in content
    assert "./data/translations.json" in content
    assert "./assets/js/router.js" in content
    assert "./assets/js/search.js" in content
    assert "./data/protocols.json" in content
