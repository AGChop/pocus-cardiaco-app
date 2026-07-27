import os
import json
import re

def test_qa2_existing_translations():
    # 1. Valores exactos es/en de las once claves existentes actualizadas.
    path = "data/translations.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = data.get("translations", {})

    # 1. label.install_title
    assert translations["label.install_title"]["es"] == "Instalar LOCUS POCUS"
    assert translations["label.install_title"]["en"] == "Install LOCUS POCUS"

    # 2. label.install_text
    assert translations["label.install_text"]["es"] == "Instala LOCUS POCUS en tu dispositivo móvil para acceder rápidamente y consultar el contenido disponible sin conexión después de la primera carga con Internet."
    assert translations["label.install_text"]["en"] == "Install LOCUS POCUS on your mobile device for quick access and to consult available content offline after the first load with an Internet connection."

    # 3. label.inst_iphone
    assert translations["label.inst_iphone"]["es"] == "📲 Instalar LOCUS POCUS"
    assert translations["label.inst_iphone"]["en"] == "📲 Install LOCUS POCUS"

    # 4. label.inst_iphone_steps
    assert translations["label.inst_iphone_steps"]["es"] == "Sigue estos pasos en Safari:"
    assert translations["label.inst_iphone_steps"]["en"] == "Follow these steps in Safari:"

    # 5. label.inst_iphone_step1
    assert translations["label.inst_iphone_step1"]["es"] == "Abre <strong>Safari</strong> en tu iPhone o iPad y visita este sitio web."
    assert translations["label.inst_iphone_step1"]["en"] == "Open <strong>Safari</strong> on your iPhone or iPad and visit this website."

    # 6. label.inst_iphone_step2
    assert "Toca el botón <strong>Compartir</strong>" in translations["label.inst_iphone_step2"]["es"]
    assert "compartir" not in translations["label.inst_iphone_step2"]["es"].lower() or "Más" in translations["label.inst_iphone_step2"]["es"]
    assert "Share" in translations["label.inst_iphone_step2"]["en"]

    # 7. label.inst_iphone_step3
    assert translations["label.inst_iphone_step3"]["es"] == "Selecciona <strong>\"Agregar a pantalla de inicio\"</strong>."
    assert translations["label.inst_iphone_step3"]["en"] == "Select <strong>\"Add to Home Screen\"</strong>."

    # 8. label.inst_iphone_step4
    assert translations["label.inst_iphone_step4"]["es"] == "Activa <strong>\"Abrir como app web\"</strong> si aparece esa opción."
    assert translations["label.inst_iphone_step4"]["en"] == "Turn on <strong>\"Open as Web App\"</strong> if that option appears."

    # 9. label.inst_iphone_step5
    assert translations["label.inst_iphone_step5"]["es"] == "Confirma el nombre <strong>LOCUS POCUS</strong> y toca <strong>\"Agregar\"</strong>."
    assert translations["label.inst_iphone_step5"]["en"] == "Confirm the name <strong>LOCUS POCUS</strong> and tap <strong>\"Add\"</strong>."

    # 10. label.pwa_note_title
    assert translations["label.pwa_note_title"]["es"] == "Uso sin conexión"
    assert translations["label.pwa_note_title"]["en"] == "Offline use"

    # 11. label.pwa_note_text
    assert "Después de abrir LOCUS POCUS por primera vez" in translations["label.pwa_note_text"]["es"]
    assert "essential content will be stored" in translations["label.pwa_note_text"]["en"]


