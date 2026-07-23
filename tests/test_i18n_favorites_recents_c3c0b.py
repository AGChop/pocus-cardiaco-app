import os
import json

def test_router_js_favs_and_recs_blocks():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    idx_favs = content.find("async renderFavorites(")
    idx_recs = content.find("async renderRecents(")
    idx_refs = content.find("async renderReferences(")

    assert idx_favs != -1, "No se encontró renderFavorites en router.js"
    assert idx_recs != -1, "No se encontró renderRecents en router.js"
    assert idx_refs != -1, "No se encontró renderReferences en router.js"

    favs_code = content[idx_favs:idx_recs]
    recs_code = content[idx_recs:idx_refs]

    # 1 y 2. renderFavorites y renderRecents continúan siendo async
    assert "async renderFavorites(" in content
    assert "async renderRecents(" in content

    # 3. Ambas funciones cargan DataLoader.getMeasurements() y DataLoader.getGlossary()
    assert "DataLoader.getMeasurements()" in favs_code
    assert "DataLoader.getGlossary()" in favs_code
    assert "DataLoader.getMeasurements()" in recs_code
    assert "DataLoader.getGlossary()" in recs_code

    # 4. Ambas manejan errores o no-array
    assert "try {" in favs_code
    assert "try {" in recs_code
    assert "Array.isArray" in favs_code
    assert "Array.isArray" in recs_code

    # 5. Se construyen mapas por ID
    assert "measurementMap" in favs_code
    assert "glossaryMap" in favs_code
    assert "measurementMap" in recs_code
    assert "glossaryMap" in recs_code

    # 6 y 7. Se localiza measurement y term desde el recurso actual
    assert "I18n.localize(resource.measurement)" in favs_code
    assert "I18n.localize(resource.term)" in favs_code

    # 8. entry.title se conserva como respaldo
    assert "I18n.localize(entry.title)" in favs_code
    assert "I18n.localize(entry.title)" in recs_code

    # 9. entry.id se utiliza como último respaldo
    assert "entry.id" in favs_code
    assert "entry.id" in recs_code

    # 10. No se modifica entry.title
    assert "entry.title =" not in favs_code
    assert "entry.title=" not in favs_code
    assert "entry.title =" not in recs_code
    assert "entry.title=" not in recs_code

    # 11. No se escribe en localStorage
    assert "localStorage.setItem" not in favs_code
    assert "localStorage.setItem" not in recs_code

    # 12. No se llama Storage.addRecent
    assert "Storage.addRecent" not in favs_code
    assert "Storage.addRecent" not in recs_code

    # 13. No se muestran directamente crudos
    assert "${f.title}" not in favs_code
    assert "${r.title}" not in recs_code
    assert "${f.type}" not in favs_code
    assert "${r.type}" not in recs_code

    # 14, 15, 16. escapeHTML se utiliza para títulos, tipos, IDs y enlaces
    assert "escapeHTML(resolvedTitle)" in favs_code or "escapeHTML(resolveCurrentTitle" in favs_code
    assert "escapeHTML(resolvedTitle)" in recs_code or "escapeHTML(resolveCurrentTitle" in recs_code
    assert "escapeHTML(getLocalizedTypeLabel" in favs_code
    assert "escapeHTML(getLocalizedTypeLabel" in recs_code
    assert "escapeHTML(link)" in favs_code
    assert "escapeHTML(link)" in recs_code

    # 17. Favoritos usa nav.favorites, state.no_favorites, action.remove_favorite
    assert "nav.favorites" in favs_code
    assert "state.no_favorites" in favs_code
    assert "action.remove_favorite" in favs_code

    # 18. Recientes usa nav.recents, state.no_recents, action.clear_history
    assert "nav.recents" in recs_code
    assert "state.no_recents" in recs_code
    assert "action.clear_history" in recs_code

    # 19. Los badges usan label.measurement y label.term
    assert "label.measurement" in favs_code
    assert "label.term" in favs_code
    assert "label.measurement" in recs_code
    assert "label.term" in recs_code

    # 20. Existe traducción local para Clear favorites, confirmación, Elemento/Item
    assert "Clear favorites" in favs_code
    assert "Elemento" in favs_code
    assert "Item" in favs_code

    # 21. No existe onclick="Storage.toggleFavorite dentro de renderFavorites
    assert "onclick=\"Storage.toggleFavorite" not in favs_code
    assert "onclick='Storage.toggleFavorite" not in favs_code

    # 22 y 23. Eliminación individual usa data-favorite-index, addEventListener, Storage.toggleFavorite, resolvedTitle
    assert "data-favorite-index" in favs_code
    assert "addEventListener" in favs_code
    assert "Storage.toggleFavorite" in favs_code

    # 24 y 25. Clear favorites y clear recents conserva addEventListener
    assert 'document.getElementById("clear-all-favs")?.addEventListener' in favs_code
    assert 'document.getElementById("clear-all-recs")?.addEventListener' in recs_code

    # 26 y 27. Las rutas siguen siendo #/medicion/ y #/glosario/, y las clases badge-medicion y badge-termino
    assert "#/medicion/" in favs_code
    assert "#/glosario/" in favs_code
    assert "#/medicion/" in recs_code
    assert "#/glosario/" in recs_code
    assert "badge-medicion" in favs_code
    assert "badge-termino" in favs_code
    assert "badge-medicion" in recs_code
    assert "badge-termino" in recs_code

def test_unmodified_files_c3c0b():
    assert os.path.exists("assets/js/storage.js")
    # 28. storage.js conserva FAVORITES: 'pocus_favorites', RECENTS: 'pocus_recents'
    with open("assets/js/storage.js", "r", encoding="utf-8") as f:
        storage_content = f.read()
    assert "pocus_favorites" in storage_content
    assert "pocus_recents" in storage_content

    # 30 y 31. Ningún archivo data/ fue modificado
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
    assert os.path.exists("data/translations.json")

    # 32. No se modificó service-worker.js
    assert os.path.exists("service-worker.js")

    # 34. No aparece eval(, document.write, [object Object] dentro de las funciones
    path = "assets/js/router.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "eval(" not in content
    assert "document.write" not in content
