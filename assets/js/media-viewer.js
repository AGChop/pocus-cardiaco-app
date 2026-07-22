// Módulo de visualización y renderizado multimedia genérico de POCUS Cardíaco
const MediaViewer = {
    // Tipos de recursos soportados
    SUPPORTED_TYPES: ['image', 'video', 'animation', 'diagram', 'audio'],

    // MIME types de imagen admitidos
    IMAGE_MIMES: ['image/avif', 'image/webp', 'image/png', 'image/jpeg', 'image/svg+xml'],

    // MIME types de video admitidos
    VIDEO_MIMES: ['video/webm', 'video/mp4'],

    // Obtener los recursos multimedia relacionados a una entidad específica
    getMediaForEntity(resources, entityType, entityId) {
        if (!Array.isArray(resources)) return [];

        const keyMap = {
            protocol: 'linked_protocol_ids',
            component: 'linked_component_ids',
            window: 'linked_window_ids',
            measurement: 'linked_measurement_ids'
        };

        const targetField = keyMap[entityType];
        if (!targetField) {
            console.warn(`MediaViewer: Tipo de entidad '${entityType}' no soportado.`);
            return [];
        }

        const seenIds = new Set();
        return resources.filter(res => {
            if (!res || !res.id || !res.type || !this.SUPPORTED_TYPES.includes(res.type)) {
                return false;
            }
            if (seenIds.has(res.id)) {
                return false; // Evitar duplicaciones
            }

            const linkedIds = res[targetField];
            if (Array.isArray(linkedIds) && linkedIds.includes(entityId)) {
                seenIds.add(res.id);
                return true;
            }
            return false;
        });
    },

    // Resuelve textos internacionalizados con caídas de seguridad
    resolveLocalizedMediaText(value, language = 'es', fallbackLanguage = 'es') {
        if (!value) return '';
        if (typeof value === 'string') return value;
        if (typeof value === 'object') {
            if (value[language]) return value[language];
            if (value[fallbackLanguage]) return value[fallbackLanguage];
            if (value['es']) return value['es'];
            // Retorna la primera cadena disponible en el objeto
            const keys = Object.keys(value);
            if (keys.length > 0) {
                return value[keys[0]] || '';
            }
        }
        return '';
    },

    // Renderiza la sección multimedia principal si hay recursos
    renderMediaSection(resources, options = {}) {
        if (!Array.isArray(resources) || resources.length === 0) {
            return ''; // No crear nodos ni títulos si está vacío
        }

        const lang = options.language || document.documentElement.lang || 'es';
        const titleText = lang === 'en' ? 'Educational Media' : 'Contenido Multimedia Educativo';

        let html = `
            <div class="media-section">
                <h3 class="media-section-title">${titleText}</h3>
                <div class="media-grid">
        `;

        resources.forEach(res => {
            html += this.renderMediaResource(res, options);
        });

        html += `
                </div>
            </div>
        `;
        return html;
    },

    // Renderiza un recurso individual basándose en su tipo
    renderMediaResource(resource, options = {}) {
        if (!resource || !resource.type) return '';

        switch (resource.type) {
            case 'image':
            case 'diagram':
                return this.renderImageResource(resource, options);
            case 'video':
            case 'animation':
                return this.renderVideoResource(resource, options);
            case 'audio':
                return this.renderAudioResource(resource, options);
            default:
                return this.renderMediaFallback(resource, 'Tipo de recurso no soportado.');
        }
    },

    // Genera marcado HTML para imágenes y diagramas
    renderImageResource(resource, options = {}) {
        const lang = options.language || document.documentElement.lang || 'es';
        const title = this.resolveLocalizedMediaText(resource.title, lang);

        let altText = '';
        if (resource.alt_text) {
            altText = this.resolveLocalizedMediaText(resource.alt_text, lang);
        } else {
            console.warn(`MediaViewer: Recurso de imagen '${resource.id}' no posee alt_text requerido.`);
        }

        const caption = this.resolveLocalizedMediaText(resource.caption, lang);
        const attribution = this.resolveLocalizedMediaText(resource.attribution, lang);
        const author = resource.author || '';
        const license = resource.license || '';

        // Filtrar fuentes válidas
        const sources = Array.isArray(resource.sources) ? resource.sources.filter(s => s && this.IMAGE_MIMES.includes(s.mime_type)) : [];
        if (sources.length === 0) {
            return this.renderMediaFallback(resource, 'No se encontraron fuentes de imagen compatibles.');
        }

        // Definir fallback del <img> final
        const fallbackSrc = sources[sources.length - 1].src;

        let sourcesHtml = '';
        // Agregar sources para formatos modernos (AVIF, WebP)
        sources.forEach(srcObj => {
            if (srcObj.mime_type !== 'image/png' && srcObj.mime_type !== 'image/jpeg') {
                sourcesHtml += `<source srcset="${srcObj.src}" type="${srcObj.mime_type}">`;
            }
        });

        let attributionHtml = '';
        if (attribution || author || license) {
            const parts = [];
            if (author) parts.push(author);
            if (attribution) parts.push(attribution);
            if (license) parts.push(license);
            attributionHtml = `<p class="media-attribution">${parts.join(' &bull; ')}</p>`;
        }

        let figcaptionHtml = '';
        if (title || caption || attributionHtml) {
            figcaptionHtml = `
                <figcaption class="media-caption">
                    ${title ? `<strong>${title}</strong><br>` : ''}
                    ${caption ? `<span>${caption}</span>` : ''}
                    ${attributionHtml}
                </figcaption>
            `;
        }

        return `
            <div class="media-card" id="media-card-${resource.id}">
                <figure class="media-figure">
                    <picture class="media-picture">
                        ${sourcesHtml}
                        <img src="${fallbackSrc}" alt="${altText}" class="media-image" loading="lazy" decoding="async">
                    </picture>
                    ${figcaptionHtml}
                </figure>
            </div>
        `;
    },

    // Genera marcado HTML para videos y animaciones basadas en video
    renderVideoResource(resource, options = {}) {
        const lang = options.language || document.documentElement.lang || 'es';
        const title = this.resolveLocalizedMediaText(resource.title, lang);
        const caption = this.resolveLocalizedMediaText(resource.caption, lang);
        const attribution = this.resolveLocalizedMediaText(resource.attribution, lang);
        const transcript = this.resolveLocalizedMediaText(resource.transcript, lang);
        const author = resource.author || '';
        const license = resource.license || '';

        const sources = Array.isArray(resource.sources) ? resource.sources.filter(s => s && this.VIDEO_MIMES.includes(s.mime_type)) : [];
        if (sources.length === 0) {
            return this.renderMediaFallback(resource, 'No se encontraron fuentes de video compatibles.');
        }

        let sourcesHtml = '';
        sources.forEach(s => {
            sourcesHtml += `<source src="${s.src}" type="${s.mime_type}">`;
        });

        let tracksHtml = '';
        if (resource.subtitles && typeof resource.subtitles === 'object') {
            Object.keys(resource.subtitles).forEach(langKey => {
                const label = langKey === 'es' ? 'Español' : (langKey === 'en' ? 'English' : langKey.toUpperCase());
                tracksHtml += `<track kind="subtitles" src="${resource.subtitles[langKey]}" srclang="${langKey}" label="${label}">`;
            });
        }

        let attributionHtml = '';
        if (attribution || author || license) {
            const parts = [];
            if (author) parts.push(author);
            if (attribution) parts.push(attribution);
            if (license) parts.push(license);
            attributionHtml = `<p class="media-attribution">${parts.join(' &bull; ')}</p>`;
        }

        let transcriptHtml = '';
        if (transcript) {
            const buttonText = lang === 'en' ? 'Show Transcript' : 'Ver Transcripción';
            transcriptHtml = `
                <div class="media-transcript-container">
                    <button class="btn-secondary media-transcript-btn" aria-expanded="false">${buttonText}</button>
                    <div class="media-transcript" hidden>
                        <p>${transcript}</p>
                    </div>
                </div>
            `;
        }

        let figcaptionHtml = '';
        if (title || caption || attributionHtml || transcriptHtml) {
            figcaptionHtml = `
                <figcaption class="media-caption">
                    ${title ? `<strong>${title}</strong><br>` : ''}
                    ${caption ? `<span>${caption}</span>` : ''}
                    ${attributionHtml}
                    ${transcriptHtml}
                </figcaption>
            `;
        }

        // Respetar prefers-reduced-motion en HTML
        const hasReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const preloadVal = hasReducedMotion ? 'none' : 'metadata';

        const posterAttr = (resource.poster && resource.poster.trim() !== '') ? ` poster="${resource.poster}"` : '';

        return `
            <div class="media-card" id="media-card-${resource.id}">
                <figure class="media-figure">
                    <video class="media-video" controls preload="${preloadVal}" playsinline${posterAttr}>
                        ${sourcesHtml}
                        ${tracksHtml}
                        <p class="media-fallback-message">Tu navegador no soporta la reproducción de video.</p>
                    </video>
                    ${figcaptionHtml}
                </figure>
            </div>
        `;
    },

    // Genera marcado HTML para audios
    renderAudioResource(resource, options = {}) {
        const lang = options.language || document.documentElement.lang || 'es';
        const title = this.resolveLocalizedMediaText(resource.title, lang);
        const caption = this.resolveLocalizedMediaText(resource.caption, lang);
        const transcript = this.resolveLocalizedMediaText(resource.transcript, lang);

        let sourcesHtml = '';
        if (Array.isArray(resource.sources)) {
            resource.sources.forEach(s => {
                if (s && s.src) {
                    const mimeAttr = s.mime_type ? ` type="${s.mime_type}"` : '';
                    sourcesHtml += `<source src="${s.src}"${mimeAttr}>`;
                }
            });
        }

        if (!sourcesHtml) {
            return this.renderMediaFallback(resource, 'No se encontraron fuentes de audio compatibles.');
        }

        let transcriptHtml = '';
        if (transcript) {
            const buttonText = lang === 'en' ? 'Show Transcript' : 'Ver Transcripción';
            transcriptHtml = `
                <div class="media-transcript-container">
                    <button class="btn-secondary media-transcript-btn" aria-expanded="false">${buttonText}</button>
                    <div class="media-transcript" hidden>
                        <p>${transcript}</p>
                    </div>
                </div>
            `;
        }

        let captionHtml = '';
        if (title || caption || transcriptHtml) {
            captionHtml = `
                <div class="media-caption">
                    ${title ? `<strong>${title}</strong><br>` : ''}
                    ${caption ? `<span>${caption}</span>` : ''}
                    ${transcriptHtml}
                </div>
            `;
        }

        return `
            <div class="media-card" id="media-card-${resource.id}">
                <div class="media-audio-container">
                    <audio class="media-audio" controls preload="metadata">
                        ${sourcesHtml}
                        <p class="media-fallback-message">Tu navegador no soporta la reproducción de audio.</p>
                    </audio>
                    ${captionHtml}
                </div>
            </div>
        `;
    },

    // Renderiza un cuadro de error amigable cuando falla la carga de un recurso multimedia
    renderMediaFallback(resource, message) {
        const resourceId = resource ? resource.id : 'desconocido';
        return `
            <div class="media-card media-fallback" id="media-card-${resourceId}">
                <div class="media-fallback-content">
                    <span class="media-fallback-icon">⚠️</span>
                    <p class="media-fallback-text"><strong>Recurso multimedia no disponible:</strong> ${message}</p>
                </div>
            </div>
        `;
    },

    // Inicializa interacciones y comportamientos de transcripciones en el contenedor renderizado
    initializeMediaInteractions(container) {
        if (!container) return;

        const transcriptButtons = container.querySelectorAll('.media-transcript-btn');
        transcriptButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const transcriptDiv = btn.nextElementSibling;
                if (transcriptDiv) {
                    const isHidden = transcriptDiv.hasAttribute('hidden');
                    if (isHidden) {
                        transcriptDiv.removeAttribute('hidden');
                        btn.setAttribute('aria-expanded', 'true');
                    } else {
                        transcriptDiv.setAttribute('hidden', 'true');
                        btn.setAttribute('aria-expanded', 'false');
                    }
                }
            });
        });
    }
};
