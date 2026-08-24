import json
import os
import sys
import hashlib
import subprocess
import pytest

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

def test_json_is_valid(protocols_draft):
    # 1. El JSON es válido
    assert isinstance(protocols_draft, dict)
    assert "metadata" in protocols_draft
    assert "references" in protocols_draft
    assert "protocols" in protocols_draft

def test_exactly_two_protocols_rush_and_fate(protocols_draft):
    # 2. Existen exactamente dos protocolos
    assert len(protocols_draft["protocols"]) == 2
    # 3. Sus IDs son rush y fate
    ids = [p["id"] for p in protocols_draft["protocols"]]
    assert "rush" in ids
    assert "fate" in ids

def test_protocol_components_ids(protocols_draft):
    rush = next(p for p in protocols_draft["protocols"] if p["id"] == "rush")
    assert "components" in rush
    assert len(rush["components"]) == 3
    rush_comp_ids = [c["id"] for c in rush["components"]]
    assert rush_comp_ids == ["pump", "tank", "pipes"]

    fate = next(p for p in protocols_draft["protocols"] if p["id"] == "fate")
    assert "components" in fate
    assert len(fate["components"]) == 4
    fate_comp_ids = [c["id"] for c in fate["components"]]
    assert fate_comp_ids == ["subcostal_4c", "apical_4c", "parasternal", "pleural"]

def test_no_duplicate_ids(protocols_draft):
    # 6. No hay IDs duplicados en componentes o referencias
    for protocol in protocols_draft["protocols"]:
        comp_ids = [c["id"] for c in protocol["components"]]
        assert len(comp_ids) == len(set(comp_ids))

    ref_ids = [r["id"] for r in protocols_draft["references"]]
    assert len(ref_ids) == len(set(ref_ids))

def test_all_used_references_exist(protocols_draft):
    # 7. Todas las referencias utilizadas existen
    ref_ids = {r["id"] for r in protocols_draft["references"]}

    for protocol in protocols_draft["protocols"]:
        for ref_id in protocol.get("reference_ids", []):
            assert ref_id in ref_ids

        # Referencias de cada componente
        for comp in protocol["components"]:
            for ref_id in comp.get("reference_ids", []):
                assert ref_id in ref_ids

def test_linked_window_ids_exist(protocols_draft, windows_data):
    # 8. Todos los linked_window_ids existen en windows.json
    valid_window_ids = {w["id"] for w in windows_data}
    for protocol in protocols_draft["protocols"]:
        for comp in protocol["components"]:
            for w_id in comp["linked_window_ids"]:
                assert w_id in valid_window_ids

def test_linked_measurement_ids_exist(protocols_draft, measurements_data):
    # 9. Todos los linked_measurement_ids existen en measurements.json
    valid_measurement_ids = {m["id"] for m in measurements_data}
    for protocol in protocols_draft["protocols"]:
        for comp in protocol["components"]:
            for m_id in comp["linked_measurement_ids"]:
                assert m_id in valid_measurement_ids

def test_no_fictitious_references_or_metadata(protocols_draft):
    # 10. No existe el texto Referencia_RUSH_Editor.pdf
    # 11. No existen source_document ni source_page ficticios
    json_str = json.dumps(protocols_draft)
    assert "Referencia_RUSH_Editor.pdf" not in json_str

    for protocol in protocols_draft["protocols"]:
        assert "source_document" not in protocol
        assert "source_page" not in protocol
        for comp in protocol["components"]:
            assert "source_document" not in comp
            assert "source_page" not in comp

def test_required_fields_exist(protocols_draft):
    # 12. Existe disclaimer
    assert "disclaimer" in protocols_draft["metadata"]
    # 13-15. Campos requeridos en todos los protocolos y componentes
    for protocol in protocols_draft["protocols"]:
        assert "limitations" in protocol
        assert "safety_and_workflow_notes" in protocol
        for comp in protocol["components"]:
            assert "interpretation_limits" in comp

def test_clinical_corrections_validation(protocols_draft):
    json_str = json.dumps(protocols_draft)

    # 1. pump.name_es es “La Bomba (Evaluación cardíaca)”
    rush = next(p for p in protocols_draft["protocols"] if p["id"] == "rush")
    pump_comp = next(c for c in rush["components"] if c["id"] == "pump")
    assert pump_comp["name_es"] == "La Bomba (Evaluación cardíaca)"

    # 2. No existe el texto “El Bombo”
    assert "El Bombo" not in json_str

    # 3. No existe la expresión “FEVI normal visualmente estimulada”
    assert "FEVI normal visualmente estimulada" not in json_str

    # 4. No existe la frase absoluta “Todo procedimiento invasivo”
    assert "Todo procedimiento invasivo" not in json_str

    # 5. La cita de Perera contiene “28(1):29-56, vii”
    perera_ref = next(r for r in protocols_draft["references"] if r["id"] == "ref_perera_2010")
    assert "28(1):29-56, vii" in perera_ref["citation"]

    # 6. Se conservan PMID 19945597 y DOI 10.1016/j.emc.2009.09.010
    assert perera_ref["pmid"] == "19945597"
    assert perera_ref["doi"] == "10.1016/j.emc.2009.09.010"

    # 7. Pipes puede tener listas vinculadas vacías sin inventar IDs
    pipes_comp = next(c for c in rush["components"] if c["id"] == "pipes")
    assert pipes_comp["linked_window_ids"] == []
    assert pipes_comp["linked_measurement_ids"] == []

def test_status_is_pending_clinical_review(protocols_draft):
    # 16. El status es pending-clinical-review
    assert protocols_draft["metadata"]["status"] == "pending-clinical-review"
    for protocol in protocols_draft["protocols"]:
        if protocol["id"] == "rush":
            assert protocol["review_status"] == "approved-for-app-use"
        elif protocol["id"] == "fate":
            assert protocol["review_status"] == "pending-clinical-review"

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def test_script_reproducibility_and_non_modification():
    windows_path = "data/windows.json"
    measurements_path = "data/measurements.json"
    draft_path = "data/protocols.draft.json"

    # Guardar hashes actuales de los archivos de datos para verificar que no cambian
    win_hash_before = get_file_hash(windows_path)
    meas_hash_before = get_file_hash(measurements_path)

    # Generar hash de protocols.draft.json antes de correr el script
    draft_hash_before = get_file_hash(draft_path) if os.path.exists(draft_path) else None

    # 17. El script es reproducible: Ejecutar scripts/build_protocols_draft.py usando el python del venv
    result = subprocess.run([sys.executable, "scripts/build_protocols_draft.py"], capture_output=True, text=True)
    assert result.returncode == 0, f"Error al ejecutar script: {result.stderr}"

    # Generar hash de protocols.draft.json después
    draft_hash_after = get_file_hash(draft_path)

    # Si existía antes, debe ser idéntico (reproducibilidad)
    if draft_hash_before:
        assert draft_hash_before == draft_hash_after, "El script de generación no es reproducible o produce outputs distintos en ejecuciones sucesivas"

    # 18. data/windows.json no se modifica
    win_hash_after = get_file_hash(windows_path)
    assert win_hash_before == win_hash_after, "El script modificó data/windows.json"

    # 19. data/measurements.json no se modifica
    meas_hash_after = get_file_hash(measurements_path)
    assert meas_hash_before == meas_hash_after, "El script modificó data/measurements.json"
