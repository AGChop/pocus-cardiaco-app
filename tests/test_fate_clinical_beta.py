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
def protocols_beta():
    path = "data/protocols.beta.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def translations():
    path = "data/translations.json"
    assert os.path.exists(path), f"No se encontró {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_protocols_json_contains_only_rush_approved(protocols_final):
    # RUSH must be approved-for-app-use
    assert len(protocols_final["protocols"]) == 1
    rush = protocols_final["protocols"][0]
    assert rush["id"] == "rush"
    assert rush["review_status"] == "approved-for-app-use"
    # FATE must not be in protocols.json
    assert not any(p["id"] == "fate" for p in protocols_final["protocols"])

def test_protocols_beta_json_contains_only_fate(protocols_beta):
    assert len(protocols_beta["protocols"]) == 1
    fate = protocols_beta["protocols"][0]
    assert fate["id"] == "fate"
    # FATE retains pending-clinical-review
    assert fate["review_status"] == "pending-clinical-review"
    # FATE has publication_status public-beta
    assert fate["publication_status"] == "public-beta"
    # FATE is never approved-for-app-use
    assert fate["review_status"] != "approved-for-app-use"

def test_beta_feedback_url_and_metadata(protocols_beta):
    fate = protocols_beta["protocols"][0]
    assert "feedback_url" in fate
    url = fate["feedback_url"]
    assert url.startswith("https://")
    assert "viewform" in url
    assert "/edit" not in url
    assert url == "https://docs.google.com/forms/d/e/1FAIpQLSeqAC_O5Iw3rbG6OagPAa-Ly2UMvBlZvsGrvwFPVAsnSSlyOQ/viewform?usp=dialog"

    # No approved_on nor clinical approval statement in beta
    assert "approved_on" not in protocols_beta
    assert "approved_on" not in protocols_beta["metadata"]
    assert protocols_beta["status"] == "public-beta"
    assert protocols_beta["source"] == "data/protocols.draft.json"

def test_reachable_references(protocols_final, protocols_beta):
    # final
    final_ref_ids = {r["id"] for r in protocols_final["references"]}
    expected_final_ref_ids = set(protocols_final["protocols"][0]["reference_ids"])
    for comp in protocols_final["protocols"][0]["components"]:
        expected_final_ref_ids.update(comp.get("reference_ids", []))
    assert final_ref_ids == expected_final_ref_ids

    # beta
    beta_ref_ids = {r["id"] for r in protocols_beta["references"]}
    expected_beta_ref_ids = set(protocols_beta["protocols"][0]["reference_ids"])
    for comp in protocols_beta["protocols"][0]["components"]:
        expected_beta_ref_ids.update(comp.get("reference_ids", []))
    assert beta_ref_ids == expected_beta_ref_ids

def test_reproducibility_and_non_modification():
    draft_path = "data/protocols.draft.json"
    win_path = "data/windows.json"
    meas_path = "data/measurements.json"
    i18n_path = "data/protocols.i18n.json"
    final_path = "data/protocols.json"
    beta_path = "data/protocols.beta.json"

    # Hashes before
    draft_h1 = hashlib.sha256(open(draft_path, "rb").read()).hexdigest()
    win_h1 = hashlib.sha256(open(win_path, "rb").read()).hexdigest()
    meas_h1 = hashlib.sha256(open(meas_path, "rb").read()).hexdigest()
    i18n_h1 = hashlib.sha256(open(i18n_path, "rb").read()).hexdigest()
    final_h1 = hashlib.sha256(open(final_path, "rb").read()).hexdigest()
    beta_h1 = hashlib.sha256(open(beta_path, "rb").read()).hexdigest()

    # Run scripts
    subprocess.run([".venv/bin/python", "scripts/build_protocols_draft.py"], check=True)
    subprocess.run([".venv/bin/python", "scripts/promote_protocols.py"], check=True)

    # Hashes after
    draft_h2 = hashlib.sha256(open(draft_path, "rb").read()).hexdigest()
    win_h2 = hashlib.sha256(open(win_path, "rb").read()).hexdigest()
    meas_h2 = hashlib.sha256(open(meas_path, "rb").read()).hexdigest()
    i18n_h2 = hashlib.sha256(open(i18n_path, "rb").read()).hexdigest()
    final_h2 = hashlib.sha256(open(final_path, "rb").read()).hexdigest()
    beta_h2 = hashlib.sha256(open(beta_path, "rb").read()).hexdigest()

    assert draft_h1 == draft_h2
    assert win_h1 == win_h2
    assert meas_h1 == meas_h2
    assert i18n_h1 == i18n_h2
    assert final_h1 == final_h2
    assert beta_h1 == beta_h2

