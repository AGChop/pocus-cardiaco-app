import os
import json
import re

def test_i18n_files_exist():
    assert os.path.exists("assets/js/i18n.js")
    assert os.path.exists("data/translations.json")

def test_translations_json_validity():
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("schema_version") == "1.0"
    assert data.get("default_language") == "es"
    assert data.get("supported_languages") == ["es", "en"]
    assert "translations" in data

    translations = data.get("translations")
    for key in ["language.selector_label", "language.spanish", "language.english"]:
        assert key in translations
        assert "es" in translations[key]
        assert "en" in translations[key]
        assert translations[key]["es"] != ""
        assert translations[key]["en"] != ""

def test_index_html_language_select():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Debe contener select con id exacto
    assert 'id="language-select"' in content
    # Selector con opciones es y en
    assert 'value="es"' in content
    assert 'value="en"' in content
    # Debe poseer etiqueta accesible (label o aria-label)
    assert 'aria-label=' in content or '<label' in content
    # Debe cargar i18n.js
    assert 'src="assets/js/i18n.js"' in content

def test_storage_language_methods():
    with open("assets/js/storage.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus_language" in content
    assert "getLanguage" in content
    assert "setLanguage" in content
    assert "es" in content
    assert "en" in content

def test_i18n_js_implementation():
    with open("assets/js/i18n.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Debe actualizar document.documentElement.lang
    assert "document.documentElement.lang" in content
    # Debe emitir el CustomEvent pocus-language-changed
    assert "pocus-language-changed" in content
    assert "CustomEvent" in content
    assert "detail" in content
    assert "language" in content

    # Debe contener lógica de fallback a español ('es')
    assert "'es'" in content or '"es"' in content

    # Seguridad: no debe usar eval ni innerHTML
    assert "eval(" not in content
    assert "innerHTML" not in content

def test_dataloader_translations_integration():
    with open("assets/js/data-loader.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "getTranslations" in content
    assert "translations" in content

def test_app_js_initialization_order():
    with open("assets/js/app.js", "r", encoding="utf-8") as f:
        content = f.read()

    # app.js inicializa I18n después de cargar el DOM (DOMContentLoaded)
    assert "I18n.init()" in content
    # El selector de idioma llama a setLanguage al cambiar
    assert "languageSelect.addEventListener" in content
    assert "setLanguage" in content

def test_technical_ids_unmodified():
    # Asegurarnos de que no hayamos modificado IDs técnicos en otros archivos
    assert os.path.exists("data/windows.json")
    with open("data/windows.json", "r", encoding="utf-8") as f:
        windows = json.load(f)
    for window in windows:
        assert window["id"] in ["plax", "psax", "a4c", "rv_focused_a4c", "a2c", "a3c", "a5c", "subcostal_4c", "subcostal_ivc", "rv_inflow", "right_parasternal", "suprasternal"]
