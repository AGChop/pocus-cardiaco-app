import json
import os
import shutil
import subprocess
import pytest

@pytest.fixture
def protocols_final():
    path = "data/protocols.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def protocols_draft():
    path = "data/protocols.draft.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def protocols_i18n():
    path = "data/protocols.i18n.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_i18n_catalog_properties(protocols_i18n):
    # 1. Existe data/protocols.i18n.json (ya verificado por fixture)
    # 2. Declara es como origen y en como destino
    assert protocols_i18n.get("source_language") == "es"
    assert protocols_i18n.get("target_language") == "en"

    # 3. Representación de traducciones autorizadas en catálogo
    assert "educational_disclaimer" in protocols_i18n
    # educational_disclaimer debe ser un objeto con es y en
    ed = protocols_i18n["educational_disclaimer"]
    assert isinstance(ed, dict)
    assert "es" in ed and "en" in ed
    assert ed["es"] == "Este contenido es educativo. El protocolo RUSH complementa y no sustituye la valoración clínica, la reanimación ni los estudios diagnósticos definitivos. Los hallazgos deben integrarse con el contexto clínico."
    assert ed["en"] == "This content is educational. The RUSH protocol complements and does not replace clinical assessment, resuscitation, or definitive diagnostic studies. Findings must be integrated with the clinical context."

    assert "metadata" in protocols_i18n
    assert "protocols" in protocols_i18n
    assert "rush" in protocols_i18n["protocols"]

    # Comprobación de que no haya strings literales del descargo español en el promotor
    promoter_path = "scripts/promote_protocols.py"
    with open(promoter_path, "r", encoding="utf-8") as f:
        promoter_content = f.read()
    assert "Este contenido es educativo" not in promoter_content
    assert "El protocolo RUSH complementa y no sustituye" not in promoter_content

