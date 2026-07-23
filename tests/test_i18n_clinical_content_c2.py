import os
import json
import re

def test_glossary_json_validity_and_bilingual():
    path = "data/glossary.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 106  # Mismo número de registros

    ids = set()
    for item in data:
        assert "id" in item
        assert isinstance(item["id"], str)
        ids.add(item["id"])

        # Campos traducibles
        for field in ["category", "term", "definition", "acquisition_utility_limitation"]:
            assert field in item
            val = item[field]
            assert isinstance(val, dict)
            assert "es" in val
            assert "en" in val
            assert isinstance(val["es"], str)
            assert isinstance(val["en"], str)
            assert val["es"] != ""
            assert val["en"] != ""

            # Validar no XSS
            for lang in ["es", "en"]:
                txt = val[lang]
                assert "<script" not in txt.lower()
                assert "javascript:" not in txt.lower()
                assert "onerror" not in txt.lower()
                assert "onclick" not in txt.lower()

        # Aliases
        assert "aliases" in item
        aliases = item["aliases"]
        assert isinstance(aliases, dict)
        assert "es" in aliases
        assert "en" in aliases
        assert isinstance(aliases["es"], list)
        assert isinstance(aliases["en"], list)
        for val in aliases["es"] + aliases["en"]:
            assert isinstance(val, str)
            assert val != ""

    assert len(ids) == 106  # IDs únicos

def test_classifications_json_validity_and_bilingual():
    path = "data/classifications.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 3  # Mismo número de registros

    for item in data:
        assert "id" in item
        assert isinstance(item["id"], str)

        assert "name" in item
        assert isinstance(item["name"], dict)
        assert "es" in item["name"]
        assert "en" in item["name"]

        if "note" in item:
            assert isinstance(item["note"], dict)
            assert "es" in item["note"]
            assert "en" in item["note"]

        for subitem in item["items"]:
            if "parameter" in subitem:
                p = subitem["parameter"]
                # Puede ser string o dict bilingüe
                if isinstance(p, dict):
                    assert "es" in p
                    assert "en" in p
                else:
                    assert isinstance(p, str)

            if "category" in subitem:
                cat = subitem["category"]
                assert isinstance(cat, dict)
                assert "es" in cat
                assert "en" in cat

            if "method" in subitem:
                m = subitem["method"]
                assert isinstance(m, dict)
                assert "es" in m
                assert "en" in m

            if "threshold" in subitem:
                th = subitem["threshold"]
                if isinstance(th, dict):
                    assert "es" in th
                    assert "en" in th
                else:
                    assert isinstance(th, str)

def test_router_js_localizes_glossary_and_classifications():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Comprobamos que router localiza los campos bilingües y aliases del glosario
    assert "termLoc" in content
    assert "defLoc" in content
    assert "utilLoc" in content
    assert "catLoc" in content
    assert "activeAliases" in content
    assert "I18n.localize(term.term)" in content
    assert "getLocalizedAliases" in content

    # Comprobamos clasificaciones
    assert "nameLoc" in content
    assert "noteLoc" in content
    assert "paramLoc" in content
    assert "catLoc" in content
    assert "thresholdLoc" in content
    assert "methodLoc" in content

    # escapeHTML se usa en los campos de renderGlossaryList, renderGlossaryDetail y renderClassifications
    assert "escapeHTML(termLoc)" in content
    assert "escapeHTML(defLoc)" in content
    assert "escapeHTML(utilLoc)" in content
    assert "escapeHTML(nameLoc)" in content
    assert "escapeHTML(noteLoc)" in content

def test_unmodified_files_c2():
    # No se modificaron otros archivos JSON
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/windows.json")
    assert os.path.exists("data/protocols.json")
    assert os.path.exists("data/quizzes.json")

    # No se modificaron archivos prohibidos
    assert os.path.exists("assets/js/app.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/quiz-engine.js")
    assert os.path.exists("service-worker.js")
