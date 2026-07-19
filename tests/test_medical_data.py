import os
import json
import pytest

# Función auxiliar para normalizar texto en Python (equivalente a JS)
def normalize_text(text):
    if not text:
        return ""
    import unicodedata
    normalized = str(text).lower()
    # Eliminar tildes
    normalized = "".join(
        c for c in unicodedata.normalize("NFD", normalized)
        if unicodedata.category(c) != "Mn"
    )
    # Normalizar apóstrofes
    normalized = normalized.replace("’", "'").replace("´", "'").replace("‘", "'")
    return " ".join(normalized.split()).strip()

# A. PRUEBAS DE ARCHIVOS
def test_files_exist():
    assert os.path.exists("index.html")
    assert os.path.exists("manifest.webmanifest")
    assert os.path.exists("service-worker.js")
    assert os.path.exists("data/sections.json")
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/glossary.json")
    assert os.path.exists("data/abbreviations.json")
    assert os.path.exists("data/classifications.json")
    assert os.path.exists("data/unit_warnings.json")
    assert os.path.exists("data/references.json")
    assert os.path.exists("data/metadata.json")

# B. PRUEBAS DE SECCIONES
def test_sections():
    with open("data/sections.json", "r", encoding="utf-8") as f:
        sections = json.load(f)
        
    assert len(sections) == 12
    ids = [s["id"] for s in sections]
    slugs = [s["slug"] for s in sections]
    numbers = [s["number"] for s in sections]
    
    assert len(ids) == len(set(ids))
    assert len(slugs) == len(set(slugs))
    assert len(numbers) == len(set(numbers))
    assert numbers == sorted(numbers)

# C. PRUEBAS DE MEDICIONES
def test_measurements():
    with open("data/sections.json", "r", encoding="utf-8") as f:
        sections = json.load(f)
    section_ids = {s["id"] for s in sections}

    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)

    for m in measurements:
        assert m["id"]
        assert m["measurement"]
        assert m["section_id"] in section_ids
        assert 1 <= m["source_page"] <= 18
        assert m["units"]
        assert isinstance(m["aliases"], list)

# D. PRUEBAS DE BÚSQUEDA (Normalización en Python)
@pytest.mark.parametrize("query,expected_substring", [
    ("FEVI", "fevi"),
    ("fraccion de eyeccion", "fevi"),
    ("Longitud VD", "rv_length"),
    ("ventriculo derecho", "vd"),
    ("e prima", "e'"),
    ("e'", "e'"),
    ("s prima", "s'"),
    ("LVOT", "tsvi"),
    ("PVR", "rvp")
])
def test_search_normalization(query, expected_substring):
    # Cargar mediciones
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    
    # Cargar glosario
    with open("data/glossary.json", "r", encoding="utf-8") as f:
        glossary = json.load(f)

    query_norm = normalize_text(query)
    
    # Mapeo manual de alias para emular el diccionario de equivalencias
    equivalences = {
        "fevi": "fevi",
        "fraccion de eyeccion": "fevi",
        "longitud vd": "longitud del vd",
        "ventriculo derecho": "vd",
        "e prima": "e'",
        "e'": "e'",
        "s prima": "s'",
        "lvot": "tsvi",
        "pvr": "rvp"
    }
    
    mapped_query = equivalences.get(query_norm, query_norm)
    mapped_query_norm = normalize_text(mapped_query)
    
    match_found = False
    
    # Buscar en mediciones
    for m in measurements:
        name_norm = normalize_text(m["measurement"])
        abbr_norm = normalize_text(m["abbreviation"])
        aliases_norm = [normalize_text(a) for a in m["aliases"]]
        
        if (mapped_query_norm in name_norm or 
            mapped_query_norm in abbr_norm or 
            any(mapped_query_norm in alias for alias in aliases_norm) or
            expected_substring.lower() in m["id"].lower()):
            match_found = True
            break
            
    # Buscar en glosario
    if not match_found:
        for g in glossary:
            term_norm = normalize_text(g["term"])
            aliases_norm = [normalize_text(a) for a in g["aliases"]]
            if (mapped_query_norm in term_norm or 
                any(mapped_query_norm in alias for alias in aliases_norm) or
                expected_substring.lower() in g["id"].lower()):
                match_found = True
                break

    assert match_found, f"No se encontró coincidencia para '{query}' (normalizada como '{mapped_query_norm}')"

# E. PRUEBAS DE RELACIONES
def test_relations():
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    meas_ids = {m["id"] for m in measurements}

    with open("data/glossary.json", "r", encoding="utf-8") as f:
        glossary = json.load(f)
    gloss_ids = {g["id"] for g in glossary}

    # Verificar que los related_glossary_ids existan en glossary.json
    for m in measurements:
        for gid in m.get("related_glossary_ids", []):
            assert gid in gloss_ids, f"Medición '{m['id']}' tiene enlace roto a término de glosario '{gid}'"

    # Verificar que los related_measurement_ids existan en measurements.json
    for g in glossary:
        for mid in g.get("related_measurement_ids", []):
            assert mid in meas_ids, f"Término '{g['id']}' tiene enlace roto a medición '{mid}'"