def test_compiled_data_structure(protocols_final, protocols_draft, protocols_i18n):
    # 6. Conserva RUSH
    proto_rush = next(p for p in protocols_final["protocols"] if p["id"] == "rush")
    proto_fate = next((p for p in protocols_final["protocols"] if p["id"] == "fate"), None)

    # 7. Tiene tres componentes en orden original para RUSH
    components_rush = proto_rush["components"]
    assert len(components_rush) == 3
    assert [c["id"] for c in components_rush] == ["pump", "tank", "pipes"]

    # Si FATE está presente, tiene cuatro componentes en orden original para FATE
    if proto_fate:
        components_fate = proto_fate["components"]
        assert len(components_fate) == 4
        assert [c["id"] for c in components_fate] == ["subcostal_4c", "apical_4c", "parasternal", "pleural"]

    # 9. Los campos generales/metadatos son bilingües y no vacíos
    bilingual_fields = [
        ("educational_disclaimer", protocols_final["educational_disclaimer"]),
        ("metadata.title", protocols_final["metadata"]["title"]),
        ("metadata.scope", protocols_final["metadata"]["scope"]),
        ("metadata.intended_audience", protocols_final["metadata"]["intended_audience"]),
        ("metadata.disclaimer", protocols_final["metadata"]["disclaimer"]),
        ("rush.clinical_context", proto_rush["clinical_context"]),
        ("rush.purpose", proto_rush["purpose"]),
        ("rush.target_population", proto_rush["target_population"]),
        ("rush.prerequisites", proto_rush["prerequisites"]),
        ("rush.sequence_note", proto_rush["sequence_note"]),
        ("rush.integration", proto_rush["integration"]),
        ("rush.limitations", proto_rush["limitations"]),
        ("rush.safety_and_workflow_notes", proto_rush["safety_and_workflow_notes"]),
    ]
    if proto_fate:
        bilingual_fields.extend([
            ("fate.clinical_context", proto_fate["clinical_context"]),
            ("fate.purpose", proto_fate["purpose"]),
            ("fate.target_population", proto_fate["target_population"]),
            ("fate.prerequisites", proto_fate["prerequisites"]),
            ("fate.sequence_note", proto_fate["sequence_note"]),
            ("fate.integration", proto_fate["integration"]),
            ("fate.limitations", proto_fate["limitations"]),
            ("fate.safety_and_workflow_notes", proto_fate["safety_and_workflow_notes"])
        ])
    for name, fld in bilingual_fields:
        assert isinstance(fld, dict), f"{name} no es un dict"
        assert "es" in fld and "en" in fld
        assert fld["es"].strip() != ""
        assert fld["en"].strip() != ""

    # 10 y 11. Estructura de listas de componentes bilingües
    for proto in [p for p in [proto_rush, proto_fate] if p is not None]:
        for comp in proto["components"]:
            c_id = comp["id"]
            # interpretation_limits es dict bilingüe
            assert isinstance(comp["interpretation_limits"], dict)
            assert "es" in comp["interpretation_limits"]
            assert "en" in comp["interpretation_limits"]

            for lf in ["clinical_questions", "targets", "suggested_views", "possible_findings"]:
                lst = comp[lf]
                assert isinstance(lst, list)
                # Cada elemento es un diccionario {es, en}
                for idx, item in enumerate(lst):
                    assert isinstance(item, dict), f"Elemento {idx} de {lf} en {c_id} no es dict"
                    assert "es" in item and "en" in item
                    assert isinstance(item["es"], str)
                    assert isinstance(item["en"], str)
                    assert item["es"].strip() != ""
                    assert item["en"].strip() != ""

    # 13. El español generado coincide con el draft (excepto por educational_disclaimer que no existe en el draft)
    def extract_spanish(data):
        if isinstance(data, dict):
            if "es" in data and "en" in data:
                return extract_spanish(data["es"])
            return {k: extract_spanish(v) for k, v in data.items() if k not in ["name_en"]}
        elif isinstance(data, list):
            return [extract_spanish(item) for item in data]
        return data

    # Compare RUSH Spanish parts only
    final_rush_es = extract_spanish(proto_rush)
    draft_rush_es = extract_spanish(next(p for p in protocols_draft["protocols"] if p["id"] == "rush"))
    assert final_rush_es == draft_rush_es

    # 14. El inglés coincide con el catálogo i18n
    i18n_rush = protocols_i18n["protocols"]["rush"]
    assert protocols_final["educational_disclaimer"]["en"] == protocols_i18n["educational_disclaimer"]["en"]
    assert protocols_final["metadata"]["title"]["en"] == protocols_i18n["metadata"]["title"]
    assert protocols_final["metadata"]["scope"]["en"] == protocols_i18n["metadata"]["scope"]
    assert protocols_final["metadata"]["intended_audience"]["en"] == protocols_i18n["metadata"]["intended_audience"]
    assert protocols_final["metadata"]["disclaimer"]["en"] == protocols_i18n["metadata"]["disclaimer"]

    # Validar RUSH inglés
    assert proto_rush["clinical_context"]["en"] == i18n_rush["clinical_context"]
    assert proto_rush["purpose"]["en"] == i18n_rush["purpose"]
    assert proto_rush["target_population"]["en"] == i18n_rush["target_population"]
    assert proto_rush["prerequisites"]["en"] == i18n_rush["prerequisites"]
    assert proto_rush["sequence_note"]["en"] == i18n_rush["sequence_note"]
    assert proto_rush["integration"]["en"] == i18n_rush["integration"]
    assert proto_rush["limitations"]["en"] == i18n_rush["limitations"]
    assert proto_rush["safety_and_workflow_notes"]["en"] == i18n_rush["safety_and_workflow_notes"]

    for comp in components_rush:
        c_id = comp["id"]
        i18n_comp = i18n_rush["components"][c_id]
        assert comp["interpretation_limits"]["en"] == i18n_comp["interpretation_limits"]
        for lf in ["clinical_questions", "targets", "suggested_views", "possible_findings"]:
            for idx, item in enumerate(comp[lf]):
                assert item["en"] == i18n_comp[lf][idx]

    # Validar FATE inglés si está presente
    if proto_fate:
        i18n_fate = protocols_i18n["protocols"]["fate"]
        assert proto_fate["clinical_context"]["en"] == i18n_fate["clinical_context"]
        assert proto_fate["purpose"]["en"] == i18n_fate["purpose"]
        assert proto_fate["target_population"]["en"] == i18n_fate["target_population"]
        assert proto_fate["prerequisites"]["en"] == i18n_fate["prerequisites"]
        assert proto_fate["sequence_note"]["en"] == i18n_fate["sequence_note"]
        assert proto_fate["integration"]["en"] == i18n_fate["integration"]
        assert proto_fate["limitations"]["en"] == i18n_fate["limitations"]
        assert proto_fate["safety_and_workflow_notes"]["en"] == i18n_fate["safety_and_workflow_notes"]

        for comp in components_fate:
            c_id = comp["id"]
            i18n_comp = i18n_fate["components"][c_id]
            assert comp["interpretation_limits"]["en"] == i18n_comp["interpretation_limits"]
            for lf in ["clinical_questions", "targets", "suggested_views", "possible_findings"]:
                for idx, item in enumerate(comp[lf]):
                    assert item["en"] == i18n_comp[lf][idx]

    # 15. Invariantes
    assert protocols_final["status"] == "approved-for-app-use"
    assert protocols_final["version"] == "1.0.0"
    assert protocols_final["approved_on"] == "2026-07-21"
    assert protocols_final["source"] == "data/protocols.draft.json"
    for proto in [p for p in [proto_rush, proto_fate] if p is not None]:
        if proto["id"] == "rush":
            assert proto["review_status"] == "approved-for-app-use"
        elif proto["id"] == "fate":
            assert proto["review_status"] == "pending-clinical-review"

