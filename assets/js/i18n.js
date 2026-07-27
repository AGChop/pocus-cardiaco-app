// Módulo de internacionalización (i18n) para la aplicación POCUS Cardíaco
const I18n = {
    _currentLanguage: 'es',
    _translations: {},
    _supportedLanguages: ['es', 'en'],

    async init() {
        // Cargar diccionario desde DataLoader
        try {
            const data = await DataLoader.getTranslations();
            if (data && typeof data === 'object' && data.translations) {
                this._translations = data.translations;
                if (Array.isArray(data.supported_languages)) {
                    this._supportedLanguages = data.supported_languages;
                }
            }
        } catch (e) {
            console.warn("I18n: No se pudo cargar el diccionario de traducciones, usando fallback.", e);
        }

        // Leer idioma desde Storage
        let initialLang = 'es';
        if (typeof Storage !== 'undefined' && typeof Storage.getLanguage === 'function') {
            initialLang = Storage.getLanguage();
        }

        // Validar e inicializar
        this.setLanguage(initialLang, false);
    },

    getLanguage() {
        return this._currentLanguage;
    },

    setLanguage(language, triggerEvent = true) {
        if (!this.isSupportedLanguage(language)) {
            language = 'es';
        }

        this._currentLanguage = language;

        // Guardar en Storage
        if (typeof Storage !== 'undefined' && typeof Storage.setLanguage === 'function') {
            Storage.setLanguage(language);
        }

        // Actualizar etiqueta del documento
        document.documentElement.lang = language;

        // Sincronizar selector visual
        this.refreshLanguageSelector();

        // Aplicar traducciones estáticas del documento
        this.applyTranslations(document);

        // Actualizar título del documento
        const docTitle = this.translate('app.document_title');
        if (docTitle && docTitle !== 'app.document_title') {
            document.title = docTitle;
        }

        // Emitir evento si es solicitado
        if (triggerEvent) {
            const event = new CustomEvent('pocus-language-changed', {
                detail: { language }
            });
            window.dispatchEvent(event);
        }
    },

    isSupportedLanguage(language) {
        return this._supportedLanguages.includes(language);
    },

    getSupportedLanguages() {
        return [...this._supportedLanguages];
    },

    translate(key, variables = {}) {
        if (!key) return "";

        const translationObj = this._translations[key];
        let text = "";

        if (translationObj && typeof translationObj === 'object') {
            text = translationObj[this._currentLanguage] || translationObj['es'] || translationObj['en'] || "";
        }

        // Si no se encuentra la traducción, devolver la propia clave
        if (!text) {
            text = key;
        }

        // Interpolación simple
        Object.keys(variables).forEach(varKey => {
            const replacement = variables[varKey] !== undefined && variables[varKey] !== null ? String(variables[varKey]) : "";
            // Reemplazar de manera segura {varKey}
            text = text.replace(new RegExp(`\\{${varKey}\\}`, 'g'), replacement);
        });

        return text;
    },

    localize(value, language) {
        if (value === null || value === undefined) return "";
        if (typeof value === 'string') return value;
        if (typeof value === 'number' || typeof value === 'boolean') return String(value);

        if (typeof value === 'object') {
            const targetLang = language && this.isSupportedLanguage(language) ? language : this._currentLanguage;

            // Intentar idioma objetivo -> español -> inglés -> primera clave válida -> ""
            if (value[targetLang] !== undefined && value[targetLang] !== null) {
                return String(value[targetLang]);
            }
            if (value['es'] !== undefined && value['es'] !== null) {
                return String(value['es']);
            }
            if (value['en'] !== undefined && value['en'] !== null) {
                return String(value['en']);
            }

            // Buscar primera propiedad de tipo string
            const keys = Object.keys(value);
            for (const k of keys) {
                if (value[k] !== undefined && value[k] !== null) {
                    return String(value[k]);
                }
            }
        }

        return "";
    },

    refreshLanguageSelector() {
        const selector = document.getElementById('language-select');
        if (selector) {
            selector.value = this._currentLanguage;
        }
    },

    applyTranslations(root = document) {
        if (!root) return;

        // 1. TextContent: data-i18n
        const textElements = root.querySelectorAll('[data-i18n]');
        textElements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (key) {
                const translation = this.translate(key);
                if (translation !== key || (this._translations[key] !== undefined)) {
                    el.textContent = translation;
                }
            }
        });

        // 2. Placeholder: data-i18n-placeholder
        const placeholderElements = root.querySelectorAll('[data-i18n-placeholder]');
        placeholderElements.forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (key) {
                const translation = this.translate(key);
                if (translation !== key || (this._translations[key] !== undefined)) {
                    el.setAttribute('placeholder', translation);
                }
            }
        });

        // 3. Aria-label: data-i18n-aria-label
        const ariaElements = root.querySelectorAll('[data-i18n-aria-label]');
        ariaElements.forEach(el => {
            const key = el.getAttribute('data-i18n-aria-label');
            if (key) {
                const translation = this.translate(key);
                if (translation !== key || (this._translations[key] !== undefined)) {
                    el.setAttribute('aria-label', translation);
                }
            }
        });

        // 4. Title: data-i18n-title
        const titleElements = root.querySelectorAll('[data-i18n-title]');
        titleElements.forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (key) {
                const translation = this.translate(key);
                if (translation !== key || (this._translations[key] !== undefined)) {
                    el.setAttribute('title', translation);
                }
            }
        });
    }
};

// Exponer globalmente
window.I18n = I18n;
