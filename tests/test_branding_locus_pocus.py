import os
import json
import re
import pytest

def get_png_dimensions(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "rb") as f:
        data = f.read(24)
    # Check PNG signature
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"File is not a valid PNG: {filepath}"
    # Extract dimensions (Width at bytes 16-20, Height at bytes 20-24)
    width = int.from_bytes(data[16:20], byteorder="big")
    height = int.from_bytes(data[20:24], byteorder="big")
    return width, height

def test_png_dimensions():
    # A. Existencia y dimensiones mediante lectura directa del encabezado PNG
    images_config = {
        "assets/images/locus_pocus_branding.png": (1024, 1024),
        "assets/images/locus_pocus_social_preview_1200x630.png": (1200, 630),
        "assets/icons/locus-pocus-icon-192.png": (192, 192),
        "assets/icons/locus-pocus-icon-512.png": (512, 512),
        "assets/icons/locus-pocus-icon-maskable-512.png": (512, 512),
        "assets/icons/locus-pocus-apple-touch-icon-180.png": (180, 180)
    }

    for filepath, expected_size in images_config.items():
        w, h = get_png_dimensions(filepath)
        assert (w, h) == expected_size, f"Mismatch in dimensions for {filepath}. Expected {expected_size}, got ({w}, {h})"

def test_index_html_branding():
    # B. index.html uses new assets and metadata/title
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    assert "assets/images/locus_pocus_branding.png" in content
    assert "assets/images/locus_pocus_social_preview_1200x630.png" in content
    assert "./assets/icons/locus-pocus-icon-192.png" in content
    assert "./assets/icons/locus-pocus-apple-touch-icon-180.png" in content

    # Title, metadata, footer contains LOCUS POCUS
    assert "<title data-i18n=\"app.document_title\">LOCUS POCUS - Glosario y Mediciones</title>" in content
    assert 'content="LOCUS POCUS"' in content
    assert "&copy; 2026 LOCUS POCUS. Versión Inicial Mínima." in content

    # No exact visible branding strings
    assert "POCUS Cardíaco" not in content
    assert "Cardiac POCUS" not in content

def test_translations_locus_pocus():
    # C. translations.json contains exact translations
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    t = data["translations"]

    assert t["app.document_title"]["es"] == "LOCUS POCUS - Glosario y Mediciones"
    assert t["app.document_title"]["en"] == "LOCUS POCUS - Glossary and Measurements"

    assert t["app.name"]["es"] == "LOCUS POCUS"
    assert t["app.name"]["en"] == "LOCUS POCUS"

    assert t["footer.version"]["es"] == "© 2026 LOCUS POCUS. Versión Inicial Mínima."
    assert t["footer.version"]["en"] == "© 2026 LOCUS POCUS. Initial Minimum Version."

    assert t["label.about_title"]["es"] == "Acerca de LOCUS POCUS"
    assert t["label.about_title"]["en"] == "About LOCUS POCUS"

    assert "<strong>LOCUS POCUS</strong>" in t["label.inst_iphone_step4"]["es"]
    assert "<strong>LOCUS POCUS</strong>" in t["label.inst_iphone_step4"]["en"]

    # Protocolos POCUS remains
    assert t["nav.protocols"]["es"] == "Protocolos POCUS"

def test_manifest_locus_pocus():
    # D. manifest.webmanifest app name and icon paths
    with open("manifest.webmanifest", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["name"] == "LOCUS POCUS - Glosario y banco de mediciones"
    assert manifest["short_name"] == "LOCUS POCUS"

    # Three new icon paths
    icon_srcs = [icon["src"] for icon in manifest["icons"]]
    assert "./assets/icons/locus-pocus-icon-192.png" in icon_srcs
    assert "./assets/icons/locus-pocus-icon-512.png" in icon_srcs
    assert "./assets/icons/locus-pocus-icon-maskable-512.png" in icon_srcs

def test_metadata_locus_pocus():
    # E. metadata.json title and source document
    with open("data/metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["title"] == "LOCUS POCUS - Glosario y Banco de Mediciones"
    assert meta["source_document"] == "Mediciones_POCUS_Cardiaco_Adultos_Glosario.pdf"

def test_router_locus_pocus():
    # F. router.js renderAbout
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Uses App name localization in renderAbout
    assert '${I18n.translate("app.name")}</strong> es una aplicación' in content
    assert "<strong>POCUS Cardíaco</strong>" not in content
    # Source document intact
    assert "Mediciones POCUS Cardiaco Adultos - Glosario" in content

def test_service_worker_locus_pocus():
    # G. service-worker.js
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Cache name
    assert "pocus-cardiaco-cache-v17-c3d1-brand1" in content

    # New assets in cache
    assert "./assets/images/locus_pocus_branding.png" in content
    assert "./assets/images/locus_pocus_social_preview_1200x630.png" in content
    assert "./assets/icons/locus-pocus-apple-touch-icon-180.png" in content
    assert "./assets/icons/locus-pocus-icon-192.png" in content
    assert "./assets/icons/locus-pocus-icon-512.png" in content
    assert "./assets/icons/locus-pocus-icon-maskable-512.png" in content

    # Essentail assets remain
    assert "./assets/js/i18n.js" in content
    assert "./data/translations.json" in content

    # Old assets removed from caching array
    assert "./assets/images/pocus_fusion_branding.png" not in content
    assert "./assets/icons/apple-touch-icon-180.png" not in content
    assert "./assets/icons/icon-192.png" not in content
    assert "./assets/icons/icon-512.png" not in content
    assert "./assets/icons/icon-maskable-512.png" not in content
    assert "./assets/images/social-preview-1200x630.png" not in content

def test_clinical_data_integrity():
    # H. Clinical data files remain intact
    files = [
        "data/measurements.json",
        "data/glossary.json",
        "data/windows.json",
        "data/protocols.json",
        "data/references.json",
        "data/classifications.json"
    ]
    for file in files:
        assert os.path.exists(file)
        # Verify it is valid JSON
        with open(file, "r", encoding="utf-8") as f:
            json.load(f)
