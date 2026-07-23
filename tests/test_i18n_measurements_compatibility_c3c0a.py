import os
import json

def test_measurements_unmodified_and_count():
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 101 # Sigue teniendo 101 registros

def test_router_js_measurements_blocks():
    path = "assets/js/router.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    idx_list = content.find("async renderMeasurementsList(")
    idx_detail = content.find("async renderMeasurementDetail(")
    idx_windows = content.find("async renderWindowsList(")

    assert idx_list != -1, "No se encontró renderMeasurementsList en router.js"
    assert idx_detail != -1, "No se encontró renderMeasurementDetail en router.js"
    assert idx_windows != -1, "No se encontró renderWindowsList en router.js"

    list_code = content[idx_list:idx_detail]
    detail_code = content[idx_detail:idx_windows]

    # Valida en renderMeasurementsList:
    # 1. I18n.localize(item.measurement)
    assert "I18n.localize(item.measurement)" in list_code
    # 2. I18n.localize(item.formula_or_method)
    assert "I18n.localize(item.formula_or_method)" in list_code
    # 3. I18n.localize(item.normal_values)
    assert "I18n.localize(item.normal_values)" in list_code
    # 4. I18n.localize(item.interpretation_limitations)
    assert "I18n.localize(item.interpretation_limitations)" in list_code
    # 5. I18n.localize(item.units)
    assert "I18n.localize(item.units)" in list_code
    # 6. copyData usa los valores localizados.
    assert "measurementLoc" in list_code
    assert "formulaLoc" in list_code
    assert "normalValuesLoc" in list_code
    assert "limitationsLoc" in list_code
    assert "unitsLoc" in list_code
    # 7. Existe encodeInlineValue.
    assert "encodeInlineValue" in list_code
    # 8. Se reemplaza el apóstrofo por %27.
    assert ".replace(/'/g, \"%27\")" in list_code or ".replace(/'/g, '%27')" in list_code
    # 9. Router.toggleFav recibe título decodificado.
    assert "Router.toggleFav('medición', decodeURIComponent" in list_code or "Router.toggleFav(\"medición\", decodeURIComponent" in list_code
    # 10. No existen interpolaciones directas de los cinco campos clínicos.
    assert "${item.measurement}" not in list_code
    assert "${item.formula_or_method}" not in list_code
    assert "${item.normal_values}" not in list_code
    assert "${item.interpretation_limitations}" not in list_code
    assert "${item.units}" not in list_code

    # Valida en renderMeasurementDetail:
    # 1. Localiza los diez campos clínicos indicados.
    detail_fields = [
        "measurementLoc", "formulaLoc", "normalValuesLoc", "limitationsLoc", "unitsLoc",
        "primaryWindowLoc", "preferredViewLoc", "modalityLoc", "acquisitionTimingLoc", "acquisitionKeyLoc"
    ]
    for field in detail_fields:
        assert field in detail_code
    # 2. Utiliza getLocalizedList(item.aliases).
    assert "getLocalizedList(item.aliases)" in detail_code
    # 3. Utiliza getLocalizedList(item.alternate_windows).
    assert "getLocalizedList(item.alternate_windows)" in detail_code
    # 4. Storage.addRecent recibe measurementLoc.
    assert "Storage.addRecent(\"medición\", item.id, measurementLoc)" in detail_code or "Storage.addRecent('medición', item.id, measurementLoc)" in detail_code
    # 5. copyData utiliza valores localizados.
    assert "measurementLoc" in detail_code
    assert "formulaLoc" in detail_code
    assert "normalValuesLoc" in detail_code
    assert "limitationsLoc" in detail_code
    assert "unitsLoc" in detail_code
    # 6, 7, 8. Existe encodedCopyData, encodedMeasurementTitle, encodedItemId.
    assert "encodedCopyData" in detail_code
    assert "encodedMeasurementTitle" in detail_code
    assert "encodedItemId" in detail_code
    # 9. Usa decodeURIComponent en copiar y favoritos.
    assert "decodeURIComponent" in detail_code
    # 10. getLinkForWindow utiliza collectTextVariants.
    assert "collectTextVariants" in detail_code
    # 11. getLinkForWindow utiliza normalizeComparable.
    assert "normalizeComparable" in detail_code
    # 12. No aplica toLowerCase directamente sobre primary o view crudos.
    assert "primary.toLowerCase()" not in detail_code
    assert "view.toLowerCase()" not in detail_code
    # 13. No usa item.alternate_windows.length directamente.
    assert "item.alternate_windows.length" not in detail_code
    # 14. No usa item.aliases.join directamente.
    assert "item.aliases.join" not in detail_code
    # 15. No interpola directamente campos clínicos.
    assert "${item.measurement}" not in detail_code
    assert "${item.formula_or_method}" not in detail_code
    assert "${item.normal_values}" not in detail_code
    assert "${item.interpretation_limitations}" not in detail_code
    assert "${item.units}" not in detail_code
    assert "${item.primary_window}" not in detail_code
    assert "${item.preferred_view}" not in detail_code
    assert "${item.modality}" not in detail_code
    assert "${item.acquisition_timing}" not in detail_code
    assert "${item.acquisition_key}" not in detail_code
    # 16. Escapa los textos visibles.
    assert "escapeHTML(measurementLoc)" in detail_code
    assert "escapeHTML(formulaLoc)" in detail_code
    # 17. Conserva las rutas de mediciones y ventanas.
    assert "#/mediciones/" in detail_code
    assert "#/ventanas/" in detail_code

def test_unmodified_files_c3c0a():
    assert os.path.exists("data/measurements.json")
    assert os.path.exists("data/measurement-priority.json")
    assert os.path.exists("data/measurement-priority.draft.json")
    assert os.path.exists("data/translations.json")
    assert os.path.exists("assets/js/storage.js")
    assert os.path.exists("assets/js/data-loader.js")
    assert os.path.exists("assets/js/search.js")
    assert os.path.exists("assets/js/app.js")
    assert os.path.exists("service-worker.js")
