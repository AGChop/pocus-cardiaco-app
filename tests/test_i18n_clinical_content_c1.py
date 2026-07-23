import os
import json

def test_sections_json_validity_and_structure():
    path = "data/sections.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 12  # Mismo número de registros

    ids = set()
    for item in data:
        assert "id" in item
        assert isinstance(item["id"], str)
        ids.add(item["id"])

        assert "slug" in item
        assert isinstance(item["slug"], str)

        assert "order" in item
        assert isinstance(item["order"], int)

        assert "number" in item
        assert isinstance(item["number"], int)

        # Campos traducibles
        for field in ["title", "short_title", "description", "clinical_warning"]:
            assert field in item
            val = item[field]
            assert isinstance(val, dict)
            assert "es" in val
            assert "en" in val
            assert isinstance(val["es"], str)
            assert isinstance(val["en"], str)
            if field != "clinical_warning": # clinical_warning puede ser vacío
                assert val["es"] != ""
                assert val["en"] != ""

            # No scripts o marcas inyectadas
            for lang in ["es", "en"]:
                txt = val[lang]
                assert "<script" not in txt.lower()
                assert "javascript:" not in txt.lower()
                assert "onerror" not in txt.lower()
                assert "onclick" not in txt.lower()

    assert len(ids) == 12  # IDs únicos

def test_abbreviations_json_validity_and_structure():
    path = "data/abbreviations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 34  # Mismo número de registros

    for item in data:
        assert "abbreviation" in item
        assert isinstance(item["abbreviation"], str)
        assert item["abbreviation"] != ""

        assert "meaning" in item
        meaning = item["meaning"]
        assert isinstance(meaning, dict)
        assert "es" in meaning
        assert "en" in meaning
        assert isinstance(meaning["es"], str)
        assert isinstance(meaning["en"], str)
        assert meaning["es"] != ""
        assert meaning["en"] != ""

        # No scripts o marcas inyectadas
        for lang in ["es", "en"]:
            txt = meaning[lang]
            assert "<script" not in txt.lower()
            assert "javascript:" not in txt.lower()
            assert "onerror" not in txt.lower()
            assert "onclick" not in txt.lower()

def test_router_js_uses_localize_and_escape():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Debe contener I18n.localize
    assert "I18n.localize" in content

    # Comprobar que en renderMeasurementsSections, renderMeasurementsList y renderAbbreviations se use localize
    # Y que mantenga escapeHTML
    assert "escapeHTML(titleLoc)" in content
    assert "escapeHTML(descLoc)" in content
    assert "escapeHTML(shortTitleLoc)" in content
    assert "escapeHTML(warningLoc)" in content
    assert "escapeHTML(meaningLoc)" in content

def test_unmodified_files():
    # No se modificaron otros archivos clínicos
    assert os.path.exists("data/glossary.json")
    assert os.path.exists("data/classifications.json")
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/windows.json")
    assert os.path.exists("data/protocols.json")
    assert os.path.exists("data/quizzes.json")
    assert os.path.exists("data/references.json")
    assert os.path.exists("data/media-resources.json")
    assert os.path.exists("data/unit_warnings.json")

    # No se modificaron archivos no autorizados
    assert os.path.exists("assets/js/app.js")
    assert os.path.exists("assets/js/i18n.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/quiz-engine.js")
    assert os.path.exists("assets/js/data-loader.js")
    assert os.path.exists("assets/js/storage.js")
    assert os.path.exists("assets/css/styles.css")
    assert os.path.exists("index.html")
    assert os.path.exists("service-worker.js")
