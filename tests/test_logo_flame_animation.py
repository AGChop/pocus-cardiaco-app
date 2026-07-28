import os
import json
import re
import hashlib
import colorsys
from PIL import Image

def test_ui1_html_accessible_logo():
    # 1. La imagen principal continúa usando locus_pocus_branding.png.
    # 2. La capa decorativa usa exactamente locus_pocus_flame_overlay.png.
    # 3. La capa mantiene alt="", aria-hidden="true" y draggable="false".
    path = "index.html"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Main logo image
    assert 'src="assets/images/locus_pocus_branding.png"' in content

    # Flame overlay image
    assert 'src="assets/images/locus_pocus_flame_overlay.png"' in content

    # Decorative layer attributes
    flame_match = re.search(r'<img[^>]*class="brand-logo-flame-layer"[^>]*>', content)
    assert flame_match is not None
    flame_tag = flame_match.group(0)
    assert 'alt=""' in flame_tag
    assert 'aria-hidden="true"' in flame_tag
    assert 'draggable="false"' in flame_tag

def test_ui1_css_styles():
    # 4. El CSS de UI1 ya no utiliza clip-path.
    # 5. La animación conserva 520 ms, una iteración, los límites reducidos y prefers-reduced-motion.
    path = "assets/css/styles.css"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".brand-logo-flame-layer" in css
    # Ensure no clip-path is present in UI1 classes
    layer_block_match = re.search(r'\.brand-logo-flame-layer\s*\{([^}]+)\}', css)
    if layer_block_match:
        layer_block = layer_block_match.group(1)
        assert "clip-path" not in layer_block

    # Animation properties
    assert "520ms" in css
    assert "infinite" not in css.lower()

    # Movement limits verification inside @keyframes flame-flicker
    start_idx = css.find("@keyframes flame-flicker")
    end_idx = css.find("@media (prefers-reduced-motion: reduce)", start_idx)
    assert start_idx != -1
    assert end_idx != -1
    assert end_idx > start_idx

    keyframes_block = css[start_idx:end_idx]
    transforms = re.findall(r'transform:\s*([^;]+);', keyframes_block)
    for t in transforms:
        # Scale limits (sx <= 1.02, sy <= 1.06)
        scale_match = re.search(r'scale\(([^)]+)\)', t)
        if scale_match:
            scale_vals = [float(s.strip()) for s in scale_match.group(1).split(',')]
            if len(scale_vals) == 2:
                sx, sy = scale_vals
                assert sx <= 1.02, f"Scale X {sx} exceeds 1.02 limit"
                assert sy <= 1.06, f"Scale Y {sy} exceeds 1.06 limit"

        # TranslateY limit (val <= 0.8%)
        translate_match = re.search(r'translateY\(([^)]+)\)', t)
        if translate_match:
            t_val_str = translate_match.group(1)
            if t_val_str.endswith('%'):
                t_val = abs(float(t_val_str.replace('%', '')))
                assert t_val <= 0.8, f"translateY {t_val}% exceeds 0.8% limit"

        # Rotation limit (val <= 0.6deg)
        rotate_match = re.search(r'rotate\(([^)]+)\)', t)
        if rotate_match:
            r_val_str = rotate_match.group(1)
            if r_val_str.endswith('deg'):
                r_val = abs(float(r_val_str.replace('deg', '')))
                assert r_val <= 0.6, f"rotation {r_val}deg exceeds 0.6deg limit"

    # prefers-reduced-motion
    assert "prefers-reduced-motion: reduce" in css

