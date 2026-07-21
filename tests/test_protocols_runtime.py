import json
import os
import hashlib
import subprocess
import pytest

@pytest.fixture
def protocols_final():
    path = "data/protocols.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def protocols_draft():
    path = "data/protocols.draft.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def windows_data():
    path = "data/windows.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def measurements_data():
    path = "data/measurements.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_final_metadata_and_disclaimer(protocols_final):
    # 1. data/protocols.json existe (ya verificado por fixture)
    # 2. Es JSON válido (ya cargado por fixture)

    # 3. status raíz es "approved-for-app-use"
    assert protocols_final["status"] == "approved-for-app-use"

    # 4. version raíz es "1.0.0"
    assert protocols_final["version"] == "1.0.0"

    # 5. approved_on es "2026-07-21"
    assert protocols_final["approved_on"] == "2026-07-21"

    # 6. source es "data/protocols.draft.json"
    assert protocols_final["source"] == "data/protocols.draft.json"

    # 7. educational_disclaimer existe y no está vacío
    assert "educational_disclaimer" in protocols_final
    assert len(protocols_final["educational_disclaimer"].strip()) > 0

def test_final_protocol_structure(protocols_final):
    # 8. Existe exactamente un protocolo
    assert len(protocols_final["protocols"]) == 1
    # 9. El protocolo es rush
    assert protocols_final["protocols"][0]["id"] == "rush"

    # 10. Existen exactamente tres componentes
    components = protocols_final["protocols"][0]["components"]
    assert len(components) == 3
    # 11. Sus IDs son pump, tank y pipes
    comp_ids = [c["id"] for c in components]
    assert comp_ids == ["pump", "tank", "pipes"]

    # 12. pump.name_es es "La Bomba (Evaluación cardíaca)"
    pump_comp = next(c for c in components if c["id"] == "pump")
    assert pump_comp["name_es"] == "La Bomba (Evaluación cardíaca)"

def test_draft_final_matching(protocols_final, protocols_draft):
    # 13. References del archivo final coinciden con las del draft
    assert protocols_final["references"] == protocols_draft["references"]

    # 14. Protocols del archivo final coinciden con los del draft
    assert protocols_final["protocols"] == protocols_draft["protocols"]

    # 14.1 El review_status del protocolo RUSH debe conservarse como "pending-clinical-review"
    assert protocols_final["protocols"][0]["review_status"] == "pending-clinical-review"

def test_linked_ids_integrity(protocols_final, windows_data, measurements_data):
    # 15. Todos los IDs vinculados siguen siendo válidos
    valid_window_ids = {w["id"] for w in windows_data}
    valid_measurement_ids = {m["id"] for m in measurements_data}

    for comp in protocols_final["protocols"][0]["components"]:
        for w_id in comp["linked_window_ids"]:
            assert w_id in valid_window_ids
        for m_id in comp["linked_measurement_ids"]:
            assert m_id in valid_measurement_ids

    # 16. Pipes conserva listas vacías sin IDs inventados cuando no existen datos vasculares vinculables
    pipes_comp = next(c for c in protocols_final["protocols"][0]["components"] if c["id"] == "pipes")
    assert pipes_comp["linked_window_ids"] == []
    assert pipes_comp["linked_measurement_ids"] == []

def test_absence_of_fictitious_elements(protocols_final):
    # 17. No existe Referencia_RUSH_Editor.pdf
    # 18. No existen source_document ni source_page ficticios
    json_str = json.dumps(protocols_final)
    assert "Referencia_RUSH_Editor.pdf" not in json_str
    assert "source_document" not in protocols_final["protocols"][0]
    assert "source_page" not in protocols_final["protocols"][0]
    for comp in protocols_final["protocols"][0]["components"]:
        assert "source_document" not in comp
        assert "source_page" not in comp

def test_reference_correctness(protocols_final):
    perera_ref = next(r for r in protocols_final["references"] if r["id"] == "ref_perera_2010")
    # 19. Se conserva PMID 19945597
    assert perera_ref["pmid"] == "19945597"
    # 20. Se conserva DOI 10.1016/j.emc.2009.09.010
    assert perera_ref["doi"] == "10.1016/j.emc.2009.09.010"
    # 21. La cita de Perera contiene "28(1):29-56, vii"
    assert "28(1):29-56, vii" in perera_ref["citation"]

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def test_promotion_script_and_sources_integrity():
    draft_path = "data/protocols.draft.json"
    windows_path = "data/windows.json"
    measurements_path = "data/measurements.json"
    output_path = "data/protocols.json"

    # Guardar hashes antes
    # 23. data/protocols.draft.json no se modifica
    draft_hash_before = get_file_hash(draft_path)
    # 24. data/windows.json no se modifica
    win_hash_before = get_file_hash(windows_path)
    # 25. data/measurements.json no se modifica
    meas_hash_before = get_file_hash(measurements_path)

    # Hash del output final antes
    final_hash_before = get_file_hash(output_path) if os.path.exists(output_path) else None

    # 22. El script de promoción es reproducible
    result = subprocess.run([".venv/bin/python", "scripts/promote_protocols.py"], capture_output=True, text=True)
    assert result.returncode == 0

    # Hash del output final después
    final_hash_after = get_file_hash(output_path)
    if final_hash_before:
        assert final_hash_before == final_hash_after, "El script de promoción no es reproducible byte a byte"

    # Verificar que los orígenes siguen intactos
    assert draft_hash_before == get_file_hash(draft_path)
    assert win_hash_before == get_file_hash(windows_path)
    assert meas_hash_before == get_file_hash(measurements_path)
