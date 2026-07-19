import json
import pytest

# Pruebas de lógica clínica específicas para evitar regresiones de valores numéricos del PDF
def test_rvp_formula_logic():
    # La fórmula de RVP debe estar sustentada en el VTI del TSVD y no en el TSVI
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
        
    rvp_meas = next((m for m in measurements if m["id"] == "rvp_ecografica"), None)
    assert rvp_meas is not None, "La medición 'rvp_ecografica' (Resistencia Vascular Pulmonar) no existe"
    
    formula = rvp_meas["formula_or_method"].lower()
    
    # Debe mencionar VTI del TSVD o VTI TSVD o TSVD
    assert "tsvd" in formula or "vti_tsvd" in formula or "vti del tsvd" in formula
    # NO debe mencionar TSVI
    assert "tsvi" not in formula, "Error crítico: La fórmula de RVP menciona incorrectamente el TSVI en lugar del TSVD"

def test_tapse_values():
    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
        
    tapse = next((m for m in measurements if m["id"] == "tapse_meas"), None)
    assert tapse is not None, "El parámetro TAPSE no existe"
    
    normal_values = tapse["normal_values"].lower()
    # Debe especificar que es anormal si es menor a 17 mm (o 1.7 cm)
    assert "17" in normal_values or "1.7" in normal_values

def test_fevi_ranges():
    with open("data/classifications.json", "r", encoding="utf-8") as f:
        classifications = json.load(f)
        
    fevi_class = next((c for c in classifications if "fevi" in c["name"].lower() or "eyección" in c["name"].lower()), None)
    assert fevi_class is not None, "La clasificación de FEVI no existe"
    
    # Verificar los valores límites exactos
    severa_found = False
    for item in fevi_class["items"]:
        if "sever" in item["category"].lower():
            assert "30" in item["range"], "La disfunción severa de FEVI debe ser < 30%"
            severa_found = True
            
    assert severa_found

def test_stenosis_thresholds():
    with open("data/classifications.json", "r", encoding="utf-8") as f:
        classifications = json.load(f)
        
    aortic = next((c for c in classifications if "aórtica" in c["name"].lower()), None)
    assert aortic is not None, "La clasificación de estenosis aórtica no existe"
    
    # Validar valores límites de estenosis aórtica severa
    for item in aortic["items"]:
        param = item["parameter"].lower()
        val = item["threshold"].lower()
        if "vmax" in param:
            assert "4" in val
        elif "gradiente" in param:
            assert "40" in val
        elif "ava" in param:
            assert "1,0" in val or "1.0" in val
