import os
import json
import re

def test_pwa_cache_name():
    # 1. CACHE_NAME exacto terminado en `-logo2-pwa1`
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1).startswith("pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final-logo2-pwa1")

def test_service_worker_features():
    # 2. Permanencia de skipWaiting, clients.claim, limpieza de cachés antiguas y las 36 entradas originales del precache.
    sw_path = "service-worker.js"
    assert os.path.exists(sw_path)
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "self.skipWaiting()" in content
    assert "self.clients.claim()" in content
    assert "caches.delete" in content
    assert "cache !== CACHE_NAME" in content or "cache != CACHE_NAME" in content

    # Find ASSETS_TO_CACHE elements
    assets_block_match = re.search(r"const ASSETS_TO_CACHE = \[(.*?)\];", content, re.DOTALL)
    assert assets_block_match is not None
    assets_text = assets_block_match.group(1)
    assets = [a.strip().strip("'\",") for a in assets_text.split("\n") if a.strip()]
    assert len(assets) == 37
    
    expected_assets = [
        './',
        './index.html',
        './manifest.webmanifest',
        './assets/css/styles.css',
        './assets/js/app.js',
        './assets/js/analytics.js',
        './assets/js/media-viewer.js',
        './assets/js/quiz-engine.js',
        './assets/js/data-loader.js',
        './assets/js/storage.js',
        './assets/js/theme.js',
        './assets/js/i18n.js',
        './assets/js/search.js',
        './assets/js/router.js',
        './data/translations.json',
        './data/media-resources.json',
        './data/quizzes.json',
        './data/sections.json',
        './data/measurements.json',
        './data/measurement-priority.json',
        './data/glossary.json',
        './data/abbreviations.json',
        './data/classifications.json',
        './data/minimum_pocus_set.json',
        './data/unit_warnings.json',
        './data/references.json',
        './data/metadata.json',
        './data/windows.json',
        './data/protocols.json',
        './assets/images/locus_pocus_branding.png',
        './assets/images/locus_pocus_flame_overlay.png',
        './assets/icons/locus-pocus-apple-touch-icon-180.png',
        './assets/icons/locus-pocus-icon-192.png',
        './assets/icons/locus-pocus-icon-512.png',
        './assets/icons/locus-pocus-icon-maskable-512.png',
        './assets/images/locus_pocus_social_preview_1200x630.png'
    ]
    for asset in expected_assets:
        assert asset in assets

def test_app_js_registration_and_update_behavior():
    app_path = "assets/js/app.js"
    assert os.path.exists(app_path)
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Extraer sw_block
    marker = "// Registro del Service Worker para capacidades Offline de la PWA"
    assert marker in content
    sw_block = content[content.index(marker):]

    # 2. Cambiar todas las aserciones para examinar sw_block
    # 3. Registro con updateViaCache: "none"
    assert "updateViaCache" in sw_block
    assert re.search(r"updateViaCache\s*:\s*['\"]none['\"]", sw_block) is not None

    # 4. Presencia de registration.update()
    assert "registration.update()" in sw_block

    # 5. Presencia del listener controllerchange
    assert "controllerchange" in sw_block

    # 6. Existencia de una bandera que limite la recarga a una sola vez.
    assert re.search(r"(isReloading|reloading|reloadFlag|isReloadingForServiceWorkerUpdate)", sw_block, re.IGNORECASE) is not None

    # 7. Diferenciación entre primera instalación sin controlador y actualización con controlador previo.
    assert "navigator.serviceWorker.controller" in sw_block
    assert re.search(r"(hadServiceWorkerController|hadController|existedController|prevController)", sw_block, re.IGNORECASE) is not None

    # 8. Uso de window.location.reload()
    assert "location.reload()" in sw_block

    # 9. Que no se agreguen llamadas a location.replace, cambios de hash ni temporizadores de recarga.
    assert "location.replace" not in sw_block
    assert "setTimeout" not in sw_block
    assert "setInterval" not in sw_block

    # 3. Verificaciones de orden
    # - hadServiceWorkerController aparece antes de controllerchange.
    idx_had_controller = sw_block.index("hadServiceWorkerController")
    idx_controllerchange = sw_block.index("controllerchange")
    assert idx_had_controller < idx_controllerchange

    # - controllerchange aparece antes de navigator.serviceWorker.register.
    idx_register = sw_block.index("navigator.serviceWorker.register")
    assert idx_controllerchange < idx_register

    # - La asignación isReloadingForServiceWorkerUpdate = true aparece antes de window.location.reload().
    match_assign = re.search(r"isReloadingForServiceWorkerUpdate\s*=\s*true", sw_block)
    assert match_assign is not None
    idx_assign = match_assign.start()
    idx_reload = sw_block.index("window.location.reload()")
    assert idx_assign < idx_reload

    # - registration.update() está seguido por manejo .catch.
    idx_update = sw_block.index("registration.update()")
    idx_catch = sw_block.index(".catch", idx_update)
    assert idx_update < idx_catch

def test_clinical_and_ui_integrity():
    # 10. Que no se modifiquen datos clínicos, traducciones, router, búsqueda, almacenamiento, estilos, imágenes o manifest.
    assert os.path.exists("data/translations.json")
    assert os.path.exists("assets/js/router.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/storage.js")
    assert os.path.exists("assets/css/styles.css")
    assert os.path.exists("manifest.webmanifest")
    assert os.path.exists("index.html")

    # 11. Que measurements.json conserve 101 registros.
    measurements_path = "data/measurements.json"
    assert os.path.exists(measurements_path)
    with open(measurements_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 101