def test_draft_canonical_monolingual(protocols_draft):
    # 1. El borrador no contiene educational_disclaimer en el nivel superior (ausencia intencional)
    assert "educational_disclaimer" not in protocols_draft

    # 2. Los campos traducibles que sí existen en el draft continúan siendo strings monolingües
    assert isinstance(protocols_draft["metadata"]["title"], str)
    assert isinstance(protocols_draft["protocols"][0]["clinical_context"], str)
    assert isinstance(protocols_draft["protocols"][0]["components"][0]["clinical_questions"][0], str)

    # 3. El borrador permanece monolingüe y sin objetos de traducción
    json_str = json.dumps(protocols_draft)
    assert '"es":' not in json_str
    assert '"en":' not in json_str

def test_fate_exclusions_and_clean_state(protocols_draft):
    fate = next(p for p in protocols_draft["protocols"] if p["id"] == "fate")
    fate_str = json.dumps(fate).lower()
    # Assert exclusions of unwanted clinical terms
    assert "pneumothorax" not in fate_str
    assert "neumotórax" not in fate_str
    assert "a-line" not in fate_str
    assert "líneas a" not in fate_str
    assert "lung sliding" not in fate_str
    assert "deslizamiento pulmonar" not in fate_str
    assert "deslizamiento pleural" not in fate_str
    assert "derrame masivo" not in fate_str
    assert "tomografía" not in fate_str
    assert "toracocentesis" not in fate_str

    # Assert three references exist and are resoluble, and have no source_page
    ref_ids = {r["id"] for r in protocols_draft["references"]}
    for ref_id in ["jensen_2004", "via_2014", "neskovic_2018"]:
        assert ref_id in ref_ids
        ref_obj = next(r for r in protocols_draft["references"] if r["id"] == ref_id)
        assert "source_page" not in ref_obj

    # Assert correct DOI of via_2014 and absence of incorrect DOI
    via_ref = next(r for r in protocols_draft["references"] if r["id"] == "via_2014")
    assert "10.1016/j.echo.2014.05.001" in via_ref["citation"]
    assert "10.1017/j.echo" not in via_ref["citation"]

    # Jensen remains primary source for components, while Via and Neskovic support protocol level
    assert "jensen_2004" in fate["reference_ids"]
    assert "via_2014" in fate["reference_ids"]
    assert "neskovic_2018" in fate["reference_ids"]

    # Jensen is the reference for each component, but Via/Neskovic are not in components
    for comp in fate["components"]:
        assert "jensen_2004" in comp["reference_ids"]
        assert "via_2014" not in comp["reference_ids"]
        assert "neskovic_2018" not in comp["reference_ids"]

    # Coherencia biventricular del componente apical
    apical = next(c for c in fate["components"] if c["id"] == "apical_4c")
    assert "biventricular" in apical["quick_reference"]["assess"].lower()

    # Parasternal component does not make septal flattening a central alert
    parasternal = next(c for c in fate["components"] if c["id"] == "parasternal")
    assert "aplanamiento septal" not in parasternal["quick_reference"]["alerts"].lower()
    # Categorías paraesternales separadas
    assert len(parasternal["possible_findings"]) == 5
    assert "Sin alteración evidente de las dimensiones" in parasternal["possible_findings"][0]
    assert "Alteración aparente de las dimensiones" in parasternal["possible_findings"][1]
    assert "Contractilidad global aparentemente conservada" in parasternal["possible_findings"][2]
    assert "Contractilidad global aparentemente reducida" in parasternal["possible_findings"][3]
    assert "Estudio no concluyente" in parasternal["possible_findings"][4]

    # Pleural scan/component mentions bilateral scans and anatomical landmarks
    pleural = next(c for c in fate["components"] if c["id"] == "pleural")
    pleural_limits = pleural["interpretation_limits"].lower()
    assert "colecciones" in pleural_limits
    assert "loculadas" in pleural_limits
    assert "no concluyente" in pleural_limits
    # Categoría pleural "sin hallazgo evidente"
    assert "Sin hallazgo evidente de líquido pleural" in pleural["possible_findings"][3]
    # Ausencia de afirmación diagnóstica de "ausencia de derrame"
    assert "ausencia de derrame" not in pleural_limits

    # Assert no mandatory quantitative measurements
    for comp in fate["components"]:
        assert comp["linked_measurement_ids"] == []

    # Verification of references in protocols.json (should only contain RUSH reachable references)
    with open("data/protocols.json", "r", encoding="utf-8") as f:
        promoted = json.load(f)
    # FATE must be absent
    assert not any(p["id"] == "fate" for p in promoted["protocols"])
    # RUSH must be present and approved
    rush = next(p for p in promoted["protocols"] if p["id"] == "rush")
    assert rush["review_status"] == "approved-for-app-use"

    # Reachable references for RUSH
    rush_ref_ids = set(rush["reference_ids"])
    for c in rush["components"]:
        rush_ref_ids.update(c.get("reference_ids", []))

    promoted_ref_ids = {r["id"] for r in promoted["references"]}
    assert promoted_ref_ids == rush_ref_ids
    assert "via_2014" not in promoted_ref_ids
    assert "neskovic_2018" not in promoted_ref_ids

