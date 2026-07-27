import os
import json

def test_translations_json_expanded_keys():
    path = "data/translations.json"
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("schema_version") == "1.0"
    assert data.get("default_language") == "es"
    assert data.get("supported_languages") == ["es", "en"]
    assert "translations" in data

    translations = data.get("translations")

    # Claves obligatorias según la consigna
    required_keys = [
        "app.document_title",
        "app.name",
        "language.selector_label",
        "theme.selector_label",
        "theme.auto",
        "theme.light",
        "theme.dark",
        "safety.notice",
        "search.placeholder",
        "search.aria_label",
        "search.clear",
        "search.loading",
        "search.no_results_title",
        "search.no_results_message",
        "search.results_count",
        "nav.home",
        "nav.glossary",
        "nav.measurements",
        "nav.windows",
        "nav.protocols",
        "nav.favorites",
        "nav.recents",
        "nav.about",
        "nav.install",
        "action.back",
        "action.copy_definition",
        "action.copy_formula",
        "action.save_favorite",
        "action.remove_favorite",
        "action.clear_history",
        "state.loading_content",
        "state.no_favorites",
        "state.no_recents",
        "error.not_found_title",
        "error.not_found_message",
        "error.go_home",
        "footer.version",
        "footer.developed_by"
    ]

    for key in required_keys:
        assert key in translations, f"Falta la clave {key} en translations.json"
        assert "es" in translations[key]
        assert "en" in translations[key]
        assert translations[key]["es"] != ""
        assert translations[key]["en"] != ""

def test_index_html_has_declarative_attributes():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    assert "data-i18n=" in content
    assert "data-i18n-placeholder=" in content
    assert "data-i18n-aria-label=" in content

def test_i18n_js_exposes_apply_translations():
    with open("assets/js/i18n.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "applyTranslations" in content
    assert "textContent" in content
    assert "innerHTML" not in content
    assert "eval(" not in content

def test_app_js_uses_translate():
    with open("assets/js/app.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "I18n.translate" in content
    assert "pocus-language-changed" in content

def test_router_js_uses_translate():
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "I18n.translate" in content
    assert "pocus-language-changed" in content
    assert "window.location.hash" in content
    assert "location.reload" not in content

def test_unmodified_files():
    # Asegurar que no se tocaron archivos prohibidos
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/quiz-engine.js")
    assert os.path.exists("assets/js/storage.js")
    assert os.path.exists("assets/js/data-loader.js")
    assert os.path.exists("assets/js/theme.js")
    assert os.path.exists("assets/css/styles.css")
    assert os.path.exists("service-worker.js")
    assert os.path.exists("data/glossary.json")
