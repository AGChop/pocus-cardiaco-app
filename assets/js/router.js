// Enrutador de la aplicación basado en Hash Routing
const Router = {
    // Definición de las rutas y sus respectivos controladores
    async route() {
        const hash = window.location.hash || '#/';
        const container = document.getElementById("app-content");

        if (!container) return;

        // Limpiar contenido previo
        container.innerHTML = `<div class="loading">Cargando contenido médico...</div>`;

        // 1. Ruta de Inicio
        if (hash === '#/' || hash === '#') {
            this.renderHome(container);
            return;
        }

        // 2. Rutas del Glosario
        if (hash === '#/glosario') {
            await this.renderGlossaryList(container);
            return;
        }
        if (hash.startsWith('#/glosario/')) {
            const id = hash.replace('#/glosario/', '');
            await this.renderGlossaryDetail(container, id);
            return;
        }

        // 3. Rutas de Mediciones
        if (hash === '#/mediciones') {
            await this.renderMeasurementsSections(container);
            return;
        }
        if (hash.startsWith('#/mediciones/')) {
            const sectionId = hash.replace('#/mediciones/', '');
            await this.renderMeasurementsList(container, sectionId);
            return;
        }
        if (hash.startsWith('#/medicion/')) {
            const id = hash.replace('#/medicion/', '');
            await this.renderMeasurementDetail(container, id);
            return;
        }

        // Rutas de Ventanas Ecocardiográficas
        if (hash === '#/ventanas') {
            await this.renderWindowsList(container);
            return;
        }
        if (hash.startsWith('#/ventanas/')) {
            const id = hash.replace('#/ventanas/', '');
            await this.renderWindowDetail(container, id);
            return;
        }

        // 4. Otras Secciones
        if (hash === '#/abreviaturas') {
            await this.renderAbbreviations(container);
            return;
        }
        if (hash === '#/clasificaciones') {
            await this.renderClassifications(container);
            return;
        }
        if (hash === '#/conjunto-minimo') {
            await this.renderMinimumSet(container);
            return;
        }
        if (hash === '#/unidades-y-errores') {
            await this.renderUnitWarnings(container);
            return;
        }
        if (hash === '#/favoritos') {
            await this.renderFavorites(container);
            return;
        }
        if (hash === '#/recientes') {
            await this.renderRecents(container);
            return;
        }
        if (hash === '#/referencias') {
            await this.renderReferences(container);
            return;
        }
        if (hash === '#/acerca') {
            this.renderAbout(container);
            return;
        }
        if (hash === '#/instalar') {
            this.renderInstall(container);
            return;
        }

        // Ruta no encontrada (404)
        this.render404(container);
    },

    // --- UTILERÍAS ---

    // Función para copiar texto de forma simple
    copyText(text, btnId) {
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById(btnId);
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = "✓ Contenido copiado";
                btn.style.backgroundColor = "#e2e8f0";
                btn.style.color = "#1e293b";
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = "";
                    btn.style.color = "";
                }, 1500);
            }
        });
    },

    // Función para manejar favoritos
    toggleFav(type, id, title, btnId) {
        const added = Storage.toggleFavorite(type, id, title);
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.innerHTML = added ? "★ Quitar Favorito" : "☆ Guardar Favorito";
        }
    },

    // --- RENDERIZADORES DE VISTAS ---

    // Menú Principal
    renderHome(container) {
        container.innerHTML = `
            <div style="text-align: center; margin-bottom: 1.5rem; margin-top: 1rem;">
                <p style="font-size: 0.95rem; color: var(--text-muted-light);">
                    Herramienta educativa de consulta rápida para residentes y médicos en formación en ultrasonido POCUS cardiaco.
                </p>
            </div>

            <div class="main-nav">
                <a href="#/glosario" class="nav-card">
                    <h2>Glosario de Términos</h2>
                    <p>Definición de parámetros, ventanas de adquisición y vocabulario clínico de POCUS.</p>
                </a>
                <a href="#/mediciones" class="nav-card">
                    <h2>Banco de Mediciones</h2>
                    <p>12 secciones con valores normales, fórmulas y puntos de corte ecocardiográficos.</p>
                </a>
                <a href="#/ventanas" class="nav-card">
                    <h2>Ventanas ecocardiográficas</h2>
                    <p>Guía de posición del transductor, orientación del marcador, estructuras visibles y mediciones asociadas.</p>
                </a>
            </div>

            <div class="secondary-nav" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem;">
                <a href="#/abreviaturas" class="btn-secondary">Abreviaturas</a>
                <a href="#/clasificaciones" class="btn-secondary">Clasificaciones</a>
                <a href="#/conjunto-minimo" class="btn-secondary">Conjunto Mínimo</a>
                <a href="#/unidades-y-errores" class="btn-secondary">Unidades y Errores</a>
                <a href="#/favoritos" class="btn-secondary">Mis Favoritos</a>
                <a href="#/recientes" class="btn-secondary">Recientes</a>
                <a href="#/referencias" class="btn-secondary">Referencias</a>
                <a href="#/acerca" class="btn-secondary">Acerca de</a>
            </div>

            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="#/instalar" class="btn-install">📲 Instalar en iPhone</a>
            </div>
        `;
    },

    // 404 - No Encontrado
    render404(container) {
        container.innerHTML = `
            <div class="card error-card">
                <h2>Ruta no encontrada</h2>
                <p>Lo sentimos, la sección o página que buscas no existe o fue movida.</p>
                <a href="#/" class="btn-primary">Volver al Inicio</a>
            </div>
        `;
    },

    // GLOSARIO DE TÉRMINOS
    async renderGlossaryList(container) {
        const glossary = await DataLoader.getGlossary() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Glosario de Términos</h2>
            </div>

            <!-- Vista de Computadora (Tabla) -->
            <div class="desktop-view">
                <table class="clinical-table">
                    <thead>
                        <tr>
                            <th>Término</th>
                            <th>Definición</th>
                            <th>Adquisición, Utilidad o Limitación</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        glossary.forEach(item => {
            const isFav = Storage.isFavorite("término", item.id);
            const copyData = `Término: ${item.term}\nDefinición: ${item.definition}\nAdquisición/Utilidad: ${item.acquisition_utility_limitation}\nFuente: ${item.source_document} (Pág. ${item.source_page})`;

            html += `
                <tr>
                    <td><strong>${item.term}</strong></td>
                    <td>${item.definition}</td>
                    <td>${item.acquisition_utility_limitation}</td>
                    <td>
                        <div class="table-actions">
                            <a href="#/glosario/${item.id}" class="btn-table-action">Detalle</a>
                            <button class="btn-table-action" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-t-${item.id}')" id="copy-t-${item.id}">Copiar</button>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>

            <!-- Vista de Teléfono (Tarjetas) -->
            <div class="mobile-view">
                <div class="cards-list">
        `;

        glossary.forEach(item => {
            const isFav = Storage.isFavorite("término", item.id);
            const copyData = `Término: ${item.term}\nDefinición: ${item.definition}\nAdquisición/Utilidad: ${item.acquisition_utility_limitation}\nFuente: ${item.source_document} (Pág. ${item.source_page})`;

            html += `
                <div class="card clinical-card">
                    <div class="card-header">
                        <h3>${item.term}</h3>
                        <span class="card-category">${item.category}</span>
                    </div>
                    <p class="card-definition"><strong>Definición:</strong> ${item.definition}</p>
                    <p class="card-acquisition"><strong>Adquisición/Utilidad:</strong> ${item.acquisition_utility_limitation}</p>
                    <div class="card-meta">Página origen: ${item.source_page}</div>
                    <div class="card-actions">
                        <a href="#/glosario/${item.id}" class="btn-card-action">Detalle</a>
                        <button class="btn-card-action" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-m-t-${item.id}')" id="copy-m-t-${item.id}">Copiar</button>
                        <button class="btn-card-action" onclick="Router.toggleFav('término', '${item.id}', '${item.term}', 'fav-t-${item.id}')" id="fav-t-${item.id}">
                            ${isFav ? "★ Quitar" : "☆ Favorito"}
                        </button>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
        container.innerHTML = html;
    },

    // DETALLE DE TÉRMINO
    async renderGlossaryDetail(container, id) {
        const glossary = await DataLoader.getGlossary() || [];
        const term = glossary.find(item => item.id === id);

        if (!term) {
            this.render404(container);
            return;
        }

        Storage.addRecent("término", term.id, term.term);
        const isFav = Storage.isFavorite("término", term.id);
        const copyData = `Término: ${term.term}\nDefinición: ${term.definition}\nAdquisición/Utilidad: ${term.acquisition_utility_limitation}\nFuente: ${term.source_document} (Pág. ${term.source_page})`;

        let html = `
            <div class="navigation-header">
                <a href="#/glosario" class="btn-back">← Glosario</a>
                <h2>${term.term}</h2>
            </div>

            <div class="card clinical-detail-card">
                <div class="card-section">
                    <span class="detail-label">Categoría</span>
                    <span class="detail-value">${term.category}</span>
                </div>
                <div class="card-section">
                    <span class="detail-label">Definición</span>
                    <p class="detail-text">${term.definition}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">Adquisición, Utilidad y Limitaciones</span>
                    <p class="detail-text">${term.acquisition_utility_limitation}</p>
                </div>
                ${term.aliases && term.aliases.length > 0 ? `
                <div class="card-section">
                    <span class="detail-label">Alias / Sinonimia</span>
                    <p class="detail-text">${term.aliases.join(", ")}</p>
                </div>` : ''}
                <div class="card-section">
                    <span class="detail-label">Fuente Autorizada</span>
                    <p class="detail-text">${term.source_document} (Página ${term.source_page})</p>
                </div>

                <div class="detail-actions">
                    <button class="btn-primary" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-det-t')" id="copy-det-t">Copiar Contenido</button>
                    <button class="btn-secondary" onclick="Router.toggleFav('término', '${term.id}', '${term.term}', 'fav-det-t')" id="fav-det-t">
                        ${isFav ? "★ Quitar Favorito" : "☆ Guardar Favorito"}
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    // BANCO DE MEDICIONES - SECCIONES
    async renderMeasurementsSections(container) {
        const sections = await DataLoader.getSections() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Banco de Mediciones</h2>
            </div>
            <div class="sections-list">
        `;

        sections.forEach(sec => {
            html += `
                <a href="#/mediciones/${sec.id}" class="section-card">
                    <div class="section-num">Sección ${sec.number}</div>
                    <h3>${sec.title}</h3>
                    <p>${sec.description}</p>
                    ${sec.clinical_warning ? `<span class="warning-badge">⚠️ Advertencia</span>` : ''}
                </a>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
    },

    // MEDICIONES POR SECCIÓN
    async renderMeasurementsList(container, sectionId) {
        const sections = await DataLoader.getSections() || [];
        const section = sections.find(s => s.id === sectionId);

        if (!section) {
            this.render404(container);
            return;
        }

        const measurements = await DataLoader.getMeasurements() || [];
        const filtered = measurements.filter(m => m.section_id === sectionId);

        // Ordenar tarjetas dentro de la sección por display_order, priority_tier, original_order y measurement_id
        filtered.sort((a, b) => {
            const displayA = a.display_order !== undefined ? a.display_order : 9999;
            const displayB = b.display_order !== undefined ? b.display_order : 9999;
            if (displayA !== displayB) return displayA - displayB;

            const tierA = a.priority_tier !== undefined ? a.priority_tier : 99;
            const tierB = b.priority_tier !== undefined ? b.priority_tier : 99;
            if (tierA !== tierB) return tierA - tierB;

            const origA = a.original_order !== undefined ? a.original_order : (a.order || 9999);
            const origB = b.original_order !== undefined ? b.original_order : (b.order || 9999);
            if (origA !== origB) return origA - origB;

            return (a.id || "").localeCompare(b.id || "");
        });

        let html = `
            <div class="navigation-header">
                <a href="#/mediciones" class="btn-back">← Banco</a>
                <h2>Sección ${section.number}: ${section.short_title}</h2>
            </div>

            ${section.clinical_warning ? `
            <div class="safety-banner" role="alert">
                <strong>Advertencia de Seguridad:</strong> ${section.clinical_warning}
            </div>` : ''}

            <!-- Lista de Mediciones en Acordeón -->
            <div class="measurements-grid cards-list">
        `;

        filtered.forEach(item => {
            const isFav = Storage.isFavorite("medición", item.id);
            const copyData = `Medición: ${item.measurement}\nFórmula/Método: ${item.formula_or_method}\nValores normales: ${item.normal_values}\nLimitaciones: ${item.interpretation_limitations}\nUnidad: ${item.units}\nFuente: ${item.source_document} (Pág. ${item.source_page})`;

            html += `
                <details class="measurement-accordion card clinical-card">
                    <summary class="accordion-summary">
                        <span class="measurement-title">${item.measurement}</span>
                        <span class="accordion-arrow"></span>
                    </summary>
                    <div class="measurement-accordion-content">
                        <div class="measurement-header-content">
                            <span class="unit-badge">${item.units}</span>
                        </div>
                        <p><strong>Fórmula/Adquisición:</strong> ${item.formula_or_method}</p>
                        <p class="normal-values"><strong>Valores normales / Corte:</strong> ${item.normal_values}</p>
                        <p class="limitations"><strong>Limitaciones:</strong> ${item.interpretation_limitations}</p>
                        <div class="card-meta">Página origen: ${item.source_page}</div>
                        <div class="card-actions">
                            <a href="#/medicion/${item.id}" class="btn-card-action">Detalle</a>
                            <button class="btn-card-action" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-m-m-${item.id}')" id="copy-m-m-${item.id}">Copiar</button>
                            <button class="btn-card-action" onclick="Router.toggleFav('medición', '${item.id}', '${item.measurement}', 'fav-m-${item.id}')" id="fav-m-${item.id}">
                                ${isFav ? "★ Quitar" : "☆ Favorito"}
                            </button>
                        </div>
                    </div>
                </details>
            `;
        });

        html += `
            </div>
        `;

        container.innerHTML = html;
    },

    // DETALLE DE MEDICIÓN
    async renderMeasurementDetail(container, id) {
        const measurements = await DataLoader.getMeasurements() || [];
        const item = measurements.find(m => m.id === id);

        if (!item) {
            this.render404(container);
            return;
        }

        Storage.addRecent("medición", item.id, item.measurement);
        const isFav = Storage.isFavorite("medición", item.id);
        const copyData = `Medición: ${item.measurement}\nFórmula/Método: ${item.formula_or_method}\nValores normales: ${item.normal_values}\nLimitaciones: ${item.interpretation_limitations}\nUnidad: ${item.units}\nFuente: ${item.source_document} (Pág. ${item.source_page})`;

        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const getLinkForWindow = (primary, view) => {
            const p = (primary || "").toLowerCase();
            const v = (view || "").toLowerCase();
            if (v.includes("plax")) return "plax";
            if (v.includes("psax")) return "psax";
            if (v.includes("a4c-vd") || v.includes("enfoque vd") || v.includes("enfocada en vd")) return "rv_focused_a4c";
            if (v.includes("a4c") || v.includes("4c")) return "a4c";
            if (v.includes("a2c") || v.includes("2c")) return "a2c";
            if (v.includes("a3c") || v.includes("3c")) return "a3c";
            if (v.includes("a5c") || v.includes("5c")) return "a5c";
            if (v.includes("vci") || v.includes("cava")) return "subcostal_ivc";
            if (v.includes("subcostal 4c") || v.includes("sc4c")) return "subcostal_4c";
            if (v.includes("inflow") || v.includes("entrada vd")) return "rv_inflow";
            if (p.includes("derecha") || v.includes("rps")) return "right_parasternal";
            if (p.includes("supraesternal") || v.includes("ssn")) return "suprasternal";
            if (p.includes("subcostal")) return "subcostal_4c";
            if (p.includes("paraesternal")) return "plax";
            return null;
        };

        // Construir la sección de Ventana y técnica recomendadas
        let windowsHtml = "";
        const isAltArray = Array.isArray(item.alternate_windows);
        const hasAlternate = isAltArray && item.alternate_windows.length > 0;

        if (item.primary_window || item.preferred_view || item.modality || item.acquisition_timing || item.acquisition_key || hasAlternate) {
            let altWindowsContent = "";
            if (!isAltArray || item.alternate_windows.length === 0) {
                altWindowsContent = '<p class="detail-text">No se especifican ventanas alternativas.</p>';
            } else if (item.alternate_windows.length === 1) {
                altWindowsContent = `<p class="detail-text">${escapeHTML(item.alternate_windows[0])}</p>`;
            } else {
                altWindowsContent = `<ul class="detail-list" style="margin: 0.25rem 0 0 1.25rem; padding-left: 0; color: var(--text-main-light); list-style-type: disc;">
                    ${item.alternate_windows.map(win => `<li style="margin-bottom: 0.25rem;">${escapeHTML(win)}</li>`).join("")}
                </ul>`;
            }

            const winId = getLinkForWindow(item.primary_window, item.preferred_view);
            const primaryWindowHTML = winId
                ? `<a href="#/ventanas/${winId}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(item.primary_window)}</a>`
                : escapeHTML(item.primary_window);

            windowsHtml = `
                <div class="card-section-divider" style="margin: 0.5rem 0; border-top: 1px dashed var(--border-light);"></div>
                <details style="margin-top: 0.5rem;">
                    <summary style="font-size: 1.1rem; font-weight: 600; color: var(--primary-medium); cursor: pointer; padding: 0.25rem 0; outline: none; user-select: none;">
                        Ventana y técnica recomendadas
                    </summary>
                    <div style="display: flex; flex-direction: column; gap: 1.25rem; margin-top: 0.75rem; padding-left: 0.25rem;">
                        ${item.primary_window ? `
                        <div class="card-section">
                            <span class="detail-label">Ventana acústica primaria</span>
                            <p class="detail-text">${primaryWindowHTML}</p>
                        </div>` : ''}

                        ${item.preferred_view ? `
                        <div class="card-section">
                            <span class="detail-label">Vista recomendada</span>
                            <p class="detail-text">${escapeHTML(item.preferred_view)}</p>
                        </div>` : ''}

                        ${item.modality ? `
                        <div class="card-section">
                            <span class="detail-label">Modalidad ecográfica</span>
                            <p class="detail-text">${escapeHTML(item.modality)}</p>
                        </div>` : ''}

                        ${item.acquisition_timing ? `
                        <div class="card-section">
                            <span class="detail-label">Momento de adquisición</span>
                            <p class="detail-text">${escapeHTML(item.acquisition_timing)}</p>
                        </div>` : ''}

                        ${item.acquisition_key ? `
                        <div class="card-section">
                            <span class="detail-label">Consejo técnico de adquisición</span>
                            <p class="detail-text" style="font-style: italic;">${escapeHTML(item.acquisition_key)}</p>
                        </div>` : ''}

                        <div class="card-section">
                            <span class="detail-label">Ventanas alternativas</span>
                            ${altWindowsContent}
                        </div>
                    </div>
                </details>
            `;
        }

        let html = `
            <div class="navigation-header">
                <a href="#/mediciones/${item.section_id}" class="btn-back">← Sección</a>
                <h2>${item.measurement}</h2>
            </div>

            <div class="card clinical-detail-card">
                <div class="card-section">
                    <span class="detail-label">Fórmula o Método de Adquisición</span>
                    <p class="detail-text">${item.formula_or_method}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">Valores de Referencia / Puntos de Corte</span>
                    <p class="detail-text highlight-text">${item.normal_values}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">Unidades de Medida</span>
                    <span class="unit-badge large-badge">${item.units}</span>
                </div>
                <div class="card-section">
                    <span class="detail-label">Limitaciones y Precauciones</span>
                    <p class="detail-text warning-text">${item.interpretation_limitations}</p>
                </div>
                ${item.aliases && item.aliases.length > 0 ? `
                <div class="card-section">
                    <span class="detail-label">Alias comunes</span>
                    <p class="detail-text">${item.aliases.join(", ")}</p>
                </div>` : ''}
                <div class="card-section">
                    <span class="detail-label">Fuente Autorizada</span>
                    <p class="detail-text">${item.source_document} (Página ${item.source_page})</p>
                </div>

                ${windowsHtml}

                <div class="detail-actions">
                    <button class="btn-primary" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-det-m')" id="copy-det-m">Copiar Contenido</button>
                    <button class="btn-secondary" onclick="Router.toggleFav('medición', '${item.id}', '${item.measurement}', 'fav-det-m')" id="fav-det-m">
                        ${isFav ? "★ Quitar Favorito" : "☆ Guardar Favorito"}
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    // LISTA DE VENTANAS ECOCARDIOGRÁFICAS
    async renderWindowsList(container) {
        let windows = [];
        try {
            windows = await DataLoader.getWindows();
            if (!windows || windows.length === 0) {
                throw new Error("No se encontraron ventanas o el archivo está vacío.");
            }
        } catch (error) {
            container.innerHTML = `
                <div class="card error-card">
                    <h2>Error al cargar las ventanas</h2>
                    <p>Lo sentimos, no pudimos cargar la lista de ventanas ecocardiográficas. Por favor, intente nuevamente más tarde.</p>
                    <a href="#/" class="btn-primary">Volver al Inicio</a>
                </div>
            `;
            return;
        }

        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Ventanas Ecocardiográficas</h2>
            </div>

            <div class="desktop-view">
                <table class="clinical-table">
                    <thead>
                        <tr>
                            <th>Ventana</th>
                            <th>Abreviatura</th>
                            <th>Estructuras Favorecidas</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        windows.forEach(item => {
            html += `
                <tr>
                    <td><strong>${escapeHTML(item.window)}</strong></td>
                    <td><span class="unit-badge">${escapeHTML(item.abbreviation)}</span></td>
                    <td>${escapeHTML(item.favored_structures)}</td>
                    <td>
                        <a href="#/ventanas/${item.id}" class="btn-table-action">Detalle</a>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>

            <div class="mobile-view">
                <div class="cards-list">
        `;

        windows.forEach(item => {
            html += `
                <div class="card clinical-card">
                    <div class="card-header">
                        <h3>${escapeHTML(item.window)}</h3>
                        <span class="unit-badge">${escapeHTML(item.abbreviation)}</span>
                    </div>
                    <p><strong>Estructuras favorecidas:</strong> ${escapeHTML(item.favored_structures)}</p>
                    <div class="card-actions">
                        <a href="#/ventanas/${item.id}" class="btn-card-action">Detalle</a>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    // DETALLE DE VENTANA ECOCARDIOGRÁFICA
    async renderWindowDetail(container, id) {
        let windows = [];
        let measurements = [];
        try {
            windows = await DataLoader.getWindows() || [];
            measurements = await DataLoader.getMeasurements() || [];
        } catch (error) {
            container.innerHTML = `
                <div class="card error-card">
                    <h2>Error al cargar la información</h2>
                    <p>No se pudo cargar la información de la ventana ecocardiográfica.</p>
                    <a href="#/ventanas" class="btn-primary">Volver a Ventanas</a>
                </div>
            `;
            return;
        }

        const item = windows.find(w => w.id === id);
        if (!item) {
            this.render404(container);
            return;
        }

        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        // Relación con mediciones
        let favoredMeasurementsHTML = "";
        if (item.favored_measurements) {
            const parts = item.favored_measurements.split(",").map(p => p.trim());
            const linkedParts = parts.map(part => {
                const part_lower = part.toLowerCase();
                let found = null;

                for (const m of measurements) {
                    const m_name = m.measurement.toLowerCase();
                    const m_abbr = (m.abbreviation || "").toLowerCase();
                    const aliases = (m.aliases || []).map(a => a.toLowerCase());

                    if (part_lower === m_abbr || part_lower === m_name || aliases.includes(part_lower)) {
                        found = m;
                        break;
                    }
                }

                if (!found) {
                    const manualMap = {
                        "dtdvi/dtsvi": "dtdvi",
                        "dtdvi": "dtdvi",
                        "dtsvi": "dtsvi",
                        "ivsd": "ivsd",
                        "pwtd": "pwtd",
                        "rwt": "rwt_meas",
                        "epss": "epss",
                        "mapse": "mapse",
                        "tapse": "tapse_meas",
                        "grosor pared vd": "grosor_pared_vd",
                        "planimetría mitral": "area_mitral_planimetria",
                        "diámetro tsvi": "area_tsvi_meas",
                        "diámetro ai": "diametro_ap_ai",
                        "lavi": "lavi_meas",
                        "flujo mitral": "onda_e_mitral",
                        "gls": "gls_vi",
                        "wmsi": "wmsi",
                        "subcostal": "derrame_pericardico_pequeno"
                    };
                    if (manualMap[part_lower]) {
                        found = measurements.find(m => m.id === manualMap[part_lower]);
                    }
                }

                if (found) {
                    return `<a href="#/medicion/${found.id}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(part)}</a>`;
                } else {
                    return escapeHTML(part);
                }
            });
            favoredMeasurementsHTML = linkedParts.join(", ");
        }

        let html = `
            <div class="navigation-header">
                <a href="#/ventanas" class="btn-back">← Ventanas</a>
                <h2>${escapeHTML(item.window)}</h2>
            </div>

            <div class="card clinical-detail-card">
                ${item.abbreviation ? `
                <div class="card-section">
                    <span class="detail-label">Abreviatura</span>
                    <span class="unit-badge large-badge" style="width: fit-content;">${escapeHTML(item.abbreviation)}</span>
                </div>` : ''}

                ${item.typical_probe_position ? `
                <div class="card-section">
                    <span class="detail-label">Posición del transductor</span>
                    <p class="detail-text">${escapeHTML(item.typical_probe_position)}</p>
                </div>` : ''}

                ${item.typical_marker_orientation ? `
                <div class="card-section">
                    <span class="detail-label">Orientación del marcador</span>
                    <p class="detail-text">${escapeHTML(item.typical_marker_orientation)}</p>
                </div>` : ''}

                ${item.favored_structures ? `
                <div class="card-section">
                    <span class="detail-label">Estructuras favorecidas</span>
                    <p class="detail-text">${escapeHTML(item.favored_structures)}</p>
                </div>` : ''}

                ${favoredMeasurementsHTML ? `
                <div class="card-section">
                    <span class="detail-label">Mediciones favorecidas</span>
                    <p class="detail-text">${favoredMeasurementsHTML}</p>
                </div>` : ''}
            </div>
        `;

        container.innerHTML = html;
    },

    // ABREVIATURAS
    async renderAbbreviations(container) {
        const abbreviations = await DataLoader.getAbbreviations() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Lista de Abreviaturas</h2>
            </div>

            <table class="clinical-table">
                <thead>
                    <tr>
                        <th>Abreviatura</th>
                        <th>Significado Clínico</th>
                        <th>Página</th>
                    </tr>
                </thead>
                <tbody>
        `;

        abbreviations.forEach(abbr => {
            html += `
                <tr>
                    <td><strong>${abbr.abbreviation}</strong></td>
                    <td>${abbr.meaning}</td>
                    <td>Pág. ${abbr.source_page}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;
        container.innerHTML = html;
    },

    // CLASIFICACIONES
    async renderClassifications(container) {
        const classifications = await DataLoader.getClassifications() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Clasificaciones Prácticas</h2>
            </div>
        `;

        classifications.forEach(c => {
            html += `
                <div class="card" style="margin-bottom: 1.5rem; padding: 1.5rem; background-color: var(--card-bg-light); border: 1px solid var(--border-light); border-radius: 12px;">
                    <h3 style="color: var(--primary-medium); margin-bottom: 0.5rem;">${c.name}</h3>
                    <table class="clinical-table" style="margin: 0.5rem 0;">
                        <thead>
                            <tr>
                                <th>${c.items[0].range ? "Rango" : "Parámetro"}</th>
                                <th>${c.items[0].category ? "Clasificación" : "Punto de corte"}</th>
                                ${c.items[0].method ? "<th>Método</th>" : ""}
                            </tr>
                        </thead>
                        <tbody>
            `;
            c.items.forEach(item => {
                html += `
                    <tr>
                        <td><strong>${item.range || item.parameter}</strong></td>
                        <td>${item.category || item.threshold}</td>
                        ${item.method ? `<td>${item.method}</td>` : ""}
                    </tr>
                `;
            });
            html += `
                        </tbody>
                    </table>
                    ${c.note ? `<p style="font-size: 0.85rem; color: var(--text-muted-light); margin-top: 0.5rem;"><strong>Nota:</strong> ${c.note}</p>` : ""}
                    <div style="font-size: 0.8rem; color: var(--text-muted-light); text-align: right; margin-top: 0.25rem;">Página origen: ${c.source_page}</div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    // CONJUNTO MÍNIMO POCUS
    async renderMinimumSet(container) {
        const minSet = await DataLoader.getMinimumPocusSet() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Conjunto Mínimo POCUS</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light);">
                <p style="margin-bottom: 1rem; font-size: 0.95rem; color: var(--text-muted-light);">
                    Habilidades y destrezas ecográficas básicas que el operador POCUS debe dominar para una evaluación cardiaca inicial completa.
                </p>
                <ol style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
        `;

        minSet.forEach(item => {
            html += `
                <li style="font-size: 0.95rem;">
                    <strong>${item.skill}</strong>
                    <span style="font-size: 0.8rem; color: var(--text-muted-light); margin-left: 0.5rem;">(Pág. ${item.source_page})</span>
                </li>
            `;
        });

        html += `
                </ol>
                <div class="safety-banner" style="margin-top: 1.5rem;">
                    <strong>Principio de integración:</strong> La función diastólica, la función del VD, la hipertensión pulmonar, la severidad valvular y el taponamiento no deben definirse mediante una sola medición aislada.
                </div>
            </div>
        `;
        container.innerHTML = html;
    },

    // UNIDADES Y ERRORES FRECUENTES
    async renderUnitWarnings(container) {
        const warnings = await DataLoader.getUnitWarnings() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Unidades y Errores Frecuentes</h2>
            </div>

            <div class="cards-list">
        `;

        warnings.forEach(w => {
            html += `
                <div class="card clinical-card warning-card" style="border-left: 4px solid #eab308; background-color: var(--card-bg-light);">
                    <h3 style="color: var(--warning-text); font-size: 1.1rem; margin-bottom: 0.25rem;">${w.parameter}</h3>
                    <p style="font-size: 0.95rem;">${w.warning}</p>
                    <div style="font-size: 0.8rem; color: var(--text-muted-light); margin-top: 0.5rem; text-align: right;">Página origen: ${w.source_page}</div>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
    },

    // MIS FAVORITOS
    async renderFavorites(container) {
        const favs = Storage.getFavorites();

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Mis Favoritos</h2>
            </div>
        `;

        if (favs.length === 0) {
            html += `
                <div class="card error-card">
                    <p>Aún no has guardado ningún favorito. Pulsa sobre el botón "☆ Favorito" en cualquier ficha.</p>
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        html += `
            <div style="text-align: right; margin-bottom: 1rem;">
                <button id="clear-all-favs" class="btn-secondary" style="display: inline-flex; min-height: 38px; padding: 0.25rem 1rem;">Limpiar Todos</button>
            </div>
            <div class="cards-list">
        `;

        favs.forEach(f => {
            const link = f.type === "medición" ? `#/medicion/${f.id}` : `#/glosario/${f.id}`;
            const badgeClass = f.type === "medición" ? "badge-medicion" : "badge-termino";

            html += `
                <div class="card clinical-card" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 1rem;">
                    <div>
                        <a href="${link}" style="text-decoration: none; font-weight: 600; color: var(--primary-light); font-size: 1.05rem;">${f.title}</a>
                        <span class="result-badge ${badgeClass}" style="margin-left: 0.5rem;">${f.type}</span>
                    </div>
                    <button class="btn-table-action" onclick="Storage.toggleFavorite('${f.type}', '${f.id}', '${f.title}'); Router.route();" style="background-color: #fee2e2; color: #991b1b; border: none; border-radius: 6px; padding: 0.35rem 0.75rem; cursor: pointer;">Eliminar</button>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;

        document.getElementById("clear-all-favs")?.addEventListener("click", () => {
            if (confirm("¿Estás seguro de que deseas borrar todos tus favoritos guardados?")) {
                Storage.clearFavorites();
                Router.route();
            }
        });
    },

    // VISTOS RECIENTEMENTE
    async renderRecents(container) {
        const recents = Storage.getRecents();

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Vistos Recientemente</h2>
            </div>
        `;

        if (recents.length === 0) {
            html += `
                <div class="card error-card">
                    <p>No tienes elementos vistos recientemente en el historial.</p>
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        html += `
            <div style="text-align: right; margin-bottom: 1rem;">
                <button id="clear-all-recs" class="btn-secondary" style="display: inline-flex; min-height: 38px; padding: 0.25rem 1rem;">Limpiar Historial</button>
            </div>
            <div class="cards-list">
        `;

        recents.forEach(r => {
            const link = r.type === "medición" ? `#/medicion/${r.id}` : `#/glosario/${r.id}`;
            const badgeClass = r.type === "medición" ? "badge-medicion" : "badge-termino";

            html += `
                <div class="card clinical-card" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 1rem;">
                    <div>
                        <a href="${link}" style="text-decoration: none; font-weight: 600; color: var(--primary-light); font-size: 1.05rem;">${r.title}</a>
                        <span class="result-badge ${badgeClass}" style="margin-left: 0.5rem;">${r.type}</span>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;

        document.getElementById("clear-all-recs")?.addEventListener("click", () => {
            Storage.clearRecents();
            Router.route();
        });
    },

    // REFERENCIAS PRINCIPALES
    async renderReferences(container) {
        const refs = await DataLoader.getReferences() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Referencias Bibliográficas</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 1rem;">
        `;

        refs.forEach(r => {
            html += `
                <div style="border-bottom: 1px solid var(--border-light); padding-bottom: 0.75rem; font-size: 0.9rem;">
                    <p style="margin-bottom: 0.25rem;">${r.citation}</p>
                    <span style="font-size: 0.75rem; color: var(--text-muted-light);">Citado en Página ${r.source_page} del PDF.</span>
                </div>
            `;
        });

        html += `
                <p style="font-size: 0.8rem; color: var(--text-muted-light); font-style: italic; margin-top: 1rem;">
                    <strong>Nota editorial:</strong> Los valores de referencia pueden variar entre guías, laboratorios, equipos y poblaciones. Para decisiones clínicas definitivas debe consultarse la publicación primaria y el protocolo institucional vigente.
                </p>
            </div>
        `;
        container.innerHTML = html;
    },

    // ACERCA DE
    renderAbout(container) {
        container.innerHTML = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Acerca de POCUS Cardíaco</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 1rem; font-size: 0.95rem;">
                <p><strong>POCUS Cardíaco</strong> es una aplicación web y PWA educativa, diseñada exclusivamente como una herramienta de consulta rápida y banco de mediciones.</p>
                <p>Tiene como objetivo apoyar en la formación de médicos generales, residentes de especialidades médicas (Medicina Interna, Anestesiología, Urgencias, Cuidado Crítico) y estudiantes durante la adquisición de competencias en ultrasonido clínico enfocado en el punto de atención (POCUS).</p>
                <p>Esta aplicación fue desarrollada y revisada por médicos internistas del <strong>Hospital San Rafael de Alajuela (HSRA)</strong> para el curso de POCUS del <strong>Posgrado de Medicina Interna de la Universidad de Costa Rica (UCR)</strong>.</p>
                <p>Toda la información médica está compilada de manera estricta del documento fuente oficial <em>Mediciones POCUS Cardiaco Adultos - Glosario</em> revisado en Julio de 2026, sin alteraciones de los rangos o unidades.</p>
            </div>
        `;
    },

    // INSTALACIÓN
    renderInstall(container) {
        container.innerHTML = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← Inicio</a>
                <h2>Instalación en iPhone (PWA)</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); font-size: 0.95rem;">
                <p style="margin-bottom: 1rem; font-weight: 600;">Sigue estos pasos para instalar esta aplicación en la pantalla de inicio de tu iPhone:</p>

                <ol style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem;">
                    <li>Abre el navegador <strong>Safari</strong> en tu iPhone e ingresa a este sitio web.</li>
                    <li>Toca el botón <strong>Compartir</strong> <span style="font-size: 1.2rem;">📤</span> (el icono de caja con flecha hacia arriba) en la barra de navegación inferior de Safari.</li>
                    <li>Desplázate hacia abajo en el menú y selecciona la opción <strong>"Agregar a pantalla de inicio"</strong>.</li>
                    <li>Confirma el nombre de la aplicación (<strong>POCUS Cardíaco</strong>) y toca <strong>"Agregar"</strong> en la esquina superior derecha.</li>
                    <li>Busca el icono de la aplicación en tu pantalla de inicio y ábrela.</li>
                </ol>

                <div class="safety-banner">
                    <strong>Nota de la PWA:</strong> Después de abrir la aplicación por primera vez con conexión a Internet, todos los datos médicos clínicos quedarán almacenados de manera segura en la memoria de tu dispositivo. Podrás consultarla sin conexión de red en cualquier momento.
                </div>
            </div>
        `;
    }
};

// Escuchar cambios de hash en la URL
window.addEventListener("hashchange", () => Router.route());