def test_promotion_script_failures():
    # 18. Verificar que el promotor detecta y falla con errores esperados
    backup_path = "data/protocols.i18n.json.bak"
    shutil.copyfile("data/protocols.i18n.json", backup_path)

    try:
        # A. Faltando educational_disclaimer completo
        with open("data/protocols.i18n.json", "r", encoding="utf-8") as f:
            mutated = json.load(f)
        del mutated["educational_disclaimer"]
        with open("data/protocols.i18n.json", "w", encoding="utf-8") as f:
            json.dump(mutated, f)
        result = subprocess.run(["python3", "scripts/promote_protocols.py"], capture_output=True, text=True)
        assert result.returncode != 0
        assert "educational_disclaimer" in result.stdout or "educational_disclaimer" in result.stderr

        # B. Faltando educational_disclaimer.en
        shutil.copyfile(backup_path, "data/protocols.i18n.json")
        with open("data/protocols.i18n.json", "r", encoding="utf-8") as f:
            mutated = json.load(f)
        del mutated["educational_disclaimer"]["en"]
        with open("data/protocols.i18n.json", "w", encoding="utf-8") as f:
            json.dump(mutated, f)
        result = subprocess.run(["python3", "scripts/promote_protocols.py"], capture_output=True, text=True)
        assert result.returncode != 0
        assert "educational_disclaimer.en" in result.stdout or "educational_disclaimer.en" in result.stderr

        # C. educational_disclaimer.es vacío
        shutil.copyfile(backup_path, "data/protocols.i18n.json")
        with open("data/protocols.i18n.json", "r", encoding="utf-8") as f:
            mutated = json.load(f)
        mutated["educational_disclaimer"]["es"] = " "
        with open("data/protocols.i18n.json", "w", encoding="utf-8") as f:
            json.dump(mutated, f)
        result = subprocess.run(["python3", "scripts/promote_protocols.py"], capture_output=True, text=True)
        assert result.returncode != 0
        assert "educational_disclaimer.es" in result.stdout or "educational_disclaimer.es" in result.stderr

        # D. Mismatch de tamaño de listas
        shutil.copyfile(backup_path, "data/protocols.i18n.json")
        with open("data/protocols.i18n.json", "r", encoding="utf-8") as f:
            mutated = json.load(f)
        mutated["protocols"]["rush"]["components"]["pump"]["clinical_questions"].pop()
        with open("data/protocols.i18n.json", "w", encoding="utf-8") as f:
            json.dump(mutated, f)
        result = subprocess.run(["python3", "scripts/promote_protocols.py"], capture_output=True, text=True)
        assert result.returncode != 0
        assert "Mismatch de tamaño" in result.stdout or "Mismatch de tamaño" in result.stderr

    finally:
        # Restaurar original
        shutil.copyfile(backup_path, "data/protocols.i18n.json")
        if os.path.exists(backup_path):
            os.remove(backup_path)


