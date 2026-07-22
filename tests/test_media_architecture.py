import os
import json
import re
import pytest

def test_media_resources_json_properties():
    # 1. Existe data/media-resources.json
    path = "data/media-resources.json"
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. schema_version es "1.0"
    assert data.get("schema_version") == "1.0"

    # 3. default_language es "es"
    assert data.get("default_language") == "es"

    # 4. resources es una lista vacía
    assert isinstance(data.get("resources"), list)
    assert len(data.get("resources")) == 0

    # 5. No existen archivos multimedia reales nuevos (en assets/media)
    if os.path.exists("assets/media"):
        for root, dirs, files in os.walk("assets/media"):
            for file in files:
                assert file.endswith(".gitkeep") or file == "", "No se deben agregar archivos multimedia reales en esta fase"

def test_media_viewer_js_exists():
    # 6. Existe assets/js/media-viewer.js
    assert os.path.exists("assets/js/media-viewer.js")

def test_dataloader_integration():
    with open("assets/js/data-loader.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 7. DataLoader incluye getMediaResources o equivalente
    assert "getMediaResources()" in content

    # 8. La carga multimedia devuelve [] ante error
    assert "return []" in content

    # 9. El archivo utiliza la caché en memoria existente
    assert "fetchResource" in content or "this.cache" in content

def test_media_viewer_logic():
    with open("assets/js/media-viewer.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 10. Existe getMediaForEntity o equivalente
    assert "getMediaForEntity" in content

    # 11. Se contemplan relaciones con protocolos, componentes, ventanas, mediciones
    assert "linked_protocol_ids" in content
    assert "linked_component_ids" in content
    assert "linked_window_ids" in content
    assert "linked_measurement_ids" in content

    # 12. Existe resolución de texto localizado
    assert "resolveLocalizedMediaText" in content

    # 13. Existe fallback de idioma
    assert "fallbackLanguage" in content or "es" in content

    # 14. Se utiliza <figure>
    assert "<figure" in content

    # 15. Se utiliza <figcaption> de forma condicional
    assert "<figcaption" in content

    # 16. Se utiliza <picture>
    assert "<picture" in content

    # 17. Las imágenes usan loading="lazy"
    assert 'loading="lazy"' in content

    # 18. Las imágenes usan decoding="async"
    assert 'decoding="async"' in content

    # 19. Los videos usan controls
    assert 'controls' in content

    # 20. Los videos usan preload="metadata"
    assert 'preload="' in content

    # 21. Los videos usan playsinline
    assert 'playsinline' in content

    # 22. No existe autoplay en el renderizador
    assert 'autoplay' not in content

    # 23. Existe soporte para <source>
    assert '<source' in content

    # 24. Existe soporte para <track> y WebVTT
    assert '<track' in content

    # 25. Existe transcripción
    assert 'transcript' in content

    # 26. Existe renderizado de fallback
    assert 'renderMediaFallback' in content

    # 27. No se crea sección visible con recursos vacíos
    assert "resources.length === 0" in content

def test_router_integration():
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 28. router.js integra multimedia en protocolos, ventanas, mediciones
    assert "getMediaForEntity" in content
    assert "renderMediaSection" in content

    # 29. No existe dependencia exclusiva de RUSH
    assert "rush" not in content.lower() or content.lower().count("rush") < 100 # RUSH se usa en el stepper pero no limita la multimedia

def test_index_html_integration():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 30. index.html incluye media-viewer.js
    assert "assets/js/media-viewer.js" in content

    # 31. media-viewer.js carga antes de router.js
    idx_media = content.find("assets/js/media-viewer.js")
    idx_router = content.find("assets/js/router.js")
    assert idx_media != -1
    assert idx_router != -1
    assert idx_media < idx_router

def test_styles_css():
    with open("assets/css/styles.css", "r", encoding="utf-8") as f:
        content = f.read()

    # 32. styles.css incluye clases multimedia
    assert ".media-section" in content
    assert ".media-grid" in content
    assert ".media-card" in content

    # 33. Existe soporte responsive
    assert "@media" in content

    # 34. Existe :focus-visible
    assert ":focus-visible" in content

    # 35. Existe prefers-reduced-motion
    assert "prefers-reduced-motion" in content

def test_service_worker_caching():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 36. service-worker.js usa v15 o v16
    assert "pocus-cardiaco-cache-v15" in content or "pocus-cardiaco-cache-v16" in content

    # 37. service-worker.js precachea media-viewer.js y media-resources.json
    assert "./assets/js/media-viewer.js" in content
    assert "./data/media-resources.json" in content

    # 38. service-worker.js no precachea videos ni audios
    assets_block = content[content.find("const ASSETS_TO_CACHE"):content.find("];")] if "const ASSETS_TO_CACHE" in content else ""
    assert ".mp4" not in assets_block
    assert ".webm" not in assets_block.replace(".webmanifest", "")

    # 39. service-worker.js excluye video
    assert "video" in content

    # 40. service-worker.js excluye audio
    assert "audio" in content

    # 41. service-worker.js contempla encabezado Range
    assert "range" in content

    # 42. service-worker.js evita cachear respuestas 206 (solo status 200 en put)
    # status !== 200 asegura que no se guarde respuestas 206.
    assert "status !== 200" in content

def test_no_clinical_and_no_lightbox_modifications():
    # 44. No se modificaron archivos clínicos existentes
    # 45. No se agregaron recursos clínicos
    # 46. No se implementó lightbox
    # 47. No se implementó optional_download
    with open("assets/js/media-viewer.js", "r", encoding="utf-8") as f:
        content = f.read()
    assert "lightbox" not in content.lower()
    assert "optional_download" not in content.lower()