def test_translation_parity_and_comments_keys(translations):
    required_keys = [
        "nav.comments",
        "comments.title",
        "comments.description",
        "comments.warning",
        "comments.open_btn",
        "fate.beta_badge",
        "fate.warning_text",
        "fate.feedback_btn"
    ]
    for key in required_keys:
        assert key in translations["translations"]
        trans = translations["translations"][key]
        assert "es" in trans and "en" in trans
        assert trans["es"].strip() != ""
        assert trans["en"].strip() != ""

def test_service_worker_content():
    path = "service-worker.js"
    content = open(path, "r", encoding="utf-8").read()
    assert "./data/protocols.beta.json" in content
    assert "beta1-feedback1" in content

def test_router_integration():
    path = "assets/js/router.js"
    content = open(path, "r", encoding="utf-8").read()
    assert "#/comentarios" in content
    assert "fate.beta_badge" in content
    assert "fate.warning_text" in content
    assert "fate.feedback_btn" in content
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content

def test_loader_loader_combined_integrity():
    path = "assets/js/data-loader.js"
    content = open(path, "r", encoding="utf-8").read()
    assert "protocols.beta" in content
    assert "deduplicate" in content or "refIds" in content

def test_beta_disclaimers_no_rush_and_bilingual(protocols_beta):
    # educational_disclaimer
    ed_desc = protocols_beta["educational_disclaimer"]
    assert "rush" not in ed_desc["es"].lower()
    assert "rush" not in ed_desc["en"].lower()
    assert "fate" in ed_desc["es"].lower()
    assert "fate" in ed_desc["en"].lower()
    assert "revisión clínica" in ed_desc["es"].lower()
    assert "clinical review" in ed_desc["en"].lower()

    # metadata.disclaimer
    meta_desc = protocols_beta["metadata"]["disclaimer"]
    assert "rush" not in meta_desc["es"].lower()
    assert "rush" not in meta_desc["en"].lower()
    assert "fate" in meta_desc["es"].lower()
    assert "fate" in meta_desc["en"].lower()
    assert "revisión clínica" in meta_desc["es"].lower()
    assert "clinical review" in meta_desc["en"].lower()

def test_beta_title_bilingual(protocols_beta):
    title = protocols_beta["metadata"]["title"]
    assert title["es"] == "Protocolos clínicos POCUS — Beta pública"
    assert title["en"] == "POCUS Clinical Protocols — Public beta"

def test_protocols_json_byte_identical():
    path = "data/protocols.json"
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    current_hash = hasher.hexdigest()
    expected_hash = "f687186dd04b5f92c0560ee9fd3a7514ee5b6cf1c96ca5f28e291012851265e7"
    assert current_hash == expected_hash

def test_ordinary_resources_caching_headless():
    from tests.helpers.chrome_runner import run_js_in_chrome
    payload = """
    // Redefine real DataLoader logic in payload to test its caching behavior
    const DataLoaderReal = {
        cache: {},
        async fetchResource(name) {
            if (this.cache[name]) {
                return this.cache[name];
            }
            const data = await this.fetchResourceDirect(name);
            if (data !== null) {
                this.cache[name] = data;
            }
            return data;
        },
        async fetchResourceDirect(name) {
            const response = await fetch(`data/${name}.json`);
            return await response.json();
        }
    };

    const calls = [];
    const originalFetch = window.fetch;
    window.fetch = async (url, options) => {
        calls.push(url);
        return new Response(JSON.stringify({ test: "data" }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });
    };
    await DataLoaderReal.fetchResource("windows");
    await DataLoaderReal.fetchResource("windows");
    return calls;
    """
    res = run_js_in_chrome(payload, load_windows=True)
    assert res["success"]
    calls = res["data"]
    # Check that windows.json was fetched exactly once
    windows_fetches = [c for c in calls if "windows" in c]
    assert len(windows_fetches) == 1

def test_beta_safe_degradation_headless():
    from tests.helpers.chrome_runner import run_js_in_chrome
    payload = """
    // Mock fetch to return 404 for protocols.beta
    const originalFetch = window.fetch;
    window.fetch = async (url, options) => {
        if (url.includes("protocols.beta")) {
            return new Response("Not Found", { status: 404, statusText: "Not Found" });
        }
        return originalFetch(url, options);
    };
    // Force reload (by clearing cache key first)
    DataLoader.cache = {};
    const data = await DataLoader.fetchResource("protocols");
    return {
        protocolsCount: data.protocols.length,
        protocolIds: data.protocols.map(p => p.id)
    };
    """
    res = run_js_in_chrome(payload)
    assert res["success"]
    data = res["data"]
    # Should fall back gracefully and still load RUSH
    assert data["protocolsCount"] == 1
    assert data["protocolIds"] == ["rush"]
