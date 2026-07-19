# Guía de Publicación en GitHub Pages (POCUS Cardíaco)

Esta guía te explicará paso a paso y de manera muy sencilla cómo subir tu aplicación POCUS Cardíaco a internet de forma **100% gratuita y segura**, utilizando **GitHub** y **GitHub Pages**. 

Como la aplicación está construida con archivos web estándar (HTML, CSS, JS y JSON), no requiere de servidores de pago ni bases de datos complejas. GitHub la alojará de forma gratuita para siempre.

---

## 1. Conceptos Básicos (Para Principiantes)

* **Git:** Es como un "historial de cambios" para tus archivos de código. Te permite registrar versiones de tu trabajo para no perder nada.
* **GitHub:** Es un sitio web gratuito donde puedes guardar copias de tus proyectos (llamados "repositorios") en la nube.
* **GitHub Pages:** Es un servicio de GitHub que convierte tus archivos web estáticos en una página de internet real y accesible desde cualquier teléfono o computadora con una dirección web (URL) pública.

---

## 2. Paso 1: Crear una cuenta en GitHub

1. Entra a [github.com](https://github.com/) en tu navegador.
2. Haz clic en **Sign up** (Registrarse).
3. Introduce tu correo electrónico, crea una contraseña segura y elige un nombre de usuario.
4. Completa la verificación de seguridad rápida y confirma tu correo. ¡Listo, es completamente gratis!

---

## 3. Paso 2: Instalar Git en tu computadora Mac

Tu Mac probablemente ya tiene Git instalado. Para verificarlo o activarlo:
1. Abre tu terminal de comandos (el terminal integrado en tu editor de código o la aplicación Terminal de tu Mac).
2. Escribe el siguiente comando y pulsa Enter:
   ```bash
   git --version
   ```
3. Si te sale un número de versión (ejemplo: `git version 2.x`), ya está instalado. Si te pide instalar las "Herramientas de línea de comandos de Xcode", acepta la instalación (tardará unos minutos y es gratuita).

---

## 4. Paso 3: Inicializar tu repositorio local

En la terminal de tu proyecto en Mac, ejecuta estos comandos uno por uno para indicarle a Git que empiece a registrar el proyecto:

1. **Inicializar Git:**
   ```bash
   git init -b main
   ```
   *(Esto crea un repositorio local en la carpeta del proyecto y llama a la rama principal "main")*.

2. **Crear archivo para ignorar archivos basura (.gitignore):**
   Crea un archivo llamado `.gitignore` en la raíz de tu carpeta para que Git no suba archivos temporales ni el entorno virtual de Python. Debe contener:
   ```text
   .venv/
   __pycache__/
   .DS_Store
   ```

3. **Registrar los archivos:**
   ```bash
   git add .
   ```
   *(Esto prepara todos los archivos de tu app para ser guardados)*.

4. **Hacer tu primer "Commit" (Guardado de versión):**
   ```bash
   git commit -m "Primera version estable de POCUS Cardiaco con PWA"
   ```

---

## 5. Paso 4: Crear el repositorio en GitHub (Web)

1. Inicia sesión en [github.com](https://github.com/).
2. Haz clic en el botón verde **"New"** (Nuevo) en la esquina superior izquierda o ve a [github.com/new](https://github.com/new).
3. Escribe el nombre del repositorio: `pocus-cardiaco`.
4. Elige si quieres que sea **Público** (cualquiera puede ver el código) o **Privado** (sólo tú puedes ver el código). *Nota: Para usar GitHub Pages gratis con repositorios privados se requiere cuenta de pago, por lo que te recomendamos elegir **Público** (es seguro, no contiene datos confidenciales de pacientes, solo datos médicos educativos públicos)*.
5. **IMPORTANTE:** Deja desmarcadas las opciones de "Add a README file", "Add .gitignore" y "Choose a license", ya que nosotros ya creamos esos archivos localmente.
6. Haz clic en **"Create repository"** (Crear repositorio).

---

## 6. Paso 5: Conectar tu computadora con GitHub y subir el código

GitHub te mostrará una pantalla con instrucciones. Ejecuta estos comandos en la terminal de tu computadora (reemplazando `TU_USUARIO` por tu nombre de usuario de GitHub):

1. **Conectar tu repositorio local con la nube:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/pocus-cardiaco.git
   ```

2. **Subir tu código:**
   ```bash
   git push -u origin main
   ```
   *Nota: Si es la primera vez que lo haces, la terminal te pedirá tus credenciales. GitHub ya no permite contraseñas normales en el terminal; debes generar un **Personal Access Token (PAT)** gratuito desde la configuración de tu cuenta de GitHub (Settings -> Developer Settings -> Personal Access Tokens -> Tokens classic) con el permiso "repo" activado.*

---

## 7. Paso 6: Activar la página web (GitHub Pages)

Una vez que tu código esté en GitHub, activar la página web es cuestión de segundos:

1. Entra a tu repositorio en la web de GitHub (`https://github.com/TU_USUARIO/pocus-cardiaco`).
2. Haz clic en la pestaña **Settings** (Configuración) en la barra superior derecha.
3. En el menú lateral izquierdo, haz clic en **Pages** (Páginas).
4. En la sección **Build and deployment** (Construcción y despliegue), busca la opción **Source** y asegúrate de que esté seleccionada **"Deploy from a branch"**.
5. Debajo, en **Branch** (Rama), cambia "None" por **`main`** y deja la carpeta en **`/ (root)`**.
6. Haz clic en el botón **Save** (Guardar).

---

## 8. ¡Listo! Tu App está en Internet 🎉

Espera aproximadamente de 1 a 2 minutos. Recarga la página de configuración de Pages. En la parte superior aparecerá un recuadro verde con un mensaje similar a este:

> **Your site is live at:** `https://tu_usuario.github.io/pocus-cardiaco/`

¡Esa es la URL pública de tu aplicación!
* Puedes abrir ese enlace desde tu iPhone o compartirlo con colegas y estudiantes.
* Sigue las instrucciones de la sección **"📲 Instalar en iPhone"** dentro de la propia app para tenerla en tu pantalla de inicio como una aplicación nativa que funciona offline.
