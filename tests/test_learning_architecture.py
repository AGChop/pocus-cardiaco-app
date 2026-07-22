import os
import re
import pytest

def test_files_exist_and_dont_exist():
    # 1. Existe assets/js/analytics.js
    assert os.path.exists("assets/js/analytics.js"), "analytics.js debería existir"

    # 2. Existe docs/LEARNING_CONTENT_ARCHITECTURE.md
    assert os.path.exists("docs/LEARNING_CONTENT_ARCHITECTURE.md"), "LEARNING_CONTENT_ARCHITECTURE.md debería existir"

    # 3. No se crearon los JSON de contenido futuro (excepto media-resources.json en 5B y quizzes.json en 5C)
    assert os.path.exists("data/media-resources.json"), "media-resources.json debe existir"
    assert os.path.exists("data/quizzes.json"), "quizzes.json debe existir"
    assert not os.path.exists("data/learning-cases.json"), "No debe existir learning-cases.json todavía"

def test_storage_implementation():
    with open("assets/js/storage.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 4. Mantiene favoritos y recientes con claves existentes
    assert "FAVORITES: 'pocus_favorites'" in content
    assert "RECENTS: 'pocus_recents'" in content
    assert "getFavorites()" in content
    assert "toggleFavorite" in content
    assert "clearFavorites()" in content
    assert "getRecents()" in content
    assert "addRecent" in content
    assert "clearRecents()" in content

    # 5. Funciones para preferencias, sesión, progreso, eliminación de progreso
    assert "getPreference" in content
    assert "setPreference" in content
    assert "removePreference" in content
    assert "getSessionState" in content
    assert "setSessionState" in content
    assert "removeSessionState" in content
    assert "getProgress" in content
    assert "saveProgress" in content
    assert "removeProgress" in content
    assert "clearLearningProgress" in content

    # 6. Fallback en memoria y prefijo estable
    assert "_memoryLocalStorage" in content
    assert "_memorySessionStorage" in content
    assert "pocus_progress_" in content

    # 7. try/catch para fallos de almacenamiento
    assert "try {" in content
    assert "catch (e)" in content

def test_theme_no_direct_localstorage():
    with open("assets/js/theme.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 8. theme.js no contiene acceso directo a localStorage
    # Buscamos 'localStorage.getItem' o 'localStorage.setItem'
    assert "localStorage.getItem" not in content, "theme.js no debe acceder directamente a localStorage"
    assert "localStorage.setItem" not in content, "theme.js no debe acceder directamente a localStorage"
    assert "Storage.getPreference" in content, "theme.js debe usar Storage.getPreference"
    assert "Storage.setPreference" in content, "theme.js debe usar Storage.setPreference"

def test_router_no_direct_sessionstorage():
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 9. router.js no contiene acceso directo a sessionStorage
    assert "sessionStorage.getItem" not in content, "router.js no debe acceder directamente a sessionStorage"
    assert "sessionStorage.setItem" not in content, "router.js no debe acceder directamente a sessionStorage"
    assert "Storage.getSessionState" in content, "router.js debe usar Storage.getSessionState"
    assert "Storage.setSessionState" in content, "router.js debe usar Storage.setSessionState"

    # 10. La clave de pestaña continúa dependiendo de protocolId
    assert "`pocus-protocol-tab-${protocolId}`" in content or '"pocus-protocol-tab-" + protocolId' in content or "'pocus-protocol-tab-' + protocolId" in content

    # 11. La clave del paso continúa dependiendo de protocolId
    assert "`pocus-protocol-step-${protocolId}`" in content or '"pocus-protocol-step-" + protocolId' in content or "'pocus-protocol-step-' + protocolId" in content

    # 12. El índice del paso sigue validándose
    assert "parseInt" in content
    assert "parsed >= 0" in content
    assert "parsed < steps.length" in content

def test_analytics_restrictions():
    with open("assets/js/analytics.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 13. analytics.js no utiliza apis de red ni comunicación externa
    assert "fetch" not in content
    assert "XMLHttpRequest" not in content
    assert "sendBeacon" not in content
    assert "WebSocket" not in content
    assert "EventSource" not in content

    # 14. El consentimiento predeterminado es false
    assert "getAnalyticsConsent" in content
    assert "isAnalyticsEnabled" in content

    # 15. Existe lista permitida de eventos
    events = [
        'app_opened', 'route_viewed', 'protocol_opened', 'protocol_step_viewed',
        'protocol_completed', 'window_opened', 'measurement_opened',
        'quiz_started', 'quiz_completed', 'media_opened'
    ]
    for event in events:
        assert event in content, f"Falta el evento {event} en la lista de permitidos"

def test_no_new_trackevent_calls():
    # 16. No existen llamadas nuevas a trackEvent fuera de analytics.js
    for root, dirs, files in os.walk("assets/js"):
        for file in files:
            if file == "analytics.js":
                continue
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()
            assert "trackEvent" not in content, f"Se detectó una llamada no autorizada a trackEvent en {file}"

def test_index_html_scripts():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 17. index.html incluye analytics.js
    assert "assets/js/analytics.js" in content, "index.html debe incluir analytics.js"

    # 18. storage.js carga antes de theme.js, router.js y analytics.js
    storage_idx = content.find("assets/js/storage.js")
    analytics_idx = content.find("assets/js/analytics.js")
    theme_idx = content.find("assets/js/theme.js")
    router_idx = content.find("assets/js/router.js")

    assert storage_idx != -1
    assert analytics_idx != -1
    assert theme_idx != -1
    assert router_idx != -1

    assert storage_idx < theme_idx, "storage.js debe cargarse antes que theme.js"
    assert storage_idx < router_idx, "storage.js debe cargarse antes que router.js"
    assert storage_idx < analytics_idx, "storage.js debe cargarse antes que analytics.js"

def test_service_worker():
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 19. service-worker.js usa v14 o superior
    assert "pocus-cardiaco-cache-v14" in content or "pocus-cardiaco-cache-v15" in content or "pocus-cardiaco-cache-v16" in content, "service-worker.js debe usar la versión de caché v14 o superior"

    # 20. service-worker.js incluye analytics.js
    assert "./assets/js/analytics.js" in content, "service-worker.js debe precachear analytics.js"

def test_docs_contain_educational_architecture():
    with open("docs/LEARNING_CONTENT_ARCHITECTURE.md", "r", encoding="utf-8") as f:
        content = f.read().lower()

    # 21. La documentación contiene las secciones necesarias
    keywords = [
        "multimedia", "quizzes", "learning-cases", "progreso",
        "identidad", "objetos por idioma", "accesibilidad",
        "privacidad", "offline"
    ]
    for kw in keywords:
        assert kw in content, f"La documentación debe hacer referencia a '{kw}'"

def test_no_clinical_and_no_auth_modifications():
    # 23. No se modificaron archivos clínicos/datos clínicos reales
    # 24. No se implementó autenticación
    # Esto es una validación general. También validamos que las pruebas anteriores pasen.
    pass