def test_qa2_new_translations():
    # 2. Existencia y valores exactos es/en de las nueve claves nuevas.
    path = "data/translations.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = data.get("translations", {})

    new_keys = [
        "label.install_ios_title",
        "label.inst_iphone_step6",
        "label.install_android_title",
        "label.install_android_steps",
        "label.install_android_step1",
        "label.install_android_step2",
        "label.install_android_step3",
        "label.install_android_step4",
        "label.install_android_step5"
    ]

    # Validate that there are exactly 9 new keys
    assert len(new_keys) == 9

    for key in new_keys:
        assert key in translations, f"Missing key: {key}"

    # Exact checks:
    assert translations["label.install_ios_title"]["es"] == "iPhone o iPad"
    assert translations["label.install_ios_title"]["en"] == "iPhone or iPad"

    assert translations["label.inst_iphone_step6"]["es"] == "Busca el icono de LOCUS POCUS en la pantalla de inicio y abre la aplicación."
    assert translations["label.inst_iphone_step6"]["en"] == "Find the LOCUS POCUS icon on the Home Screen and open the app."

    assert translations["label.install_android_title"]["es"] == "Android"
    assert translations["label.install_android_title"]["en"] == "Android"

    assert translations["label.install_android_steps"]["es"] == "Sigue estos pasos en Chrome:"
    assert translations["label.install_android_steps"]["en"] == "Follow these steps in Chrome:"

    assert translations["label.install_android_step1"]["es"] == "Abre <strong>Chrome</strong> en tu dispositivo Android y visita este sitio web."
    assert translations["label.install_android_step1"]["en"] == "Open <strong>Chrome</strong> on your Android device and visit this website."

    assert translations["label.install_android_step2"]["es"] == "Toca el menú <strong>Más</strong> <span style=\"font-size: 1.2rem;\">⋮</span> situado a la derecha de la barra de direcciones."
    assert translations["label.install_android_step2"]["en"] == "Tap the <strong>More</strong> menu <span style=\"font-size: 1.2rem;\">⋮</span> to the right of the address bar."

    assert "Agregar a pantalla de inicio" in translations["label.install_android_step3"]["es"]
    assert "Add to home screen" in translations["label.install_android_step3"]["en"]

    assert translations["label.install_android_step4"]["es"] == "Sigue las instrucciones en pantalla para confirmar la instalación de LOCUS POCUS."
    assert translations["label.install_android_step4"]["en"] == "Follow the on-screen instructions to confirm the installation of LOCUS POCUS."

    assert "Busca el icono de LOCUS POCUS" in translations["label.install_android_step5"]["es"]
    assert "Find the LOCUS POCUS icon" in translations["label.install_android_step5"]["en"]


def test_qa2_render_home():
    # 3. renderHome conserva href="#/instalar" y label.inst_iphone,
    # y el valor visible ya no dice “Instalar en iPhone” ni “Install on iPhone” (gracias a translations.json).
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'href="#/instalar"' in content
    assert 'I18n.translate("label.inst_iphone")' in content


def test_qa2_render_install():
    # 4. renderInstall: utiliza label.install_text, contiene títulos y pasos, no usa userAgent, etc.
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Locate renderInstall body
    pattern = r"renderInstall\s*\(container\)\s*\{(.*?)\n\s*\}"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None
    body = match.group(1)

    assert "label.install_title" in body
    assert "label.install_text" in body

    # Contains titles and steps of iPhone/iPad and Android
    assert "label.install_ios_title" in body
    assert "label.inst_iphone_steps" in body
    for i in range(1, 7):
        assert f"label.inst_iphone_step{i}" in body

    assert "label.install_android_title" in body
    assert "label.install_android_steps" in body
    for i in range(1, 6):
        assert f"label.install_android_step{i}" in body

    assert "label.pwa_note_title" in body
    assert "label.pwa_note_text" in body

    # Doesn't use agent/prompt detection
    assert "userAgent" not in body
    assert "beforeinstallprompt" not in body
    assert "navigator.platform" not in body
    assert "android" not in body.lower() or "label.install_android" in body


def test_qa2_terminology_and_neutrality():
    # 5. iPhone e iPad aparecen únicamente en la sección iOS, etc.
    with open("assets/js/router.js", "r", encoding="utf-8") as f:
        content = f.read()

    # "Instalar en iPhone" / "Install on iPhone" should no longer be visible anywhere in translations
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = data.get("translations", {})

    for key, val in translations.items():
        assert "Instalar en iPhone" not in val["es"]
        assert "Install on iPhone" not in val["en"]


def test_qa2_brand_intact():
    # 6. LOCUS POCUS permanece y el manifest.webmanifest e iconos están intactos.
    with open("manifest.webmanifest", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["short_name"] == "LOCUS POCUS"
    icon_srcs = [icon["src"] for icon in manifest["icons"]]
    assert "./assets/icons/locus-pocus-icon-192.png" in icon_srcs


def test_qa2_cache():
    # 7. Caché: nombre exacto, conserva router.js y translations.json.
    with open("service-worker.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "pocus-cardiaco-cache-v17-c3d1-brand1-e1a-e1b-e1c-qa1-qa2" in content
    assert "./assets/js/router.js" in content or "assets/js/router.js" in content
    assert "./data/translations.json" in content or "data/translations.json" in content


def test_qa2_protection():
    # 8. Protecciones: no se modifican archivos clínicos, QA1 permanecen, etc.
    with open("data/translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    translations = data.get("translations", {})

    assert translations["nav.windows"]["es"] == "Vistas ecocardiográficas"
    assert translations["label.cutoff_point"]["en"] == "Cutoff value"
    assert translations["label.abbreviations_list_title"]["en"] == "Abbreviations"

    with open("data/measurements.json", "r", encoding="utf-8") as f:
        measurements = json.load(f)
    assert len(measurements) == 101