def test_ui1_flame_overlay_image():
    # 6. El overlay mide 1024 × 1024, es RGBA y tiene esquinas transparentes.
    # 7. Todos los píxeles con alfa distinto de cero del overlay están dentro de x=390..629, y=150..444.
    # 8. Existe una cantidad material de píxeles visibles de llama y no es una imagen vacía.
    path = "assets/images/locus_pocus_flame_overlay.png"
    assert os.path.exists(path)
    img = Image.open(path)
    assert img.size == (1024, 1024)
    assert img.mode == "RGBA"

    # Check corners are transparent
    assert img.getpixel((0, 0))[3] == 0
    assert img.getpixel((0, 1023))[3] == 0
    assert img.getpixel((1023, 0))[3] == 0
    assert img.getpixel((1023, 1023))[3] == 0

    visible_count = 0
    for y in range(1024):
        for x in range(1024):
            r, g, b, a = img.getpixel((x, y))
            if a != 0:
                visible_count += 1
                # Must be strictly within x=390..629, y=150..444
                assert 390 <= x <= 629, f"Non-zero alpha pixel x={x} is outside 390..629"
                assert 150 <= y <= 444, f"Non-zero alpha pixel y={y} is outside 150..444"

    assert visible_count > 5000, "Flame overlay has too few visible pixels"

def test_ui1_main_logo_integrity_and_recolor():
    # 9. El logotipo principal mide 1024 × 1024 y conserva el hash externo exacto.
    # 11. Dentro de las regiones LOCUS existe una cantidad significativa de píxeles dorados y no quedan letras predominantemente azules.
    # 12. POCUS y todos los elementos fuera de las regiones autorizadas permanecen intactos mediante los hashes indicados.
    path = "assets/images/locus_pocus_branding.png"
    assert os.path.exists(path)
    img = Image.open(path).convert("RGB")
    assert img.size == (1024, 1024)

    hasher = hashlib.sha256()
    gold_count = 0
    blue_count = 0

    for y in range(1024):
        for x in range(1024):
            r, g, b = img.getpixel((x, y))
            # Region LOCUS: x=220..514, y=795..879
            if 220 <= x <= 514 and 795 <= y <= 879:
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                # Check for gold/orange pixels
                if r > b and r > 120 and g > 50:
                    gold_count += 1
                # Check for remaining blue text pixels
                if 0.52 <= h <= 0.72 and s >= 0.15 and v <= 0.95:
                    blue_count += 1
            else:
                hasher.update(bytes([r, g, b]))

    computed_hash = hasher.hexdigest()
    assert computed_hash == "fbb0d5116e14858913cee3bcf1e5d31fa9be93a37775538e0334f030889f4433"
    assert gold_count > 1000, "Too few golden pixels in LOCUS region of logo"
    assert blue_count < 100, "Too many blue pixels remaining in LOCUS region of logo"

def test_ui1_social_preview_integrity_and_recolor():
    # 10. La vista previa mide 1200 × 630 y conserva el hash externo exacto.
    # 11 & 12. Recolor and integrity verification
    path = "assets/images/locus_pocus_social_preview_1200x630.png"
    assert os.path.exists(path)
    img = Image.open(path).convert("RGB")
    assert img.size == (1200, 630)

    hasher = hashlib.sha256()
    gold_count = 0
    blue_count = 0

    for y in range(630):
        for x in range(1200):
            r, g, b = img.getpixel((x, y))
            # Region LOCUS: x=390..599, y=470..529
            if 390 <= x <= 599 and 470 <= y <= 529:
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                if r > b and r > 120 and g > 50:
                    gold_count += 1
                if 0.52 <= h <= 0.72 and s >= 0.15 and v <= 0.95:
                    blue_count += 1
            else:
                hasher.update(bytes([r, g, b]))

    computed_hash = hasher.hexdigest()
    assert computed_hash == "d6c1ab56e1d7a4cfe3f6345ce3ac1eb8ee4caccef4315637d566f063b0d081ec"
    assert gold_count > 400, "Too few golden pixels in LOCUS region of social preview"
    assert blue_count < 50, "Too many blue pixels remaining in LOCUS region of social preview"

def test_ui1_service_worker():
    # 13. CACHE_NAME coincide exactamente con el sufijo -logo2.
    # 14. El nuevo overlay está incluido en ASSETS_TO_CACHE.
    path = "service-worker.js"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    cache_match = re.search(r"const CACHE_NAME = '([^']+)';", content)
    assert cache_match is not None
    assert cache_match.group(1).startswith("pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2-qa3-final-logo2")

    assert "./assets/images/locus_pocus_flame_overlay.png" in content

def test_ui1_measurements_clinical_intact():
    # 15. data/measurements.json conserva 101 registros.
    path = "data/measurements.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 101
