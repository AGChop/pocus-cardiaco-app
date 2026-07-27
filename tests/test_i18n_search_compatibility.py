import os
import re

def test_search_js_bilingual_helper_exists():
    path = "assets/js/search.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "getSearchableText" in content
    assert "matchField" in content
    assert '"[object Object]"' not in content
    assert "eval(" not in content

def test_app_js_uses_localize_in_search():
    path = "assets/js/app.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # app.js debe utilizar I18n.localize antes de escapar campos clínicos de la tarjeta de resultados
    assert "I18n.localize(item.measurement)" in content
    assert "I18n.localize(item.formula_or_method)" in content
    assert "I18n.localize(item.normal_values)" in content
    assert "I18n.localize(item.term)" in content
    assert "I18n.localize(item.definition)" in content
    assert "I18n.localize(item.meaning)" in content
    assert "I18n.localize(item.name)" in content
    assert "I18n.localize(item.note)" in content
    assert "I18n.localize(item.window)" in content
    assert "I18n.localize(item.favored_structures)" in content
    assert "I18n.localize(item.purpose)" in content

def test_unmodified_files_checks():
    # No se modificaron archivos JSON
    assert os.path.exists("data/abbreviations.json")
    assert os.path.exists("data/sections.json")
    assert os.path.exists("data/glossary.json")
    assert os.path.exists("data/classifications.json")
    assert os.path.exists("data/measurements.json")

    # No se modificaron archivos prohibidos
    assert os.path.exists("assets/js/router.js")
    assert os.path.exists("assets/js/i18n.js")
    assert os.path.exists("assets/js/quiz-engine.js")
    assert os.path.exists("service-worker.js")
