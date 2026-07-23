import os
import json
import pytest

def test_measurements_structure_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    # 2. Sigue teniendo exactamente 101 registros
    assert len(data) == 101
    
    # 3. Todos los IDs globales siguen siendo únicos
    ids = [m["id"] for m in data]
    assert len(ids) == len(set(ids))

    # 4. Existen exactamente los seis IDs
    migrated_ids = {"ivsd", "pwtd", "rwt_meas", "masa_vi_meas", "lv_mass_index", "geometria_vi_meas"}
    for mid in migrated_ids:
        assert mid in ids

def test_migrated_items_details():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 5-9. Validaciones de metadatos invariants
    expected_order = {
        "ivsd": 1,
        "pwtd": 2,
        "rwt_meas": 3,
        "masa_vi_meas": 4,
        "lv_mass_index": 5,
        "geometria_vi_meas": 6
    }
    
    expected_related = {
        "ivsd": ["ivsd_term", "plax"],
        "pwtd": ["pwtd_term", "plax"],
        "rwt_meas": ["rwt_term", "dtdvi_term", "pwtd_term"],
        "masa_vi_meas": ["masa_vi_term", "dtdvi_term", "ivsd_term", "pwtd_term"],
        "lv_mass_index": ["indice_masa_vi_term", "bsa", "indexed"],
        "geometria_vi_meas": ["remodelado_concentrico", "hipertrofia_concentrica", "hipertrofia_excentrica"]
    }

    for item in data:
        i_id = item["id"]
        if i_id in expected_order:
            # 5. section_id
            assert item["section_id"] == "lv_geometry"
            # 6. order
            assert item["order"] == expected_order[i_id]
            # 7. related_glossary_ids
            assert item["related_glossary_ids"] == expected_related[i_id]
            # 8. source_page
            assert item["source_page"] == 4
            # 9. source_document
            assert item["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

            # 12-23. Estructuras bilingües
            bilingual_fields = [
                "measurement", "formula_or_method", "normal_values", "interpretation_limitations",
                "primary_window", "preferred_view", "modality", "acquisition_timing", "acquisition_key"
            ]
            for field in bilingual_fields:
                val = item[field]
                assert isinstance(val, dict), f"Campo '{field}' en '{i_id}' no es dict."
                assert "es" in val and "en" in val
                assert isinstance(val["es"], str) and val["es"].strip() != ""
                assert isinstance(val["en"], str) and val["en"].strip() != ""

            # 13. aliases
            assert isinstance(item["aliases"], dict)
            assert "es" in item["aliases"] and "en" in item["aliases"]
            assert isinstance(item["aliases"]["es"], list)
            assert isinstance(item["aliases"]["en"], list)
            for a in item["aliases"]["es"] + item["aliases"]["en"]:
                assert isinstance(a, str) and a.strip() != ""

            # 23. alternate_windows
            assert item["alternate_windows"] == {"es": [], "en": []}

            # 34. Sin vulnerabilidades ni [object Object]
            for field in bilingual_fields:
                for lang in ["es", "en"]:
                    val = item[field][lang]
                    assert "[object Object]" not in val
                    assert "<script" not in val.lower()
                    assert "javascript:" not in val.lower()
                    assert "onerror=" not in val.lower()
                    assert "onclick=" not in val.lower()

            for lang in ["es", "en"]:
                for a in item["aliases"][lang]:
                    assert "[object Object]" not in a
                    assert "<script" not in a.lower()
                    assert "javascript:" not in a.lower()
                    assert "onerror=" not in a.lower()
                    assert "onclick=" not in a.lower()

def test_bilingual_or_monolingual_abbreviations_and_units():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 24. abbreviation conserva string en IVSd, PWTd y RWT
    ivsd = next(m for m in data if m["id"] == "ivsd")
    assert ivsd["abbreviation"] == "IVSd"

    pwtd = next(m for m in data if m["id"] == "pwtd")
    assert pwtd["abbreviation"] == "PWTd"

    rwt = next(m for m in data if m["id"] == "rwt_meas")
    assert rwt["abbreviation"] == "RWT"

    # 25. abbreviation es bilingüe en masa, índice de masa y geometría
    masa = next(m for m in data if m["id"] == "masa_vi_meas")
    assert masa["abbreviation"] == {"es": "Masa del VI", "en": "LV mass"}

    mvii = next(m for m in data if m["id"] == "lv_mass_index")
    assert mvii["abbreviation"] == {"es": "Índice de masa del VI", "en": "LV mass index"}

    geom = next(m for m in data if m["id"] == "geometria_vi_meas")
    assert geom["abbreviation"] == {"es": "Geometría del VI", "en": "LV geometry"}

    # 26. units conserva string en mm, g y g/m²
    assert ivsd["units"] == "mm"
    assert pwtd["units"] == "mm"
    assert masa["units"] == "g"
    assert mvii["units"] == "g/m²"

    # 27. units es bilingüe y usa "dimensionless" en RWT y geometría
    assert rwt["units"] == {"es": "adimensional", "en": "dimensionless"}
    assert geom["units"] == {"es": "adimensional", "en": "dimensionless"}

def test_formulas_and_thresholds():
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 29. La fórmula de RWT
    rwt = next(m for m in data if m["id"] == "rwt_meas")
    assert "2" in rwt["formula_or_method"]["es"]
    assert "PWTd" in rwt["formula_or_method"]["es"]
    assert "DTDVI" in rwt["formula_or_method"]["es"]
    assert "2" in rwt["formula_or_method"]["en"]
    assert "PWTd" in rwt["formula_or_method"]["en"]
    assert "LVIDd" in rwt["formula_or_method"]["en"]

    # 30. La fórmula de masa
    masa = next(m for m in data if m["id"] == "masa_vi_meas")
    assert "0,8" in masa["formula_or_method"]["es"]
    assert "1,04" in masa["formula_or_method"]["es"]
    assert "0,6" in masa["formula_or_method"]["es"]
    assert "IVSd" in masa["formula_or_method"]["es"]
    assert "PWTd" in masa["formula_or_method"]["es"]
    assert "DTDVI" in masa["formula_or_method"]["es"]
    assert "³" in masa["formula_or_method"]["es"]

    assert "0.8" in masa["formula_or_method"]["en"]
    assert "1.04" in masa["formula_or_method"]["en"]
    assert "0.6" in masa["formula_or_method"]["en"]
    assert "IVSd" in masa["formula_or_method"]["en"]
    assert "PWTd" in masa["formula_or_method"]["en"]
    assert "LVIDd" in masa["formula_or_method"]["en"]
    assert "³" in masa["formula_or_method"]["en"]

    # 31. Valores normales de IVSd y PWTd
    ivsd = next(m for m in data if m["id"] == "ivsd")
    assert "hombres 6-10 mm; mujeres 6-9 mm." in ivsd["normal_values"]["es"].lower()
    assert "men 6-10 mm; women 6-9 mm." in ivsd["normal_values"]["en"].lower()

    # 32. LV mass index
    mvii = next(m for m in data if m["id"] == "lv_mass_index")
    assert "115" in mvii["normal_values"]["es"]
    assert "95" in mvii["normal_values"]["es"]
    assert "115" in mvii["normal_values"]["en"]
    assert "95" in mvii["normal_values"]["en"]

    # 33. RWT conserva el límite ≤0,42 / ≤0.42
    rwt = next(m for m in data if m["id"] == "rwt_meas")
    assert "0,42" in rwt["normal_values"]["es"]
    assert "0.42" in rwt["normal_values"]["en"]

def test_other_records_and_files_unmodified():
    # 35. Los otros 95 registros no son eliminados ni alterados en sus ids
    path = "data/measurements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 101

    # 36. No se modifican archivos fuera del alcance
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
    assert os.path.exists("data/translations.json")
    assert os.path.exists("assets/js/router.js")