def test_exact_clinical_requirements(protocols_final, protocols_draft, protocols_i18n):
    # 1. DOI correcto de Via
    via_draft_ref = next(r for r in protocols_draft["references"] if r["id"] == "via_2014")
    assert "10.1016/j.echo.2014.05.001" in via_draft_ref["citation"]

    # 2. Ausencia del DOI incorrecto
    assert "10.1017/j.echo.2014.05.001" not in via_draft_ref["citation"]

    # 3. Coherencia biventricular del componente apical
    fate_draft = next(p for p in protocols_draft["protocols"] if p["id"] == "fate")
    apical_draft = next(c for c in fate_draft["components"] if c["id"] == "apical_4c")
    assert "biventricular" in apical_draft["quick_reference"]["assess"].lower()

    # 4. Categorías paraesternales separadas
    parasternal_draft = next(c for c in fate_draft["components"] if c["id"] == "parasternal")
    expected_findings_es = [
        "Sin alteración evidente de las dimensiones o del grosor parietal.",
        "Alteración aparente de las dimensiones o del grosor parietal.",
        "Contractilidad global aparentemente conservada.",
        "Contractilidad global aparentemente reducida.",
        "Estudio no concluyente."
    ]
    assert parasternal_draft["possible_findings"] == expected_findings_es

    # 5. Categoría pleural "sin hallazgo evidente"
    pleural_draft = next(c for c in fate_draft["components"] if c["id"] == "pleural")
    assert "Sin hallazgo evidente de líquido pleural en el hemitórax examinado." in pleural_draft["possible_findings"]

    # 6. Ausencia de afirmación diagnóstica de "ausencia de derrame"
    assert "ausencia de derrame" not in pleural_draft["interpretation_limits"].lower()

    # 7. Paridad posicional ES/EN
    i18n_fate = protocols_i18n["protocols"]["fate"]
    for comp in fate_draft["components"]:
        c_id = comp["id"]
        i18n_comp = i18n_fate["components"][c_id]
        for list_field in ["clinical_questions", "targets", "suggested_views", "possible_findings"]:
            assert len(comp[list_field]) == len(i18n_comp[list_field]), f"Mismatch size in {c_id}.{list_field}"

    # 8. Referencias alcanzables del archivo promovido
    promoted_ref_ids = {r["id"] for r in protocols_final["references"]}
    rush_final = next(p for p in protocols_final["protocols"] if p["id"] == "rush")
    expected_ref_ids = set(rush_final["reference_ids"])
    for comp in rush_final["components"]:
        expected_ref_ids.update(comp.get("reference_ids", []))
    assert promoted_ref_ids == expected_ref_ids

    # 9. FATE ausente de protocols.json
    assert not any(p["id"] == "fate" for p in protocols_final["protocols"])

    # 10. RUSH intacto
    assert any(p["id"] == "rush" for p in protocols_final["protocols"])


def test_fate_literal_corrections_and_absences(protocols_i18n):
    # Obtener el objeto de FATE en las traducciones
    fate_i18n = protocols_i18n["protocols"]["fate"]
    fate_str = json.dumps(fate_i18n)

    # Pruebas literales para las tres cadenas corregidas:
    # 1. Qualitative biventricular function assessment without mandatory quantitative measurements.
    assert "Qualitative biventricular function assessment without mandatory quantitative measurements." in fate_str

    # 2. Marked apparent alteration of relative RV dimensions or apparently reduced global biventricular contractility.
    assert "Marked apparent alteration of relative RV dimensions or apparently reduced global biventricular contractility." in fate_str

    # 3. Qualitative classification of each hemithorax as showing findings compatible with pleural fluid, no obvious finding, or an inconclusive study.
    assert "Qualitative classification of each hemithorax as showing findings compatible with pleural fluid, no obvious finding, or an inconclusive study." in fate_str

    # Pruebas para la ausencia, dentro de FATE, de:
    # - mandatory quantitative thresholds
    assert "mandatory quantitative thresholds" not in fate_str

    # - Apparent marked alteration
    assert "Apparent marked alteration" not in fate_str

    # - as finding compatible
    assert "as finding compatible" not in fate_str

    # - non-conclusive
    assert "non-conclusive" not in fate_str.lower()
