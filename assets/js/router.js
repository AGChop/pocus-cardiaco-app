// Enrutador de la aplicación basado en Hash Routing
const Router = {
    // ${I18n.translate("label.definition")} de las rutas y sus respectivos controladores
    async route() {
        const hash = window.location.hash || '#/';
        const container = document.getElementById("app-content");

        if (!container) return;

        // Limpiar contenido previo
        container.innerHTML = `<div class="loading">${I18n.translate("state.loading_content")}</div>`;

        // 1. Ruta de Inicio
        if (hash === '#/' || hash === '#') {
            await this.renderHome(container);
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

        // Rutas de Cuestionarios
        if (hash === '#/cuestionarios') {
            await this.renderQuizzesList(container);
            return;
        }
        if (hash.startsWith('#/cuestionarios/')) {
            const id = hash.replace('#/cuestionarios/', '');
            await this.renderQuizFlow(container, id);
            return;
        }

        // Rutas de Protocolos
        if (hash === '#/protocolos') {
            await this.renderProtocolsList(container);
            return;
        }
        if (hash.startsWith('#/protocolos/')) {
            const id = hash.replace('#/protocolos/', '');
            await this.renderProtocolDetail(container, id);
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

    toggleFav(type, id, title, btnId) {
        const added = Storage.toggleFavorite(type, id, title);
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.innerHTML = added
                ? `★ ${I18n.translate("action.remove_favorite")}`
                : `☆ ${I18n.translate("action.save_favorite")}`;
        }
    },

    // --- RENDERIZADORES DE VISTAS ---

    // Menú Principal
    async renderHome(container) {
        let quizzes = [];
        try {
            quizzes = await DataLoader.getQuizzes();
        } catch (e) {
            console.warn("Router: Error al cargar cuestionarios para renderHome:", e);
        }

        if (!Array.isArray(quizzes)) {
            quizzes = [];
        }

        const approvedQuizzes = quizzes.filter(q => q.review_status === "approved" && QuizEngine.validateQuizDefinition(q));
        const showQuizzesCard = approvedQuizzes.length > 0;

        container.innerHTML = `
            <div style="text-align: center; margin-bottom: 1.5rem; margin-top: 1rem;">
                <p style="font-size: 0.95rem; color: var(--text-muted-light);">
                    ${I18n.translate("label.sub_menu_desc")}
                </p>
            </div>

            <div class="main-nav">
                <a href="#/glosario" class="nav-card">
                    <h2>${I18n.translate("nav.glossary")}</h2>
                    <p>${I18n.translate("label.glossary_desc")}</p>
                </a>
                <a href="#/mediciones" class="nav-card">
                    <h2>${I18n.translate("nav.measurements")}</h2>
                    <p>${I18n.translate("label.measurements_desc")}</p>
                </a>
                <a href="#/ventanas" class="nav-card">
                    <h2>${I18n.translate("nav.windows")}</h2>
                    <p>${I18n.translate("label.windows_desc")}</p>
                </a>
                <a href="#/protocolos" class="nav-card">
                    <h2>${I18n.translate("nav.protocols")}</h2>
                    <p>${I18n.translate("label.protocols_desc")}</p>
                </a>
                ${showQuizzesCard ? `
                <a href="#/cuestionarios" class="nav-card">
                    <h2>${I18n.translate("label.quizzes")}</h2>
                    <p>${I18n.translate("label.quizzes_desc")}</p>
                </a>` : ''}
            </div>

            <div class="secondary-nav" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem;">
                <a href="#/abreviaturas" class="btn-secondary">${I18n.translate("label.abbreviation")}</a>
                <a href="#/clasificaciones" class="btn-secondary">${I18n.translate("label.classification")}</a>
                <a href="#/conjunto-minimo" class="btn-secondary">${I18n.translate("label.minimum_set")}</a>
                <a href="#/unidades-y-errores" class="btn-secondary">${I18n.translate("label.unit_warnings")}</a>
                <a href="#/favoritos" class="btn-secondary">${I18n.translate("nav.favorites")}</a>
                <a href="#/recientes" class="btn-secondary">${I18n.translate("nav.recents")}</a>
                <a href="#/referencias" class="btn-secondary">${I18n.translate("label.clinical_references_title")}</a>
                <a href="#/acerca" class="btn-secondary">${I18n.translate("nav.about")}</a>
            </div>

            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="#/instalar" class="btn-install">${I18n.translate("label.inst_iphone")}</a>
            </div>
        `;
    },

    // 404 - No Encontrado
    render404(container) {
        container.innerHTML = `
            <div class="card error-card">
                <h2>${I18n.translate("error.not_found_title")}</h2>
                <p>${I18n.translate("error.not_found_message")}</p>
                <a href="#/" class="btn-primary">${I18n.translate("error.go_home")}</a>
            </div>
        `;
    },

    // GLOSARIO DE TÉRMINOS
    async renderGlossaryList(container) {
        const glossary = await DataLoader.getGlossary() || [];
        const escapeHTML = (str) => {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const getLocalizedAliases = (aliases) => {
            if (!aliases) return [];
            if (Array.isArray(aliases)) return aliases;
            if (typeof aliases === "object") {
                const activeLang = I18n.getLanguage();
                return aliases[activeLang] || aliases["es"] || aliases["en"] || [];
            }
            return [];
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("nav.glossary")}</h2>
            </div>

            <div class="content-accordion-grid cards-list">
        `;

        glossary.forEach(item => {
            const isFav = Storage.isFavorite("término", item.id);
            const termLoc = I18n.localize(item.term);
            const defLoc = I18n.localize(item.definition);
            const utilLoc = I18n.localize(item.acquisition_utility_limitation);
            const catLoc = I18n.localize(item.category);
            const activeAliases = getLocalizedAliases(item.aliases);

            const copyData = `${I18n.translate("label.term")}: ${termLoc}\n${I18n.translate("label.definition")}: ${defLoc}\n${I18n.translate("label.acquisition_details")}: ${utilLoc}\n${I18n.translate("label.references")}: ${item.source_document} (P. ${item.source_page})`;

            html += `
                <details class="content-accordion glossary-accordion card clinical-card">
                    <summary class="content-accordion-summary">
                        <span class="content-accordion-title">${escapeHTML(termLoc)}</span>
                        <span class="content-accordion-arrow"></span>
                    </summary>
                    <div class="content-accordion-body">
                        ${catLoc ? `<p><strong>${I18n.translate("label.categoria")}:</strong> ${escapeHTML(catLoc)}</p>` : ''}
                        <p class="card-definition"><strong>${I18n.translate("label.definition")}:</strong> ${escapeHTML(defLoc)}</p>
                        <p class="card-acquisition"><strong>${I18n.translate("label.acquisition_details")}:</strong> ${escapeHTML(utilLoc)}</p>
                        ${activeAliases && activeAliases.length > 0 ? `<p class="card-aliases"><strong>${I18n.translate("label.sinonimos")}:</strong> ${escapeHTML(activeAliases.join(", "))}</p>` : ''}
                        <div class="card-meta">${I18n.translate("label.origen")}: ${item.source_page}</div>
                        <div class="card-actions">
                            <a href="#/glosario/${item.id}" class="btn-card-action">${I18n.translate("label.detalles")}</a>
                            <button class="btn-card-action" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-m-t-${item.id}')" id="copy-m-t-${item.id}">${I18n.translate("label.copiar")}</button>
                            <button class="btn-card-action" onclick="Router.toggleFav('término', '${item.id}', '${termLoc.replace(/'/g, "\\'")}', 'fav-t-${item.id}')" id="fav-t-${item.id}">
                                ${isFav ? "★ " + I18n.translate("label.quitar") : "☆ " + I18n.translate("label.favorito")}
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

    // DETALLE DE TÉRMINO
    async renderGlossaryDetail(container, id) {
        const glossary = await DataLoader.getGlossary() || [];
        const term = glossary.find(item => item.id === id);

        if (!term) {
            this.render404(container);
            return;
        }

        const escapeHTML = (str) => {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const getLocalizedAliases = (aliases) => {
            if (!aliases) return [];
            if (Array.isArray(aliases)) return aliases;
            if (typeof aliases === "object") {
                const activeLang = I18n.getLanguage();
                return aliases[activeLang] || aliases["es"] || aliases["en"] || [];
            }
            return [];
        };

        const termLoc = I18n.localize(term.term);
        const defLoc = I18n.localize(term.definition);
        const utilLoc = I18n.localize(term.acquisition_utility_limitation);
        const catLoc = I18n.localize(term.category);
        const activeAliases = getLocalizedAliases(term.aliases);

        Storage.addRecent("término", term.id, termLoc);
        const isFav = Storage.isFavorite("término", term.id);
        const copyData = `${I18n.translate("label.term")}: ${termLoc}\n${I18n.translate("label.definition")}: ${defLoc}\n${I18n.translate("label.acquisition_details")}: ${utilLoc}\n${I18n.translate("label.references")}: ${term.source_document} (P. ${term.source_page})`;

        let html = `
            <div class="navigation-header">
                <a href="#/glosario" class="btn-back">← ${I18n.translate("nav.glossary")}</a>
                <h2>${escapeHTML(termLoc)}</h2>
            </div>

            <div class="card clinical-detail-card">
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.categoria")}</span>
                    <span class="detail-value">${escapeHTML(catLoc)}</span>
                </div>
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.definition")}</span>
                    <p class="detail-text">${escapeHTML(defLoc)}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.acquisition_details")}</span>
                    <p class="detail-text">${escapeHTML(utilLoc)}</p>
                </div>
                ${activeAliases && activeAliases.length > 0 ? `
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.sinonimos")}</span>
                    <p class="detail-text">${escapeHTML(activeAliases.join(", "))}</p>
                </div>` : ''}
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.references")}</span>
                    <p class="detail-text">${escapeHTML(term.source_document)} (P. ${term.source_page})</p>
                </div>

                <div class="detail-actions">
                    <button class="btn-primary" onclick="Router.copyText(\`${copyData.replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`, 'copy-det-t')" id="copy-det-t">${I18n.translate("label.copiar")} Contenido</button>
                    <button class="btn-secondary" onclick="Router.toggleFav('término', '${term.id}', '${termLoc.replace(/'/g, "\\'")}', 'fav-det-t')" id="fav-det-t">
                        ${isFav ? "★ " + I18n.translate("label.quitar") + " " + I18n.translate("label.favorito") : "☆ " + I18n.translate("action.save_favorite")}
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    // BANCO DE MEDICIONES - SECCIONES
    async renderMeasurementsSections(container) {
        const sections = await DataLoader.getSections() || [];
        const escapeHTML = (str) => {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("nav.measurements")}</h2>
            </div>
            <div class="sections-list">
        `;

        sections.forEach(sec => {
            const titleLoc = I18n.localize(sec.title);
            const descLoc = I18n.localize(sec.description);
            const warningLoc = I18n.localize(sec.clinical_warning);

            html += `
                <a href="#/mediciones/${sec.id}" class="section-card">
                    <div class="section-num">${I18n.translate("label.section")} ${sec.number}</div>
                    <h3>${escapeHTML(titleLoc)}</h3>
                    <p>${escapeHTML(descLoc)}</p>
                    ${warningLoc ? `<span class="warning-badge">⚠️ ${I18n.translate("label.clinical_warning")}</span>` : ''}
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

        const escapeHTML = (str) => {
            if (str === null || str === undefined) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const shortTitleLoc = I18n.localize(section.short_title);
        const warningLoc = I18n.localize(section.clinical_warning);

        const labelSection = escapeHTML(I18n.translate("label.section"));
        const labelSafetyWarning = escapeHTML(I18n.translate("label.clinical_warning"));
        const labelFormulaMethod = escapeHTML(I18n.translate("label.formula_or_method"));
        const labelNormalValues = escapeHTML(I18n.translate("label.normal_values"));
        const labelLimitations = escapeHTML(I18n.translate("label.interpretation_limitations"));
        const labelOrigin = escapeHTML(I18n.translate("label.origen"));
        const labelDetails = escapeHTML(I18n.translate("label.detalles"));
        const labelCopy = escapeHTML(I18n.translate("label.copiar"));
        const labelRemove = escapeHTML(I18n.translate("label.quitar"));
        const labelFav = escapeHTML(I18n.translate("label.favorito"));

        let html = `
            <div class="navigation-header">
                <a href="#/mediciones" class="btn-back">← ${escapeHTML(I18n.translate("nav.measurements"))}</a>
                <h2>${labelSection} ${section.number}: ${escapeHTML(shortTitleLoc)}</h2>
            </div>

            ${warningLoc ? `
            <div class="safety-banner" role="alert">
                <strong>${labelSafetyWarning}:</strong> ${escapeHTML(warningLoc)}
            </div>` : ''}

            <div class="measurements-grid cards-list">
        `;

        const encodeInlineValue = (value) =>
            encodeURIComponent(String(value ?? "")).replace(/'/g, "%27");

        filtered.forEach(item => {
            const isFav = Storage.isFavorite("medición", item.id);
            const measurementLoc = I18n.localize(item.measurement);
            const formulaLoc = I18n.localize(item.formula_or_method);
            const normalValuesLoc = I18n.localize(item.normal_values);
            const limitationsLoc = I18n.localize(item.interpretation_limitations);
            const unitsLoc = I18n.localize(item.units);
            const priorityTier = Number(item.priority_tier) || 99;
            const priorityLabel = item.priority_label || "Sin priorizar";

            const copyData =
                `${I18n.translate("label.measurement")}: ${measurementLoc}\n` +
                `${labelFormulaMethod}: ${formulaLoc}\n` +
                `${labelNormalValues}: ${normalValuesLoc}\n` +
                `${labelLimitations}: ${limitationsLoc}\n` +
                `${escapeHTML(I18n.translate("label.unidades"))}: ${unitsLoc}\n` +
                `${escapeHTML(I18n.translate("label.references"))}: ${item.source_document} (P. ${item.source_page})`;

            const encodedCopy = encodeInlineValue(copyData);
            const encodedMeas = encodeInlineValue(measurementLoc);
            const encodedItemId = encodeInlineValue(item.id);

            html += `
                <details class="measurement-accordion card clinical-card">
                    <summary class="accordion-summary">
                        <span class="measurement-title">${escapeHTML(measurementLoc)}</span>
                        <span class="accordion-arrow"></span>
                    </summary>
                    <div class="measurement-accordion-content">
                        <div class="measurement-header-content">
                            <span class="priority-badge priority-tier-${priorityTier}">${escapeHTML(priorityLabel)}</span>
                            <span class="unit-badge">${escapeHTML(unitsLoc)}</span>
                        </div>
                        <p><strong>${labelFormulaMethod}:</strong> ${escapeHTML(formulaLoc)}</p>
                        <p class="normal-values"><strong>${labelNormalValues}:</strong> ${escapeHTML(normalValuesLoc)}</p>
                        <p class="limitations"><strong>${labelLimitations}:</strong> ${escapeHTML(limitationsLoc)}</p>
                        <div class="card-meta">${labelOrigin}: ${escapeHTML(item.source_page)}</div>
                        <div class="card-actions">
                            <a href="#/medicion/${escapeHTML(item.id)}" class="btn-card-action">${labelDetails}</a>
                            <button class="btn-card-action" onclick="Router.copyText(decodeURIComponent('${encodedCopy}'), 'copy-m-m-${escapeHTML(item.id)}')" id="copy-m-m-${escapeHTML(item.id)}">${labelCopy}</button>
                            <button class="btn-card-action" onclick="Router.toggleFav('medición', decodeURIComponent('${encodedItemId}'), decodeURIComponent('${encodedMeas}'), 'fav-m-${escapeHTML(item.id)}')" id="fav-m-${escapeHTML(item.id)}">
                                ${isFav ? "★ " + labelRemove : "☆ " + labelFav}
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
        const mediaResources = await DataLoader.getMediaResources() || [];
        const item = measurements.find(m => m.id === id);

        if (!item) {
            this.render404(container);
            return;
        }

        const escapeHTML = (value) => {
            if (value === null || value === undefined) return "";
            return String(value)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const getLocalizedList = (value) => {
            if (!value) return [];
            if (Array.isArray(value)) {
                return value.map(val => I18n.localize(val)).filter(Boolean);
            }
            if (typeof value === "object") {
                const activeLang = I18n.getLanguage();
                const list = value[activeLang] || value["es"] || value["en"] || [];
                return Array.isArray(list) ? list.map(val => I18n.localize(val)).filter(Boolean) : [];
            }
            return [];
        };

        const collectTextVariants = (value) => {
            if (value === null || value === undefined) return [];
            if (typeof value === "string") {
                const s = value.trim();
                return s ? [s] : [];
            }
            if (Array.isArray(value)) {
                let res = [];
                value.forEach(sub => {
                    res = res.concat(collectTextVariants(sub));
                });
                return res;
            }
            if (typeof value === "object") {
                let res = [];
                for (const key in value) {
                    if (Object.prototype.hasOwnProperty.call(value, key)) {
                        res = res.concat(collectTextVariants(value[key]));
                    }
                }
                return res;
            }
            return [];
        };

        const normalizeComparable = (value) => {
            if (value === null || value === undefined) return "";
            return String(value)
                .trim()
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/\s+/g, " ");
        };

        const getLinkForWindow = (primary, view) => {
            const primaryVariants = collectTextVariants(primary).map(normalizeComparable);
            const viewVariants = collectTextVariants(view).map(normalizeComparable);

            const checkMatch = (variants, keywords) => {
                return variants.some(v => keywords.some(k => v.includes(k)));
            };

            if (checkMatch(viewVariants, ["plax"])) return "plax";
            if (checkMatch(viewVariants, ["psax"])) return "psax";
            if (checkMatch(viewVariants, ["a4c-vd", "enfoque vd", "enfocada en vd", "rv-focused a4c"])) return "rv_focused_a4c";
            if (checkMatch(viewVariants, ["a4c", "4c"])) return "a4c";
            if (checkMatch(viewVariants, ["a2c", "2c"])) return "a2c";
            if (checkMatch(viewVariants, ["a3c", "3c"])) return "a3c";
            if (checkMatch(viewVariants, ["a5c", "5c"])) return "a5c";
            if (checkMatch(viewVariants, ["vci", "cava", "ivc"])) return "subcostal_ivc";
            if (checkMatch(viewVariants, ["subcostal 4c", "sc4c"])) return "subcostal_4c";
            if (checkMatch(viewVariants, ["inflow", "entrada vd", "rv inflow"])) return "rv_inflow";
            if (checkMatch(primaryVariants, ["derecha", "right parasternal", "rps"]) || checkMatch(viewVariants, ["rps"])) return "right_parasternal";
            if (checkMatch(primaryVariants, ["supraesternal", "ssn", "suprasternal"]) || checkMatch(viewVariants, ["ssn"])) return "suprasternal";
            if (checkMatch(primaryVariants, ["subcostal"])) return "subcostal_4c";
            if (checkMatch(primaryVariants, ["paraesternal"])) return "plax";

            return null;
        };

        const measurementLoc = I18n.localize(item.measurement);
        const formulaLoc = I18n.localize(item.formula_or_method);
        const normalValuesLoc = I18n.localize(item.normal_values);
        const limitationsLoc = I18n.localize(item.interpretation_limitations);
        const unitsLoc = I18n.localize(item.units);
        const priorityTier = Number(item.priority_tier) || 99;
        const priorityLabel = item.priority_label || "Sin priorizar";
        const primaryWindowLoc = I18n.localize(item.primary_window);
        const preferredViewLoc = I18n.localize(item.preferred_view);
        const modalityLoc = I18n.localize(item.modality);
        const acquisitionTimingLoc = I18n.localize(item.acquisition_timing);
        const acquisitionKeyLoc = I18n.localize(item.acquisition_key);
        const activeAliases = getLocalizedList(item.aliases);
        const activeAlternateWindows = getLocalizedList(item.alternate_windows);

        Storage.addRecent("medición", item.id, measurementLoc);
        const isFav = Storage.isFavorite("medición", item.id);

        const copyData =
            `${I18n.translate("label.measurement")}: ${measurementLoc}\n` +
            `${I18n.translate("label.formula_or_method")}: ${formulaLoc}\n` +
            `${I18n.translate("label.normal_values")}: ${normalValuesLoc}\n` +
            `${I18n.translate("label.interpretation_limitations")}: ${limitationsLoc}\n` +
            `${I18n.translate("label.unidades")}: ${unitsLoc}\n` +
            `${I18n.translate("label.references")}: ${item.source_document} (P. ${item.source_page})`;

        const encodeInlineValue = (value) =>
            encodeURIComponent(String(value ?? "")).replace(/'/g, "%27");

        const encodedCopyData = encodeInlineValue(copyData);
        const encodedMeasurementTitle = encodeInlineValue(measurementLoc);
        const encodedItemId = encodeInlineValue(item.id);

        const relatedMedia = MediaViewer.getMediaForEntity(mediaResources, 'measurement', item.id);
        const mediaHTML = MediaViewer.renderMediaSection(relatedMedia);

        const labelSection = escapeHTML(I18n.translate("label.section"));
        const labelAcqTechHeader = escapeHTML(I18n.localize({
            es: "Ventana y técnica recomendadas",
            en: "Recommended view and acquisition technique"
        }));
        const labelPrimaryWin = escapeHTML(I18n.translate("label.primary_window"));
        const labelPreferredView = escapeHTML(I18n.translate("label.preferred_view"));
        const labelModality = escapeHTML(I18n.translate("label.modality"));
        const labelAcqTiming = escapeHTML(I18n.translate("label.acquisition_timing"));
        const labelAcqKey = escapeHTML(I18n.translate("label.acquisition_key"));
        const labelAltWindows = escapeHTML(I18n.translate("label.alternate_windows"));

        const labelNoAlts = escapeHTML(I18n.localize({
            es: "No se especifican ventanas alternativas.",
            en: "No alternate windows are specified."
        }));

        let windowsHtml = "";
        const hasAlternate = activeAlternateWindows.length > 0;

        if (primaryWindowLoc || preferredViewLoc || modalityLoc || acquisitionTimingLoc || acquisitionKeyLoc || hasAlternate) {
            let altWindowsContent = "";
            if (!hasAlternate) {
                altWindowsContent = `<p class="detail-text">${labelNoAlts}</p>`;
            } else if (activeAlternateWindows.length === 1) {
                altWindowsContent = `<p class="detail-text">${escapeHTML(activeAlternateWindows[0])}</p>`;
            } else {
                altWindowsContent = `<ul class="detail-list" style="margin: 0.25rem 0 0 1.25rem; padding-left: 0; color: var(--text-main-light); list-style-type: disc;">
                    ${activeAlternateWindows.map(win => `<li style="margin-bottom: 0.25rem;">${escapeHTML(win)}</li>`).join("")}
                </ul>`;
            }

            const winId = getLinkForWindow(item.primary_window, item.preferred_view);
            const primaryWindowHTML = winId
                ? `<a href="#/ventanas/${escapeHTML(winId)}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(primaryWindowLoc)}</a>`
                : escapeHTML(primaryWindowLoc);

            windowsHtml = `
                <div class="card-section-divider" style="margin: 0.5rem 0; border-top: 1px dashed var(--border-light);"></div>
                <details style="margin-top: 0.5rem;">
                    <summary style="font-size: 1.1rem; font-weight: 600; color: var(--primary-medium); cursor: pointer; padding: 0.25rem 0; outline: none; user-select: none;">
                        ${labelAcqTechHeader}
                    </summary>
                    <div style="display: flex; flex-direction: column; gap: 1.25rem; margin-top: 0.75rem; padding-left: 0.25rem;">
                        ${primaryWindowLoc ? `
                        <div class="card-section">
                            <span class="detail-label">${labelPrimaryWin}</span>
                            <p class="detail-text">${primaryWindowHTML}</p>
                        </div>` : ''}

                        ${preferredViewLoc ? `
                        <div class="card-section">
                            <span class="detail-label">${labelPreferredView}</span>
                            <p class="detail-text">${escapeHTML(preferredViewLoc)}</p>
                        </div>` : ''}

                        ${modalityLoc ? `
                        <div class="card-section">
                            <span class="detail-label">${labelModality}</span>
                            <p class="detail-text">${escapeHTML(modalityLoc)}</p>
                        </div>` : ''}

                        ${acquisitionTimingLoc ? `
                        <div class="card-section">
                            <span class="detail-label">${labelAcqTiming}</span>
                            <p class="detail-text">${escapeHTML(acquisitionTimingLoc)}</p>
                        </div>` : ''}

                        ${acquisitionKeyLoc ? `
                        <div class="card-section">
                            <span class="detail-label">${labelAcqKey}</span>
                            <p class="detail-text" style="font-style: italic;">${escapeHTML(acquisitionKeyLoc)}</p>
                        </div>` : ''}

                        <div class="card-section">
                            <span class="detail-label">${labelAltWindows}</span>
                            ${altWindowsContent}
                        </div>
                    </div>
                </details>
            `;
        }

        const labelMethod = escapeHTML(I18n.translate("label.formula_or_method"));
        const labelRefValues = escapeHTML(I18n.translate("label.reference_values"));
        const labelUnits = escapeHTML(I18n.translate("label.unidades"));
        const labelLimitLabel = escapeHTML(I18n.translate("label.interpretation_limitations"));
        const labelAliases = escapeHTML(I18n.translate("label.sinonimos"));
        const labelRef = escapeHTML(I18n.translate("label.references"));
        const labelCopy = escapeHTML(I18n.translate("label.copiar"));
        const labelRemove = escapeHTML(I18n.translate("label.quitar"));
        const labelSaveFav = escapeHTML(I18n.translate("action.save_favorite"));

        let html = `
            <div class="navigation-header">
                <a href="#/mediciones/${escapeHTML(item.section_id)}" class="btn-back">← ${labelSection}</a>
                <h2>${escapeHTML(measurementLoc)}</h2>
            </div>

            <div class="card clinical-detail-card">
                <div class="measurement-header-content">
                    <span class="priority-badge priority-tier-${priorityTier}">${escapeHTML(priorityLabel)}</span>
                </div>
                <div class="card-section">
                    <span class="detail-label">${labelMethod}</span>
                    <p class="detail-text">${escapeHTML(formulaLoc)}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">${labelRefValues}</span>
                    <p class="detail-text highlight-text">${escapeHTML(normalValuesLoc)}</p>
                </div>
                <div class="card-section">
                    <span class="detail-label">${labelUnits}</span>
                    <span class="unit-badge large-badge">${escapeHTML(unitsLoc)}</span>
                </div>
                ${mediaHTML ? `
                <div class="card-section media-card-section">
                    ${mediaHTML}
                </div>` : ''}
                <div class="card-section">
                    <span class="detail-label">${labelLimitLabel}</span>
                    <p class="detail-text warning-text">${escapeHTML(limitationsLoc)}</p>
                </div>
                ${activeAliases.length > 0 ? `
                <div class="card-section">
                    <span class="detail-label">${labelAliases}</span>
                    <p class="detail-text">${escapeHTML(activeAliases.join(", "))}</p>
                </div>` : ''}
                <div class="card-section">
                    <span class="detail-label">${labelRef}</span>
                    <p class="detail-text">${escapeHTML(item.source_document)} (P. ${escapeHTML(item.source_page)})</p>
                </div>

                ${windowsHtml}

                <div class="detail-actions">
                    <button class="btn-primary" onclick="Router.copyText(decodeURIComponent('${encodedCopyData}'), 'copy-det-m')">${labelCopy}</button>
                    <button class="btn-secondary" onclick="Router.toggleFav('medición', decodeURIComponent('${encodedItemId}'), decodeURIComponent('${encodedMeasurementTitle}'), 'fav-det-m')" id="fav-det-m">
                        ${isFav ? "★ " + labelRemove : "☆ " + labelSaveFav}
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
        MediaViewer.initializeMediaInteractions(container);
    },

    // LISTA DE VENTANAS ECOCARDIOGRÁFICAS
    async renderWindowsList(container) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let windows = [];
        try {
            windows = await DataLoader.getWindows();
            if (!windows || windows.length === 0) {
                throw new Error("No se encontraron ventanas o el archivo está vacío.");
            }
        } catch (error) {
            container.innerHTML = `
                <div class="card error-card">
                    <h2>${escapeHTML(I18n.translate("error.windows_load_title"))}</h2>
                    <p>${escapeHTML(I18n.translate("error.windows_load_text"))}</p>
                    <a href="#/" class="btn-primary">${I18n.translate("error.go_home")}</a>
                </div>
            `;
            return;
        }

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${escapeHTML(I18n.translate("nav.windows"))}</h2>
            </div>

            <div class="content-accordion-grid cards-list">
        `;

        windows.forEach(item => {
            const windowLoc = I18n.localize(item.window);
            const structLoc = I18n.localize(item.favored_structures);
            const posLoc = I18n.localize(item.typical_probe_position);
            const oriLoc = I18n.localize(item.typical_marker_orientation);
            const measLoc = I18n.localize(item.favored_measurements);

            html += `
                <details class="content-accordion window-accordion card clinical-card">
                    <summary class="content-accordion-summary">
                        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                            <span class="content-accordion-title">${escapeHTML(windowLoc)}</span>
                            ${item.abbreviation ? `<span class="unit-badge">${escapeHTML(item.abbreviation)}</span>` : ''}
                        </div>
                        <span class="content-accordion-arrow"></span>
                    </summary>
                    <div class="content-accordion-body">
                        ${structLoc ? `<p><strong>${I18n.translate("label.est_favorecidas")}:</strong> ${escapeHTML(structLoc)}</p>` : ''}
                        ${posLoc ? `<p><strong>${I18n.translate("label.pos_transductor")}:</strong> ${escapeHTML(posLoc)}</p>` : ''}
                        ${oriLoc ? `<p><strong>${I18n.translate("label.ori_marcador")}:</strong> ${escapeHTML(oriLoc)}</p>` : ''}
                        ${measLoc ? `<p><strong>${I18n.translate("label.med_asociadas")}:</strong> ${escapeHTML(measLoc)}</p>` : ''}
                        <div class="card-actions">
                            <a href="#/ventanas/${item.id}" class="btn-card-action">${I18n.translate("label.detalles")}</a>
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

    // DETALLE DE VENTANA ECOCARDIOGRÁFICA
    async renderWindowDetail(container, id) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let windows = [];
        let measurements = [];
        let mediaResources = [];
        try {
            windows = await DataLoader.getWindows() || [];
            measurements = await DataLoader.getMeasurements() || [];
            mediaResources = await DataLoader.getMediaResources() || [];
        } catch (error) {
            container.innerHTML = `
                <div class="card error-card">
                    <h2>${escapeHTML(I18n.translate("error.window_detail_load_title"))}</h2>
                    <p>${escapeHTML(I18n.translate("error.window_detail_load_text"))}</p>
                    <a href="#/ventanas" class="btn-primary">${escapeHTML(I18n.translate("nav.back_to_windows"))}</a>
                </div>
            `;
            return;
        }

        const item = windows.find(w => w.id === id);
        if (!item) {
            this.render404(container);
            return;
        }

        const relatedMedia = MediaViewer.getMediaForEntity(mediaResources, 'window', item.id);
        const mediaHTML = MediaViewer.renderMediaSection(relatedMedia);

        const collectTextVariants = (value) => {
            if (value === null || value === undefined) return [];
            if (typeof value === "string") {
                const s = value.trim();
                return s ? [s] : [];
            }
            if (Array.isArray(value)) {
                let res = [];
                value.forEach(sub => {
                    res = res.concat(collectTextVariants(sub));
                });
                return res;
            }
            if (typeof value === "object") {
                let res = [];
                for (const key in value) {
                    if (Object.prototype.hasOwnProperty.call(value, key)) {
                        res = res.concat(collectTextVariants(value[key]));
                    }
                }
                return res;
            }
            return [];
        };

        const normalizeComparable = (value) => {
            if (value === null || value === undefined) return "";
            return String(value)
                .trim()
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/\s+/g, " ");
        };

        const windowLoc = I18n.localize(item.window);
        const posLoc = I18n.localize(item.typical_probe_position);
        const oriLoc = I18n.localize(item.typical_marker_orientation);
        const structLoc = I18n.localize(item.favored_structures);
        const measLoc = I18n.localize(item.favored_measurements);

        // Relación con mediciones
        let favoredMeasurementsHTML = "";
        if (measLoc) {
            const parts = measLoc.split(",").map(p => p.trim());
            const linkedParts = parts.map(part => {
                const part_normalized = normalizeComparable(part);
                let found = null;

                for (const m of measurements) {
                    const measurementVariants = [
                        ...collectTextVariants(m.measurement),
                        ...collectTextVariants(m.abbreviation),
                        ...collectTextVariants(m.aliases)
                    ].map(normalizeComparable).filter(Boolean);

                    if (measurementVariants.includes(part_normalized)) {
                        found = m;
                        break;
                    }
                }

                if (!found) {
                    const manualMap = {
                        "dtdvi/dtsvi": "dtdvi",
                        "lvidd/lvids": "dtdvi",
                        "dtdvi": "dtdvi",
                        "lvidd": "dtdvi",
                        "dtsvi": "dtsvi",
                        "lvids": "dtsvi",
                        "ivsd": "ivsd",
                        "pwtd": "pwtd",
                        "rwt": "rwt_meas",
                        "epss": "epss",
                        "mapse": "mapse",
                        "tapse": "tapse_meas",
                        "grosor pared vd": "grosor_pared_vd",
                        "rv wall thickness": "grosor_pared_vd",
                        "planimetría mitral": "area_mitral_planimetria",
                        "mitral planimetry": "area_mitral_planimetria",
                        "diámetro tsvi": "area_tsvi_meas",
                        "lvot diameter": "area_tsvi_meas",
                        "diámetro ai": "diametro_ap_ai",
                        "la diameter": "diametro_ap_ai",
                        "lavi": "lavi_meas",
                        "flujo mitral": "onda_e_mitral",
                        "mitral flow": "onda_e_mitral",
                        "gls": "gls_vi",
                        "wmsi": "wmsi",
                        "subcostal": "derrame_pericardico_pequeno"
                    };
                    if (manualMap[part_normalized]) {
                        found = measurements.find(m => m.id === manualMap[part_normalized]);
                    }
                }

                if (found) {
                    return `<a href="#/medicion/${escapeHTML(found.id)}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(part)}</a>`;
                } else {
                    return escapeHTML(part);
                }
            });
            favoredMeasurementsHTML = linkedParts.join(", ");
        }

        const labelAbbreviation = escapeHTML(I18n.localize({
            es: "Abreviatura",
            en: "Abbreviation"
        }));

        const labelFavoredMeasurements = escapeHTML(I18n.localize({
            es: "Mediciones favorecidas",
            en: "Favored measurements"
        }));

        let html = `
            <div class="navigation-header">
                <a href="#/ventanas" class="btn-back">← ${I18n.translate("nav.windows")}</a>
                <h2>${escapeHTML(windowLoc)}</h2>
            </div>

            <div class="card clinical-detail-card">
                ${item.abbreviation ? `
                <div class="card-section">
                    <span class="detail-label">${labelAbbreviation}</span>
                    <span class="unit-badge large-badge" style="width: fit-content;">${escapeHTML(item.abbreviation)}</span>
                </div>` : ''}

                ${posLoc ? `
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.pos_transductor")}</span>
                    <p class="detail-text">${escapeHTML(posLoc)}</p>
                </div>` : ''}

                ${oriLoc ? `
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.ori_marcador")}</span>
                    <p class="detail-text">${escapeHTML(oriLoc)}</p>
                </div>` : ''}

                ${structLoc ? `
                <div class="card-section">
                    <span class="detail-label">${I18n.translate("label.est_favorecidas")}</span>
                    <p class="detail-text">${escapeHTML(structLoc)}</p>
                </div>` : ''}

                ${mediaHTML ? `
                <div class="card-section media-card-section">
                    ${mediaHTML}
                </div>` : ''}

                ${favoredMeasurementsHTML ? `
                <div class="card-section">
                    <span class="detail-label">${labelFavoredMeasurements}</span>
                    <p class="detail-text">${favoredMeasurementsHTML}</p>
                </div>` : ''}
            </div>
        `;

        container.innerHTML = html;
        MediaViewer.initializeMediaInteractions(container);
    },

    // LISTADO DE PROTOCOLOS
    async renderProtocolsList(container) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let data = null;
        try {
            data = await DataLoader.fetchResource("protocols");
            if (!data || !data.protocols || data.protocols.length === 0) {
                throw new Error("No se encontraron protocolos o el archivo está vacío.");
            }
        } catch (error) {
            console.error("Error al cargar protocolos:", error);
            container.innerHTML = `
                <div class="card error-card">
                    <h2>${escapeHTML(I18n.translate("error.protocols_load_title"))}</h2>
                    <p>${escapeHTML(I18n.translate("error.protocols_load_text"))}</p>
                    <a href="#/" class="btn-primary">${I18n.translate("error.go_home")}</a>
                </div>
            `;
            return;
        }

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("nav.protocols")}</h2>
            </div>

            <div class="safety-banner" role="alert">
                ${I18n.translate("safety.notice")}
            </div>

            <div style="margin-bottom: 1.5rem;">
                <p style="font-size: 0.95rem; color: var(--text-muted-light);">
                    ${I18n.translate("label.protocols_desc")}
                </p>
            </div>

            <div class="content-accordion-grid cards-list">
        `;

        data.protocols.forEach(proto => {
            const protoName = I18n.localize({ es: proto.name_es, en: proto.name_en });
            const purposeLoc = I18n.localize(proto.purpose);
            const contextLoc = I18n.localize(proto.clinical_context);
            const targetLoc = I18n.localize(proto.target_population);
            const compNames = proto.components.map(c => I18n.localize({ es: c.name_es, en: c.name_en })).join(", ");
            const purposeLabel = I18n.translate("label.clinical_purpose_label");
            const contextLabel = I18n.translate("label.clinical_context");
            const targetLabel = I18n.translate("label.target_population");
            const compLabel = I18n.translate("label.components");

            html += `
                <details class="content-accordion protocol-accordion card clinical-card">
                    <summary class="content-accordion-summary">
                        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                            <span class="content-accordion-title">${escapeHTML(protoName)}</span>
                            <span class="unit-badge">${escapeHTML(proto.acronym)}</span>
                        </div>
                        <span class="content-accordion-arrow"></span>
                    </summary>
                    <div class="content-accordion-body">
                        <p><strong>${escapeHTML(purposeLabel)}:</strong> ${escapeHTML(purposeLoc)}</p>
                        <p><strong>${escapeHTML(contextLabel)}:</strong> ${escapeHTML(contextLoc)}</p>
                        <p><strong>${escapeHTML(targetLabel)}:</strong> ${escapeHTML(targetLoc)}</p>
                        <p><strong>${escapeHTML(compLabel)}:</strong> ${escapeHTML(compNames)}</p>
                        <div class="card-actions">
                            <a href="#/protocolos/${proto.id}" class="btn-card-action">${I18n.translate("label.detalles")}</a>
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

    get uiStrings() {
        return {
            guideTab: I18n.translate("label.guide_tab"),
            contentTab: I18n.translate("label.content_tab"),
            referencesTab: I18n.translate("label.references_tab"),
            previousBtn: I18n.translate("label.previous_btn"),
            nextBtn: I18n.translate("label.next_btn"),
            resetBtn: I18n.translate("label.reset_btn"),
            finishedBtn: I18n.translate("label.finished_btn"),
            startStep: I18n.translate("label.start_step"),
            integrationStep: I18n.translate("label.integration_step"),
            summaryStep: I18n.translate("label.summary_step"),
            stepIndicator: I18n.translate("label.step_indicator"),
            itemNotAvailable: I18n.translate("label.item_not_available"),
            noLinkedItems: I18n.translate("label.no_linked_items"),
            clinicalWarningsTitle: I18n.translate("label.clinical_warnings_title"),
            clinicalPurposeLabel: I18n.translate("label.clinical_purpose_label"),
            clinicalIntegrationLabel: I18n.translate("label.clinical_integration_label"),
            clinicalSafetyLabel: I18n.translate("label.clinical_safety_label"),
            clinicalWindowLabel: I18n.translate("label.clinical_window_label"),
            clinicalMeasurementLabel: I18n.translate("label.clinical_measurement_label"),
            clinicalViewsLabel: I18n.translate("label.clinical_views_label"),
            clinicalQuestionsLabel: I18n.translate("label.clinical_questions_label"),
            clinicalTargetsLabel: I18n.translate("label.clinical_targets_label"),
            clinicalFindingsLabel: I18n.translate("label.clinical_findings_label"),
            clinicalLimitsLabel: I18n.translate("label.clinical_limits_label"),
            clinicalSequenceTitle: I18n.translate("label.clinical_sequence_title"),
            clinicalGeneralLimitsTitle: I18n.translate("label.clinical_general_limits_title"),
            clinicalSafetyWorkflowTitle: I18n.translate("label.clinical_safety_workflow_title"),
            clinicalReferencesTitle: I18n.translate("label.clinical_references_title"),
            clinicalReturnToListBtn: I18n.translate("label.clinical_return_to_list_btn"),
            clinicalReturnHomeBtn: I18n.translate("label.clinical_return_home_btn"),
            errorLoadingTitle: I18n.translate("label.error_loading_title"),
            errorLoadingText: I18n.translate("label.error_loading_text"),
            errorLoadingBackBtn: I18n.translate("label.error_loading_back_btn")
        };
    },

    buildProtocolGuideSteps(protocol) {
        const steps = [];
        steps.push({
            type: "start",
            title: Router.uiStrings.startStep,
            name: I18n.localize({ es: protocol.name_es, en: protocol.name_en }),
            acronym: protocol.acronym,
            purpose: I18n.localize(protocol.purpose),
            clinical_context: I18n.localize(protocol.clinical_context),
            target_population: I18n.localize(protocol.target_population),
            sequence_note: I18n.localize(protocol.sequence_note)
        });

        protocol.components.forEach(comp => {
            steps.push({
                type: "component",
                title: I18n.localize({ es: comp.name_es, en: comp.name_en }),
                component: {
                    ...comp,
                    clinical_questions: (comp.clinical_questions || []).map(q => I18n.localize(q)),
                    targets: (comp.targets || []).map(t => I18n.localize(t)),
                    suggested_views: (comp.suggested_views || []).map(v => I18n.localize(v)),
                    possible_findings: (comp.possible_findings || []).map(f => I18n.localize(f)),
                    interpretation_limits: I18n.localize(comp.interpretation_limits)
                }
            });
        });

        steps.push({
            type: "integration",
            title: Router.uiStrings.integrationStep,
            integration: I18n.localize(protocol.integration)
        });

        steps.push({
            type: "summary",
            title: Router.uiStrings.summaryStep,
            limitations: I18n.localize(protocol.limitations),
            safety_and_workflow_notes: I18n.localize(protocol.safety_and_workflow_notes),
            components_names: protocol.components.map(c => I18n.localize({ es: c.name_es, en: c.name_en }))
        });

        return steps;
    },

    renderProtocolFlowMap(steps, helpers) {
        const { escapeHTML, resolveWindowLink, resolveMeasurementLink } = helpers;

        let html = `
        <section class="protocol-flow-map" aria-labelledby="protocol-flow-title-id">
            <div class="protocol-flow-shell">
                <h3 id="protocol-flow-title-id" class="protocol-flow-title">${escapeHTML(I18n.translate("label.protocol_flow_title"))}</h3>
                <p class="protocol-flow-description">${escapeHTML(I18n.translate("label.protocol_flow_description"))}</p>
                <h4 id="protocol-flow-path-title-id" class="sr-only">${escapeHTML(I18n.translate("label.protocol_flow_path_title"))}</h4>
                <ol class="protocol-flow-list" aria-labelledby="protocol-flow-path-title-id">
        `;

        steps.forEach((step, idx) => {
            const isOpen = idx === 0 ? "open" : "";
            const stepTitle = step.title || step.name;
            const buttonLabel = `${I18n.translate("label.protocol_flow_go_to_step")} - ${stepTitle}`;

            html += `
            <li class="protocol-flow-item">
                <details class="protocol-flow-card" ${isOpen}>
                    <summary class="protocol-flow-summary">
                        <span>${escapeHTML(stepTitle)}</span>
                    </summary>
                    <div class="protocol-flow-details-content">
            `;

            if (step.type === "start") {
                const contextLabel = I18n.translate("label.clinical_context") + ":";
                const targetLabel = I18n.translate("label.target_population") + ":";
                const sequenceLabel = I18n.translate("label.acquisition_sequence") + ":";
                html += `
                        <ul class="protocol-flow-subflow">
                            <li class="protocol-flow-stage"><strong>${escapeHTML(Router.uiStrings.clinicalPurposeLabel)}:</strong> ${escapeHTML(step.purpose)}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(contextLabel)}</strong> ${escapeHTML(step.clinical_context)}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(targetLabel)}</strong> ${escapeHTML(step.target_population)}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(sequenceLabel)}</strong> ${escapeHTML(step.sequence_note)}</li>
                        </ul>
                `;
            } else if (step.type === "component") {
                const comp = step.component;
                const linkedWindowsHTML = comp.linked_window_ids && comp.linked_window_ids.length > 0
                    ? comp.linked_window_ids.map(wId => resolveWindowLink(wId)).join(", ")
                    : escapeHTML(Router.uiStrings.noLinkedItems);

                const linkedMeasurementsHTML = comp.linked_measurement_ids && comp.linked_measurement_ids.length > 0
                    ? comp.linked_measurement_ids.map(mId => resolveMeasurementLink(mId)).join(", ")
                    : escapeHTML(Router.uiStrings.noLinkedItems);

                const questionsHeader = Router.uiStrings.clinicalQuestionsLabel + ":";
                const viewsHeader = Router.uiStrings.clinicalViewsLabel + ":";
                const targetsHeader = Router.uiStrings.clinicalTargetsLabel + ":";
                const findingsHeader = Router.uiStrings.clinicalFindingsLabel + ":";
                const limitsHeader = Router.uiStrings.clinicalLimitsLabel + ":";

                html += `
                        <ul class="protocol-flow-subflow">
                            <li class="protocol-flow-stage">
                                <strong>${escapeHTML(questionsHeader)}</strong>
                                <ul>
                                    ${comp.clinical_questions.map(q => `<li>${escapeHTML(q)}</li>`).join("")}
                                </ul>
                            </li>
                            <li class="protocol-flow-stage">
                                <strong>${escapeHTML(viewsHeader)}</strong> ${comp.suggested_views.map(v => escapeHTML(v)).join(", ")}
                            </li>
                            <li class="protocol-flow-stage">
                                <strong>${escapeHTML(targetsHeader)}</strong>
                                <ul>
                                    ${comp.targets.map(t => `<li>${escapeHTML(t)}</li>`).join("")}
                                </ul>
                                <div class="protocol-flow-linked-items">
                                    <strong>${escapeHTML(Router.uiStrings.clinicalWindowLabel)}:</strong> ${linkedWindowsHTML}<br>
                                    <strong>${escapeHTML(Router.uiStrings.clinicalMeasurementLabel)}:</strong> ${linkedMeasurementsHTML}
                                </div>
                            </li>
                            <li class="protocol-flow-stage">
                                <strong>${escapeHTML(findingsHeader)}</strong>
                                <ul>
                                    ${comp.possible_findings.map(f => `<li>${escapeHTML(f)}</li>`).join("")}
                                </ul>
                            </li>
                            <li class="protocol-flow-stage">
                                <strong>${escapeHTML(limitsHeader)}</strong> ${escapeHTML(comp.interpretation_limits)}
                            </li>
                        </ul>
                `;
            } else if (step.type === "integration") {
                html += `
                        <ul class="protocol-flow-subflow">
                            <li class="protocol-flow-stage"><strong>${escapeHTML(Router.uiStrings.integrationStep)}:</strong> ${escapeHTML(step.integration)}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(I18n.translate("label.reminder"))}:</strong> ${escapeHTML(I18n.translate("label.reminder_text"))}</li>
                        </ul>
                `;
            } else if (step.type === "summary") {
                html += `
                        <ul class="protocol-flow-subflow">
                            <li class="protocol-flow-stage"><strong>${escapeHTML(I18n.translate("label.protocol_guide_completed"))}:</strong> ${step.components_names.map(name => escapeHTML(name)).join(", ")}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(Router.uiStrings.clinicalGeneralLimitsTitle)}:</strong> ${escapeHTML(step.limitations)}</li>
                            <li class="protocol-flow-stage"><strong>${escapeHTML(Router.uiStrings.clinicalSafetyWorkflowTitle)}:</strong> ${escapeHTML(step.safety_and_workflow_notes)}</li>
                        </ul>
                `;
            }

            html += `
                        <div class="protocol-flow-actions">
                            <button type="button" class="btn-primary protocol-flow-jump" data-flow-step="${idx}" aria-label="${escapeHTML(buttonLabel)}">
                                ${escapeHTML(I18n.translate("label.protocol_flow_go_to_step"))}
                            </button>
                        </div>
                    </div>
                </details>
            </li>
            `;
        });

        html += `
                </ol>
            </div>
        </section>
        `;
        return html;
    },

    renderProtocolQuickReference(protocol, escapeHTML) {
        return ProtocolRenderer.renderQuickReference(protocol, {
            escapeHTML,
            localize: (key) => I18n.localize(key),
            translate: (key, params) => I18n.translate(key, params)
        });
    },

    // DETALLE DE PROTOCOLO
    async renderProtocolDetail(container, id) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let data = null;
        let windows = [];
        let measurements = [];
        let mediaResources = [];
        try {
            data = await DataLoader.fetchResource("protocols");
            windows = await DataLoader.getWindows() || [];
            measurements = await DataLoader.getMeasurements() || [];
            mediaResources = await DataLoader.getMediaResources() || [];
            if (!data || !data.protocols) {
                throw new Error("No se pudo cargar la base de datos de protocolos.");
            }
        } catch (error) {
            console.error("Error al cargar detalle de protocolo:", error);
            container.innerHTML = `
                <div class="card error-card">
                    <h2>${escapeHTML(Router.uiStrings.errorLoadingTitle)}</h2>
                    <p>${escapeHTML(Router.uiStrings.errorLoadingText)}</p>
                    <a href="#/protocolos" class="btn-primary">${escapeHTML(Router.uiStrings.errorLoadingBackBtn)}</a>
                </div>
            `;
            return;
        }

        const proto = data.protocols.find(p => p.id === id);
        if (!proto) {
            this.render404(container);
            return;
        }

        const resolveWindowLink = (wId) => {
            const w = windows.find(item => item.id === wId);
            if (!w) {
                console.warn(`Ventana no resuelta: ${wId}`);
                return `<span class="element-not-available" style="color: var(--text-muted-light); font-style: italic;">${escapeHTML(wId)} (${escapeHTML(Router.uiStrings.itemNotAvailable)})</span>`;
            }
            const windowAbbreviation = I18n.localize(w.abbreviation) || I18n.localize(w.window);
            return `<a href="#/ventanas/${wId}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(I18n.localize(w.window))} (${escapeHTML(windowAbbreviation)})</a>`;
        };

        const resolveMeasurementLink = (mId) => {
            const m = measurements.find(item => item.id === mId);
            if (!m) {
                console.warn(`Medición no resuelta: ${mId}`);
                return `<span class="element-not-available" style="color: var(--text-muted-light); font-style: italic;">${escapeHTML(mId)} (${escapeHTML(Router.uiStrings.itemNotAvailable)})</span>`;
            }
            const abbr = I18n.localize(m.abbreviation) || I18n.localize(m.measurement);
            return `<a href="#/medicion/${mId}" class="clinical-link" style="color: var(--primary-medium); font-weight: 600; text-decoration: underline;">${escapeHTML(I18n.localize(m.measurement))} (${escapeHTML(abbr)})</a>`;
        };

        const steps = this.buildProtocolGuideSteps(proto);
        const protoRefs = data.references || [];
        const activeRefIds = new Set(proto.reference_ids || []);
        const filteredRefs = protoRefs.filter(ref => activeRefIds.has(ref.id));

        const protoMedia = MediaViewer.getMediaForEntity(mediaResources, 'protocol', proto.id);
        const protoMediaHTML = MediaViewer.renderMediaSection(protoMedia);

        // Construir advertencias esenciales siempre visibles
        const protoName = I18n.localize({ es: proto.name_es, en: proto.name_en });
        const altName = I18n.localize({ es: proto.name_en, en: proto.name_es });

        let html = `
            <div class="navigation-header">
                <a href="#/protocolos" class="btn-back">← ${escapeHTML(Router.uiStrings.clinicalReturnToListBtn)}</a>
                <h2>${escapeHTML(protoName)} (${escapeHTML(proto.acronym)})</h2>
            </div>

            <div class="protocol-detail">
                <div class="protocol-safety-banner card" style="border-left: 4px solid #d97706; background: rgba(217, 119, 6, 0.05); padding: 0.75rem;">
                    <p style="margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: bold; color: #d97706;">${escapeHTML(Router.uiStrings.clinicalWarningsTitle)}</p>
                    <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.9rem; line-height: 1.4;">
                        <li><strong>${escapeHTML(Router.uiStrings.clinicalPurposeLabel)}:</strong> ${escapeHTML(I18n.localize(data.educational_disclaimer))}</li>
                        <li><strong>${escapeHTML(Router.uiStrings.clinicalIntegrationLabel)}:</strong> ${escapeHTML(I18n.localize(proto.integration))}</li>
                        <li><strong>${escapeHTML(Router.uiStrings.clinicalSafetyLabel)}:</strong> ${escapeHTML(I18n.localize(proto.safety_and_workflow_notes))}</li>
                    </ul>
                </div>

                <div class="protocol-tabs">
                    <div role="tablist" aria-label="${escapeHTML(I18n.translate("label.protocol_sections"))}" class="protocol-tab-list" style="display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 2px solid var(--border-light); overflow-x: auto; padding-bottom: 0.25rem;">
                        <button type="button" role="tab" aria-selected="true" aria-controls="protocol-quick-panel" id="protocol-quick-tab" tabindex="0" class="protocol-tab-button" data-protocol-tab="quick" style="padding: 0.5rem 1rem; border: none; background: none; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent;">
                            ${escapeHTML(I18n.translate("label.protocol_quick_tab"))}
                        </button>

                        <button type="button" role="tab" aria-selected="false" aria-controls="protocol-guide-panel" id="protocol-guide-tab" tabindex="-1" class="protocol-tab-button" data-protocol-tab="guide" style="padding: 0.5rem 1rem; border: none; background: none; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent;">
                            ${escapeHTML(Router.uiStrings.guideTab)}
                        </button>

                        <button type="button" role="tab" aria-selected="false" aria-controls="protocol-full-panel" id="protocol-full-tab" tabindex="-1" class="protocol-tab-button" data-protocol-tab="content" style="padding: 0.5rem 1rem; border: none; background: none; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent;">
                            ${escapeHTML(Router.uiStrings.contentTab)}
                        </button>

                        <button type="button" role="tab" aria-selected="false" aria-controls="protocol-references-panel" id="protocol-references-tab" tabindex="-1" class="protocol-tab-button" data-protocol-tab="references" style="padding: 0.5rem 1rem; border: none; background: none; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent;">
                            ${escapeHTML(Router.uiStrings.referencesTab)}
                        </button>
                    </div>

                    <!-- PESTAÑA 1: GUÍA INTERACTIVA -->
                    <div id="protocol-guide-panel" role="tabpanel" aria-labelledby="protocol-guide-tab" class="protocol-tab-panel" hidden>
                        ${this.renderProtocolFlowMap(steps, { escapeHTML, resolveWindowLink, resolveMeasurementLink })}
                        <div class="protocol-stepper" style="display: flex; flex-direction: column; gap: 1rem;">
                            <!-- Progress Bar -->
                            <div class="protocol-progress-container" style="background: var(--border-light); border-radius: 6px; height: 10px; overflow: hidden; position: relative; width: 100%;">
                                <div id="stepper-progress-now" role="progressbar" aria-valuemin="1" aria-valuemax="${steps.length}" aria-valuenow="1" aria-valuetext="" style="background: var(--primary-medium); height: 100%; width: ${100 / steps.length}%; transition: width 0.2s ease;"></div>
                            </div>

                            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: bold; color: var(--text-muted-light);">
                                <span id="stepper-progress-text"></span>
                                <span id="stepper-live-announcer" aria-live="polite" class="sr-only" style="position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); border: 0;"></span>
                            </div>

                            <!-- Step Indicators / Markers -->
                            <div class="protocol-step-markers" style="display: flex; gap: 0.25rem; justify-content: center; flex-wrap: wrap;">
                                ${steps.map((step, idx) => `
                                    <button class="protocol-step-marker" data-step="${idx}" aria-label="${escapeHTML(I18n.translate("label.go_to_step", { step: idx + 1, title: step.title }))}" style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--border-light); background: var(--bg-light); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold;">
                                        ${idx + 1}
                                    </button>
                                `).join("")}
                            </div>

                            <!-- Step Cards -->
                            <div class="protocol-step-cards">
                                ${steps.map((step, idx) => {
            if (step.type === "start") {
                const contextLabel = I18n.translate("label.clinical_context") + ":";
                const targetLabel = I18n.translate("label.target_population") + ":";
                const sequenceLabel = I18n.translate("label.acquisition_sequence") + ":";
                return `
                                            <div class="protocol-step-card card" data-step="${idx}" ${idx === 0 ? "" : "hidden"}>
                                                <h3 class="protocol-step-title" style="margin-top: 0;">${escapeHTML(step.name)} (${escapeHTML(step.acronym)})</h3>
                                                <p style="font-style: italic; color: var(--text-muted-light);">${escapeHTML(altName)}</p>
                                                <p><strong>${escapeHTML(Router.uiStrings.clinicalPurposeLabel)}:</strong> ${escapeHTML(step.purpose)}</p>
                                                <p><strong>${escapeHTML(contextLabel)}</strong> ${escapeHTML(step.clinical_context)}</p>
                                                <p><strong>${escapeHTML(targetLabel)}</strong> ${escapeHTML(step.target_population)}</p>
                                                <div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.02); border-left: 3px solid var(--primary-medium);">
                                                    <strong>${escapeHTML(sequenceLabel)}</strong> ${escapeHTML(step.sequence_note)}
                                                </div>
                                            </div>
                                        `;
            } else if (step.type === "component") {
                const comp = step.component;
                const linkedWindowsHTML = comp.linked_window_ids && comp.linked_window_ids.length > 0
                    ? comp.linked_window_ids.map(wId => resolveWindowLink(wId)).join(", ")
                    : escapeHTML(Router.uiStrings.noLinkedItems);

                const linkedMeasurementsHTML = comp.linked_measurement_ids && comp.linked_measurement_ids.length > 0
                    ? comp.linked_measurement_ids.map(mId => resolveMeasurementLink(mId)).join(", ")
                    : escapeHTML(Router.uiStrings.noLinkedItems);

                const compMedia = MediaViewer.getMediaForEntity(mediaResources, 'component', comp.id);
                const compMediaHTML = MediaViewer.renderMediaSection(compMedia);
                const componentHeader = I18n.translate("label.component_with_name", { name: I18n.localize({ es: comp.name_es, en: comp.name_en }) });

                return `
                                            <div class="protocol-step-card card" data-step="${idx}" hidden>
                                                <h3 class="protocol-step-title" style="margin-top: 0;">${escapeHTML(componentHeader)}</h3>
                                                <p style="font-style: italic; color: var(--text-muted-light); font-size: 0.9rem;">${escapeHTML(I18n.localize({ es: comp.name_en, en: comp.name_es }))}</p>

                                                <div style="margin-top: 0.5rem;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalQuestionsLabel)}:</strong>
                                                    <ul style="margin: 0.25rem 0 0.5rem 0; padding-left: 1.25rem;">
                                                        ${comp.clinical_questions.map(q => `<li>${escapeHTML(q)}</li>`).join("")}
                                                    </ul>
                                                </div>

                                                <div style="margin-top: 0.5rem;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalTargetsLabel)}:</strong>
                                                    <ul style="margin: 0.25rem 0 0.5rem 0; padding-left: 1.25rem;">
                                                        ${comp.targets.map(t => `<li>${escapeHTML(t)}</li>`).join("")}
                                                    </ul>
                                                </div>

                                                <p style="margin: 0.5rem 0;"><strong>${escapeHTML(Router.uiStrings.clinicalViewsLabel)}:</strong> ${comp.suggested_views.map(v => escapeHTML(v)).join(", ")}</p>

                                                <div class="protocol-linked-items" style="margin: 0.75rem 0; padding: 0.75rem; background: rgba(0,0,0,0.02); border-radius: 6px; border: 1px solid var(--border-light);">
                                                    <p style="margin: 0 0 0.5rem 0;"><strong>${escapeHTML(Router.uiStrings.clinicalWindowLabel)}:</strong> ${linkedWindowsHTML}</p>
                                                    <p style="margin: 0;"><strong>${escapeHTML(Router.uiStrings.clinicalMeasurementLabel)}:</strong> ${linkedMeasurementsHTML}</p>
                                                </div>

                                                <div style="margin-top: 0.5rem;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalFindingsLabel)}:</strong>
                                                    <ul style="margin: 0.25rem 0 0.5rem 0; padding-left: 1.25rem;">
                                                        ${comp.possible_findings.map(f => `<li>${escapeHTML(f)}</li>`).join("")}
                                                    </ul>
                                                </div>

                                                <p style="margin-top: 0.75rem; padding: 0.75rem; border-left: 4px solid var(--primary-medium); background: rgba(30, 58, 138, 0.02); font-size: 0.9rem; font-style: italic;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalLimitsLabel)}:</strong> ${escapeHTML(comp.interpretation_limits)}
                                                </p>

                                                ${compMediaHTML ? `
                                                <div class="protocol-step-media" style="margin-top: 1rem;">
                                                    ${compMediaHTML}
                                                </div>` : ''}
                                            </div>
                                        `;
            } else if (step.type === "integration") {
                return `
                                            <div class="protocol-step-card card" data-step="${idx}" hidden>
                                                <h3 class="protocol-step-title" style="margin-top: 0;">${escapeHTML(Router.uiStrings.integrationStep)}</h3>
                                                <p>${escapeHTML(step.integration)}</p>
                                                <div style="margin-top: 1rem; padding: 0.75rem; border-left: 4px solid #d97706; background: rgba(217, 119, 6, 0.05); font-size: 0.9rem;">
                                                    <strong>${escapeHTML(I18n.translate("label.reminder"))}:</strong> ${escapeHTML(I18n.translate("label.reminder_text"))}
                                                </div>
                                            </div>
                                        `;
            } else if (step.type === "summary") {
                return `
                                            <div class="protocol-step-card card" data-step="${idx}" hidden>
                                                <h3 class="protocol-step-title" style="margin-top: 0;">${escapeHTML(Router.uiStrings.summaryStep)}</h3>
                                                <p>${escapeHTML(I18n.translate("label.protocol_guide_completed"))}: <strong>${step.components_names.map(name => escapeHTML(name)).join(", ")}</strong>.</p>

                                                <div style="margin-top: 0.5rem;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalGeneralLimitsTitle)}:</strong>
                                                    <p>${escapeHTML(step.limitations)}</p>
                                                </div>

                                                <div style="margin-top: 0.5rem;">
                                                    <strong>${escapeHTML(Router.uiStrings.clinicalSafetyWorkflowTitle)}:</strong>
                                                    <p>${escapeHTML(step.safety_and_workflow_notes)}</p>
                                                </div>

                                                <div style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                                    <button type="button" class="btn-secondary" onclick="document.getElementById('protocol-full-tab').click();" style="cursor: pointer;">${escapeHTML(Router.uiStrings.contentTab)}</button>
                                                    <button type="button" class="btn-secondary" onclick="document.getElementById('protocol-references-tab').click();" style="cursor: pointer;">${escapeHTML(Router.uiStrings.referencesTab)}</button>
                                                </div>
                                            </div>
                                        `;
            }
            return "";
        }).join("")}
                            </div>

                            <!-- Stepper Actions -->
                            <div class="protocol-step-actions" style="display: flex; gap: 0.5rem; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                                <button type="button" id="stepper-prev-btn" class="btn-secondary" data-guide-action="previous" style="cursor: pointer;">${escapeHTML(Router.uiStrings.previousBtn)}</button>
                                <button type="button" id="stepper-reset-btn" class="btn-secondary" data-guide-action="restart" style="cursor: pointer;">${escapeHTML(Router.uiStrings.resetBtn)}</button>
                                <button type="button" id="stepper-next-btn" class="btn-primary" data-guide-action="next" style="cursor: pointer;">${escapeHTML(Router.uiStrings.nextBtn)}</button>
                            </div>
                        </div>
                    </div>
                    <!-- PESTAÑA: RESUMEN RÁPIDO -->
                    <div id="protocol-quick-panel" role="tabpanel" aria-labelledby="protocol-quick-tab" class="protocol-tab-panel">
                        ${this.renderProtocolQuickReference(proto, escapeHTML)}
                    </div>

                    <!-- PESTAÑA 2: CONTENIDO COMPLETO -->
                    <div id="protocol-full-panel" role="tabpanel" aria-labelledby="protocol-full-tab" class="protocol-tab-panel" hidden>
                        <div class="protocol-reader-shell">
                            <div class="protocol-reader-launch">
                                <button
                                    type="button"
                                    id="protocol-reader-open"
                                    class="btn-secondary protocol-reader-open"
                                    aria-pressed="false"
                                >
                                    ${escapeHTML(I18n.translate("label.reader_mode"))}
                                </button>
                            </div>

                            <section
                                id="protocol-reader-controls"
                                class="protocol-reader-controls"
                                aria-label="${escapeHTML(I18n.translate("label.reader_controls"))}"
                                hidden
                            >
                                <div class="protocol-reader-control-group">
                                    <button type="button" id="protocol-reader-close" class="protocol-reader-exit btn-secondary">${escapeHTML(I18n.translate("label.reader_exit"))}</button>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <button type="button" id="protocol-reader-font-dec" class="btn-secondary" aria-label="${escapeHTML(I18n.translate("label.reader_font_decrease"))}">A−</button>
                                    <button type="button" id="protocol-reader-font-inc" class="btn-secondary" aria-label="${escapeHTML(I18n.translate("label.reader_font_increase"))}">A+</button>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <label for="protocol-reader-line-height-select">${escapeHTML(I18n.translate("label.reader_line_height"))}</label>
                                    <select id="protocol-reader-line-height-select">
                                        <option value="compact">${escapeHTML(I18n.translate("label.reader_line_compact"))}</option>
                                        <option value="normal" selected>${escapeHTML(I18n.translate("label.reader_line_normal"))}</option>
                                        <option value="relaxed">${escapeHTML(I18n.translate("label.reader_line_relaxed"))}</option>
                                    </select>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <label for="protocol-reader-width-select">${escapeHTML(I18n.translate("label.reader_width"))}</label>
                                    <select id="protocol-reader-width-select">
                                        <option value="narrow">${escapeHTML(I18n.translate("label.reader_width_narrow"))}</option>
                                        <option value="medium" selected>${escapeHTML(I18n.translate("label.reader_width_medium"))}</option>
                                        <option value="wide">${escapeHTML(I18n.translate("label.reader_width_wide"))}</option>
                                    </select>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <span class="protocol-reader-theme-label" id="reader-appearance-label">${escapeHTML(I18n.translate("label.reader_theme"))}</span>
                                    <div class="protocol-reader-theme-options" role="group" aria-labelledby="reader-appearance-label">
                                        <button type="button" class="theme-btn-warm" data-theme-val="warm" aria-pressed="true">${escapeHTML(I18n.translate("label.reader_theme_warm"))}</button>
                                        <button type="button" class="theme-btn-sepia" data-theme-val="sepia" aria-pressed="false">${escapeHTML(I18n.translate("label.reader_theme_sepia"))}</button>
                                        <button type="button" class="theme-btn-white" data-theme-val="white" aria-pressed="false">${escapeHTML(I18n.translate("label.reader_theme_white"))}</button>
                                        <button type="button" class="theme-btn-night" data-theme-val="night" aria-pressed="false">${escapeHTML(I18n.translate("label.reader_theme_night"))}</button>
                                    </div>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <button type="button" id="protocol-reader-distraction-toggle" class="btn-secondary" aria-pressed="false">${escapeHTML(I18n.translate("label.reader_distraction_free"))}</button>
                                </div>
                                <div class="protocol-reader-control-group">
                                    <button type="button" id="protocol-reader-reset-btn" class="btn-secondary">${escapeHTML(I18n.translate("label.reader_reset"))}</button>
                                </div>
                            </section>

                            <div
                                class="protocol-reader-progress"
                                role="progressbar"
                                aria-label="${escapeHTML(I18n.translate("label.reader_progress"))}"
                                aria-valuemin="0"
                                aria-valuemax="100"
                                aria-valuenow="0"
                                hidden
                            >
                                <div class="protocol-reader-progress-bar"></div>
                                <span class="protocol-reader-progress-text">0%</span>
                            </div>

                            <article
                                id="protocol-reader-page"
                                class="protocol-reader-page"
                                data-reader-theme="warm"
                                data-reader-line-height="normal"
                                data-reader-width="medium"
                            >
                                <div class="protocol-full-content content-accordion-grid">
                                    <details class="content-accordion card clinical-card">
                                        <summary class="content-accordion-summary">
                                            <span class="content-accordion-title">${escapeHTML(I18n.translate("label.purpose_and_context"))}</span>
                                            <span class="content-accordion-arrow"></span>
                                        </summary>
                                        <div class="content-accordion-body">
                                            <p class="subtitle-en" style="font-style: italic; color: var(--text-muted-light);">${escapeHTML(altName)}</p>
                                            <p><strong>${escapeHTML(Router.uiStrings.clinicalPurposeLabel)}:</strong> ${escapeHTML(I18n.localize(proto.purpose))}</p>
                                            <p><strong>${escapeHTML(I18n.translate("label.clinical_context"))}:</strong> ${escapeHTML(I18n.localize(proto.clinical_context))}</p>
                                            <p><strong>${escapeHTML(I18n.translate("label.target_population"))}:</strong> ${escapeHTML(I18n.localize(proto.target_population))}</p>
                                        </div>
                                    </details>

                                    <details class="content-accordion card clinical-card">
                                        <summary class="content-accordion-summary">
                                            <span class="content-accordion-title">${escapeHTML(Router.uiStrings.clinicalSequenceTitle)}</span>
                                            <span class="content-accordion-arrow"></span>
                                        </summary>
                                        <div class="content-accordion-body">
                                            <p>${escapeHTML(I18n.localize(proto.sequence_note))}</p>
                                        </div>
                                    </details>

                                    ${proto.components.map(comp => {
            const linkedWindowsHTML = comp.linked_window_ids && comp.linked_window_ids.length > 0
                ? comp.linked_window_ids.map(wId => resolveWindowLink(wId)).join(", ")
                : escapeHTML(Router.uiStrings.noLinkedItems);

            const linkedMeasurementsHTML = comp.linked_measurement_ids && comp.linked_measurement_ids.length > 0
                ? comp.linked_measurement_ids.map(mId => resolveMeasurementLink(mId)).join(", ")
                : escapeHTML(Router.uiStrings.noLinkedItems);

            const componentLabel = I18n.translate("label.component_with_name", { name: "" }).replace(" :", "").replace(":", "").trim();
            const compName = I18n.localize({ es: comp.name_es, en: comp.name_en });
            const altCompName = I18n.localize({ es: comp.name_en, en: comp.name_es });

            return `
                                            <details class="content-accordion card clinical-card">
                                                <summary class="content-accordion-summary">
                                                    <span class="content-accordion-title">${escapeHTML(componentLabel)} ${escapeHTML(compName)}</span>
                                                    <span class="content-accordion-arrow"></span>
                                                </summary>
                                                <div class="content-accordion-body">
                                                    <p style="font-style: italic; color: var(--text-muted-light);">${escapeHTML(altCompName)}</p>

                                                    <div style="margin-top: 0.5rem;">
                                                        <strong>${escapeHTML(Router.uiStrings.clinicalQuestionsLabel)}:</strong>
                                                        <ul style="margin: 0.25rem 0; padding-left: 1.25rem;">
                                                            ${(comp.clinical_questions || []).map(q => `<li>${escapeHTML(I18n.localize(q))}</li>`).join("")}
                                                        </ul>
                                                    </div>

                                                    <div style="margin-top: 0.5rem;">
                                                        <strong>${escapeHTML(Router.uiStrings.clinicalTargetsLabel)}:</strong>
                                                        <ul style="margin: 0.25rem 0; padding-left: 1.25rem;">
                                                            ${(comp.targets || []).map(t => `<li>${escapeHTML(I18n.localize(t))}</li>`).join("")}
                                                        </ul>
                                                    </div>

                                                    <p><strong>${escapeHTML(Router.uiStrings.clinicalViewsLabel)}:</strong> ${(comp.suggested_views || []).map(v => escapeHTML(I18n.localize(v))).join(", ")}</p>

                                                    <div class="protocol-linked-items" style="margin: 0.75rem 0; padding: 0.75rem; background: rgba(0,0,0,0.02); border-radius: 6px; border: 1px solid var(--border-light);">
                                                        <p style="margin: 0 0 0.5rem 0;"><strong>${escapeHTML(Router.uiStrings.clinicalWindowLabel)}:</strong> ${linkedWindowsHTML}</p>
                                                        <p style="margin: 0;"><strong>${escapeHTML(Router.uiStrings.clinicalMeasurementLabel)}:</strong> ${linkedMeasurementsHTML}</p>
                                                    </div>

                                                    <div style="margin-top: 0.5rem;">
                                                        <strong>${escapeHTML(Router.uiStrings.clinicalFindingsLabel)}:</strong>
                                                        <ul style="margin: 0.25rem 0; padding-left: 1.25rem;">
                                                            ${(comp.possible_findings || []).map(f => `<li>${escapeHTML(I18n.localize(f))}</li>`).join("")}
                                                        </ul>
                                                    </div>

                                                    <p style="margin-top: 0.5rem; padding: 0.5rem; border-left: 3px solid var(--primary-medium); font-size: 0.95rem; font-style: italic;">
                                                        <strong>${escapeHTML(Router.uiStrings.clinicalLimitsLabel)}:</strong> ${escapeHTML(I18n.localize(comp.interpretation_limits))}
                                                    </p>
                                                </div>
                                            </details>
                                        `;
        }).join("")}

                                    <details class="content-accordion card clinical-card">
                                        <summary class="content-accordion-summary">
                                            <span class="content-accordion-title">${escapeHTML(Router.uiStrings.integrationStep)}</span>
                                            <span class="content-accordion-arrow"></span>
                                        </summary>
                                        <div class="content-accordion-body">
                                            <p>${escapeHTML(I18n.localize(proto.integration))}</p>
                                        </div>
                                    </details>

                                    <details class="content-accordion card clinical-card">
                                        <summary class="content-accordion-summary">
                                            <span class="content-accordion-title">${escapeHTML(Router.uiStrings.clinicalGeneralLimitsTitle)}</span>
                                            <span class="content-accordion-arrow"></span>
                                        </summary>
                                        <div class="content-accordion-body">
                                            <p>${escapeHTML(I18n.localize(proto.limitations))}</p>
                                        </div>
                                    </details>

                                    <details class="content-accordion card clinical-card">
                                        <summary class="content-accordion-summary">
                                            <span class="content-accordion-title">${escapeHTML(Router.uiStrings.clinicalSafetyWorkflowTitle)}</span>
                                            <span class="content-accordion-arrow"></span>
                                        </summary>
                                        <div class="content-accordion-body">
                                            <p>${escapeHTML(I18n.localize(proto.safety_and_workflow_notes))}</p>
                                        </div>
                                    </details>
                                    ${protoMediaHTML ? `
                                    <div class="protocol-media-container" style="margin-top: 1rem;">
                                        ${protoMediaHTML}
                                    </div>` : ''}
                                </div>
                            </article>
                        </div>
                    </div>

                    <!-- PESTAÑA 3: REFERENCIAS -->
                    <div id="protocol-references-panel" role="tabpanel" aria-labelledby="protocol-references-tab" class="protocol-tab-panel" hidden>
                        <div class="protocol-references card">
                            <h3>${escapeHTML(Router.uiStrings.clinicalReferencesTitle)}</h3>
                            <ol style="padding-left: 1.25rem; margin-top: 0.5rem; margin-bottom: 0;">
                                ${filteredRefs.map(ref => `
                                    <li style="margin-bottom: 0.75rem; font-size: 0.9rem;">
                                        ${escapeHTML(ref.citation)}
                                        ${ref.pmid ? `<br><small style="color: var(--text-muted-light);">PMID: ${escapeHTML(ref.pmid)}</small>` : ''}
                                        ${ref.pmcid ? `<br><small style="color: var(--text-muted-light);">PMCID: ${escapeHTML(ref.pmcid)}</small>` : ''}
                                        ${ref.doi ? `<br><small style="color: var(--text-muted-light);">DOI: ${escapeHTML(ref.doi)}</small>` : ''}
                                    </li>
                                `).join("")}
                            </ol>
                        </div>
                    </div>
                </div>

                <div class="protocol-footer-actions" style="margin-top: 1.5rem; display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; margin-bottom: 1.5rem;">
                    <a href="#/protocolos" class="btn-primary">${escapeHTML(Router.uiStrings.clinicalReturnToListBtn)}</a>
                    <a href="#/" class="btn-secondary">${escapeHTML(Router.uiStrings.clinicalReturnHomeBtn)}</a>
                </div>
            </div>
        `;

        container.innerHTML = html;
        MediaViewer.initializeMediaInteractions(container);

        // Inicializar controladores interactivos
        this.initializeProtocolTabs(id);
        this.initializeProtocolStepper(id, steps);
        this.initializeProtocolReader(id);
    },

    initializeProtocolTabs(protocolId) {
        const tabButtons = Array.from(
            document.querySelectorAll(".protocol-tab-button")
        );

        const selectTab = (selectedButton, saveState = true) => {
            if (!selectedButton) return;

            const selectedPanelId =
                selectedButton.getAttribute("aria-controls");

            tabButtons.forEach((button) => {
                const isSelected = button === selectedButton;

                button.setAttribute(
                    "aria-selected",
                    isSelected ? "true" : "false"
                );

                button.setAttribute(
                    "tabindex",
                    isSelected ? "0" : "-1"
                );

                button.classList.toggle("active", isSelected);

                button.style.borderBottom = isSelected
                    ? "2px solid var(--primary-medium)"
                    : "2px solid transparent";
            });

            document
                .querySelectorAll(".protocol-tab-panel")
                .forEach((panel) => {
                    const isSelected = panel.id === selectedPanelId;

                    if (isSelected) {
                        panel.removeAttribute("hidden");
                    } else {
                        panel.setAttribute("hidden", "");
                    }
                });

            if (saveState) {
                Storage.setSessionState(
                    `pocus-protocol-tab-${protocolId}`,
                    selectedButton.id
                );
            }
        };

        tabButtons.forEach((button, index) => {
            button.addEventListener("click", () => {
                selectTab(button);
            });

            button.addEventListener("keydown", (event) => {
                let nextIndex = index;

                if (event.key === "ArrowRight") {
                    nextIndex = (index + 1) % tabButtons.length;
                } else if (event.key === "ArrowLeft") {
                    nextIndex =
                        (index - 1 + tabButtons.length) %
                        tabButtons.length;
                } else if (event.key === "Home") {
                    nextIndex = 0;
                } else if (event.key === "End") {
                    nextIndex = tabButtons.length - 1;
                } else {
                    return;
                }

                event.preventDefault();

                const nextButton = tabButtons[nextIndex];
                selectTab(nextButton);
                nextButton.focus();
            });
        });

        // Abrir siempre Resumen rápido al entrar al protocolo.
        const quickTab =
            document.getElementById("protocol-quick-tab");

        selectTab(quickTab || tabButtons[0], false);
    },

    initializeProtocolStepper(protocolId, steps) {
        const stepCards = document.querySelectorAll(".protocol-step-card");
        const progressNow = document.getElementById("stepper-progress-now");
        const progressText = document.getElementById("stepper-progress-text");
        const liveAnnouncer = document.getElementById("stepper-live-announcer");

        const prevBtn = document.getElementById("stepper-prev-btn");
        const nextBtn = document.getElementById("stepper-next-btn");
        const resetBtn = document.getElementById("stepper-reset-btn");

        const markers = document.querySelectorAll(".protocol-step-marker");

        let currentStep = 0;

        // Restore from sessionStorage
        // Restore from sessionStorage
        const storedStep = Storage.getSessionState(`pocus-protocol-step-${protocolId}`);
        if (storedStep !== null) {
            const parsed = parseInt(storedStep, 10);
            if (!isNaN(parsed) && parsed >= 0 && parsed < steps.length) {
                currentStep = parsed;
            }
        }

        const showStep = (index, focusTitle = false) => {
            currentStep = index;

            // Save to sessionStorage
            Storage.setSessionState(`pocus-protocol-step-${protocolId}`, currentStep.toString());

            // Hide all step cards, show active
            stepCards.forEach((card, i) => {
                if (i === currentStep) {
                    card.removeAttribute("hidden");
                    if (focusTitle) {
                        const titleEl = card.querySelector(".protocol-step-title");
                        if (titleEl) {
                            titleEl.setAttribute("tabindex", "-1");
                            titleEl.focus();
                        }
                    }
                } else {
                    card.setAttribute("hidden", "true");
                }
            });

            // Update markers
            markers.forEach((marker, i) => {
                if (i === currentStep) {
                    marker.classList.add("active");
                    marker.style.background = "var(--primary-medium)";
                    marker.style.color = "var(--bg-light)";
                    marker.setAttribute("aria-current", "step");
                } else {
                    marker.classList.remove("active");
                    marker.style.background = "var(--bg-light)";
                    marker.style.color = "var(--text-main)";
                    marker.removeAttribute("aria-current");
                }
            });

            // Update buttons
            if (prevBtn) {
                prevBtn.disabled = currentStep === 0;
            }
            if (nextBtn) {
                if (currentStep === steps.length - 1) {
                    nextBtn.innerText = Router.uiStrings.finishedBtn;
                    nextBtn.disabled = true;
                } else {
                    nextBtn.innerText = Router.uiStrings.nextBtn;
                    nextBtn.disabled = false;
                }
            }

            // Update progress bar
            const progressPct = ((currentStep + 1) / steps.length) * 100;
            if (progressNow) {
                progressNow.style.width = `${progressPct}%`;
                progressNow.setAttribute("aria-valuenow", (currentStep + 1).toString());
                const stepText = Router.uiStrings.stepIndicator
                    .replace("{x}", (currentStep + 1).toString())
                    .replace("{y}", steps.length.toString());
                const text = `${stepText}: ${steps[currentStep].title}`;
                progressNow.setAttribute("aria-valuetext", text);
            }
            if (progressText) {
                const stepText = Router.uiStrings.stepIndicator
                    .replace("{x}", (currentStep + 1).toString())
                    .replace("{y}", steps.length.toString());
                progressText.innerText = stepText;
            }

            // Announce change to screen readers
            if (liveAnnouncer) {
                const stepText = Router.uiStrings.stepIndicator
                    .replace("{x}", (currentStep + 1).toString())
                    .replace("{y}", steps.length.toString());
                liveAnnouncer.innerText = `${stepText}: ${steps[currentStep].title}`;
            }
        };

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (currentStep > 0) {
                    showStep(currentStep - 1, true);
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                if (currentStep < steps.length - 1) {
                    showStep(currentStep + 1, true);
                }
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                showStep(0, true);
            });
        }

        // Initialize markers clicks
        markers.forEach((marker, i) => {
            marker.addEventListener("click", () => {
                showStep(i, true);
            });
        });

        // Initialize flow map buttons
        const flowJumps = document.querySelectorAll(".protocol-flow-jump");
        flowJumps.forEach(btn => {
            btn.addEventListener("click", (e) => {
                const stepIdx = parseInt(e.currentTarget.getAttribute("data-flow-step"), 10);
                if (!isNaN(stepIdx) && stepIdx >= 0 && stepIdx < steps.length) {
                    showStep(stepIdx, true);
                }
            });
        });

        // Show initial step
        showStep(currentStep, false);
    },

    initializeProtocolReader(protocolId) {
        const fullPanel = document.getElementById("protocol-full-panel");
        if (!fullPanel) return;

        const appContainer = document.querySelector(".app-container") || document.getElementById("app");
        const launchDiv = fullPanel.querySelector(".protocol-reader-launch");
        const openBtn = document.getElementById("protocol-reader-open");
        const controlsSec = document.getElementById("protocol-reader-controls");
        const closeBtn = document.getElementById("protocol-reader-close");
        const fontDecBtn = document.getElementById("protocol-reader-font-dec");
        const fontIncBtn = document.getElementById("protocol-reader-font-inc");
        const lineHeightSelect = document.getElementById("protocol-reader-line-height-select");
        const widthSelect = document.getElementById("protocol-reader-width-select");
        const themeBtns = controlsSec ? controlsSec.querySelectorAll(".protocol-reader-theme-options button") : [];
        const distractionToggle = document.getElementById("protocol-reader-distraction-toggle");
        const resetBtn = document.getElementById("protocol-reader-reset-btn");
        const progressDiv = fullPanel.querySelector(".protocol-reader-progress");
        const progressBar = progressDiv ? progressDiv.querySelector(".protocol-reader-progress-bar") : null;
        const progressText = progressDiv ? progressDiv.querySelector(".protocol-reader-progress-text") : null;
        const page = document.getElementById("protocol-reader-page");
        const accordions = page ? page.querySelectorAll("details.content-accordion") : [];

        let accordionStates = [];

        const getValidTheme = () => {
            const val = typeof Storage.getPreference === "function" ? Storage.getPreference("pocus_reader_theme") : null;
            return ["warm", "sepia", "white", "night"].includes(val) ? val : "warm";
        };
        const getValidFontSize = () => {
            const val = typeof Storage.getPreference === "function" ? parseInt(Storage.getPreference("pocus_reader_font_size"), 10) : 18;
            return (!isNaN(val) && val >= 16 && val <= 24 && val % 2 === 0) ? val : 18;
        };
        const getValidLineHeight = () => {
            const val = typeof Storage.getPreference === "function" ? Storage.getPreference("pocus_reader_line_height") : null;
            return ["compact", "normal", "relaxed"].includes(val) ? val : "normal";
        };
        const getValidWidth = () => {
            const val = typeof Storage.getPreference === "function" ? Storage.getPreference("pocus_reader_width") : null;
            return ["narrow", "medium", "wide"].includes(val) ? val : "medium";
        };
        const getValidDistractionFree = () => {
            const val = typeof Storage.getPreference === "function" ? Storage.getPreference("pocus_reader_distraction_free") : false;
            return (val === true || val === "true");
        };

        const setPreferenceSafe = (key, value) => {
            if (typeof Storage.setPreference === "function") {
                Storage.setPreference(key, value);
            }
        };

        const preventSummaryClick = (e) => {
            e.preventDefault();
        };

        const updateProgress = () => {
            if (!page || !progressDiv || progressDiv.hasAttribute("hidden")) return;
            const pageHeight = page.offsetHeight;
            const pageTop = page.offsetTop;
            const viewportHeight = window.innerHeight;
            const totalScrollable = pageHeight - viewportHeight;

            let progress = 0;
            if (totalScrollable <= 0) {
                progress = 100;
            } else {
                const currentScroll = window.scrollY - pageTop;
                progress = Math.max(0, Math.min(100, Math.round((currentScroll / totalScrollable) * 100)));
            }

            progressDiv.setAttribute("aria-valuenow", progress.toString());
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            if (progressText) {
                progressText.innerText = `${progress}%`;
            }
        };

        const applyPreferences = () => {
            if (!page) return;
            const theme = getValidTheme();
            const fontSize = getValidFontSize();
            const lineHeight = getValidLineHeight();
            const width = getValidWidth();
            const distractionFree = getValidDistractionFree();

            page.setAttribute("data-reader-theme", theme);
            page.setAttribute("data-reader-line-height", lineHeight);
            page.setAttribute("data-reader-width", width);
            page.style.setProperty("--reader-font-size", `${fontSize}px`);

            themeBtns.forEach(btn => {
                const isSelected = btn.getAttribute("data-theme-val") === theme;
                btn.setAttribute("aria-pressed", isSelected ? "true" : "false");
                if (isSelected) {
                    btn.classList.add("active");
                } else {
                    btn.classList.remove("active");
                }
            });

            if (fontDecBtn) {
                fontDecBtn.disabled = (fontSize <= 16);
                fontDecBtn.setAttribute("aria-disabled", fontSize <= 16 ? "true" : "false");
            }
            if (fontIncBtn) {
                fontIncBtn.disabled = (fontSize >= 24);
                fontIncBtn.setAttribute("aria-disabled", fontSize >= 24 ? "true" : "false");
            }

            if (lineHeightSelect) lineHeightSelect.value = lineHeight;
            if (widthSelect) widthSelect.value = width;

            if (distractionToggle) {
                distractionToggle.setAttribute("aria-pressed", distractionFree ? "true" : "false");
                if (distractionFree) {
                    distractionToggle.classList.add("active");
                    if (fullPanel.classList.contains("reader-active")) {
                        if (appContainer) appContainer.classList.add("reader-distraction-free");
                    } else {
                        if (appContainer) appContainer.classList.remove("reader-distraction-free");
                    }
                } else {
                    distractionToggle.classList.remove("active");
                    if (appContainer) appContainer.classList.remove("reader-distraction-free");
                }
            }
        };

        const activateReader = () => {
            fullPanel.classList.add("reader-active");
            if (appContainer) appContainer.classList.add("reader-layout-active");
            if (openBtn) openBtn.setAttribute("aria-pressed", "true");
            if (launchDiv) launchDiv.style.display = "none";
            if (controlsSec) controlsSec.removeAttribute("hidden");
            if (progressDiv) progressDiv.removeAttribute("hidden");

            accordionStates = [];
            accordions.forEach(acc => {
                accordionStates.push(acc.open);
                acc.open = true;
                const summary = acc.querySelector("summary");
                if (summary) {
                    summary.addEventListener("click", preventSummaryClick);
                }
            });

            applyPreferences();
            updateProgress();

            setTimeout(() => {
                if (closeBtn) closeBtn.focus();
            }, 50);
        };

        const deactivateReader = (options = {}) => {
            const restoreFocus = options.restoreFocus !== false;
            fullPanel.classList.remove("reader-active");
            if (appContainer) {
                appContainer.classList.remove("reader-layout-active");
                appContainer.classList.remove("reader-distraction-free");
            }
            if (openBtn) openBtn.setAttribute("aria-pressed", "false");
            if (launchDiv) launchDiv.style.display = "";
            if (controlsSec) controlsSec.setAttribute("hidden", "true");
            if (progressDiv) progressDiv.setAttribute("hidden", "true");

            accordions.forEach((acc, index) => {
                const summary = acc.querySelector("summary");
                if (summary) {
                    summary.removeEventListener("click", preventSummaryClick);
                }
                if (index < accordionStates.length) {
                    acc.open = accordionStates[index];
                }
            });

            if (page) {
                page.style.removeProperty("--reader-font-size");
            }

            if (restoreFocus) {
                setTimeout(() => {
                    if (openBtn) openBtn.focus();
                }, 50);
            }
        };

        const handleKeyDown = (e) => {
            if (e.key === "Escape" && fullPanel.classList.contains("reader-active")) {
                e.preventDefault();
                deactivateReader();
            }
        };

        // Event listeners
        if (openBtn) {
            openBtn.addEventListener("click", activateReader);
        }
        if (closeBtn) {
            closeBtn.addEventListener("click", deactivateReader);
        }
        if (fontDecBtn) {
            fontDecBtn.addEventListener("click", () => {
                const currentSize = getValidFontSize();
                if (currentSize > 16) {
                    setPreferenceSafe("pocus_reader_font_size", currentSize - 2);
                    applyPreferences();
                    updateProgress();
                }
            });
        }
        if (fontIncBtn) {
            fontIncBtn.addEventListener("click", () => {
                const currentSize = getValidFontSize();
                if (currentSize < 24) {
                    setPreferenceSafe("pocus_reader_font_size", currentSize + 2);
                    applyPreferences();
                    updateProgress();
                }
            });
        }
        if (lineHeightSelect) {
            lineHeightSelect.addEventListener("change", (e) => {
                const val = e.target.value;
                if (["compact", "normal", "relaxed"].includes(val)) {
                    setPreferenceSafe("pocus_reader_line_height", val);
                    applyPreferences();
                    updateProgress();
                }
            });
        }
        if (widthSelect) {
            widthSelect.addEventListener("change", (e) => {
                const val = e.target.value;
                if (["narrow", "medium", "wide"].includes(val)) {
                    setPreferenceSafe("pocus_reader_width", val);
                    applyPreferences();
                    updateProgress();
                }
            });
        }
        themeBtns.forEach(btn => {
            btn.addEventListener("click", (e) => {
                const val = e.currentTarget.getAttribute("data-theme-val");
                if (["warm", "sepia", "white", "night"].includes(val)) {
                    setPreferenceSafe("pocus_reader_theme", val);
                    applyPreferences();
                    updateProgress();
                }
            });
        });
        if (distractionToggle) {
            distractionToggle.addEventListener("click", () => {
                const current = getValidDistractionFree();
                setPreferenceSafe("pocus_reader_distraction_free", !current);
                applyPreferences();
                updateProgress();
            });
        }
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                setPreferenceSafe("pocus_reader_theme", "warm");
                setPreferenceSafe("pocus_reader_font_size", 18);
                setPreferenceSafe("pocus_reader_line_height", "normal");
                setPreferenceSafe("pocus_reader_width", "medium");
                setPreferenceSafe("pocus_reader_distraction_free", false);
                applyPreferences();
                updateProgress();
            });
        }

        // Close on switching tabs away from Contenido completo
        const tabButtons = document.querySelectorAll('[role="tab"]');
        tabButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                if (btn.id !== "protocol-full-tab") {
                    if (fullPanel.classList.contains("reader-active")) {
                        deactivateReader();
                    }
                }
            });
        });

        // Clean up helper before registering new listeners
        if (Router._readerCleanup) {
            Router._readerCleanup();
        }

        // Keydown Escape and Scroll
        window.addEventListener("keydown", handleKeyDown);
        window.addEventListener("scroll", updateProgress, { passive: true });
        window.addEventListener("resize", updateProgress, { passive: true });

        Router._readerCleanup = () => {
            deactivateReader({ restoreFocus: false });
            window.removeEventListener("keydown", handleKeyDown);
            window.removeEventListener("scroll", updateProgress);
            window.removeEventListener("resize", updateProgress);
        };

        // Apply appearance initially (but inactive)
        applyPreferences();
    },

    // ABREVIATURAS
    async renderAbbreviations(container) {
        const abbreviations = await DataLoader.getAbbreviations() || [];
        const escapeHTML = (str) => {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${escapeHTML(I18n.translate("label.abbreviations_list_title"))}</h2>
            </div>

            <table class="clinical-table">
                <thead>
                    <tr>
                        <th>${I18n.translate("label.abbreviation")}</th>
                        <th>${I18n.translate("label.definition")}</th>
                        <th>${I18n.translate("label.origen")}</th>
                    </tr>
                </thead>
                <tbody>
        `;

        abbreviations.forEach(abbr => {
            const meaningLoc = I18n.localize(abbr.meaning);
            html += `
                <tr>
                    <td><strong>${escapeHTML(abbr.abbreviation)}</strong></td>
                    <td>${escapeHTML(meaningLoc)}</td>
                    <td>P. ${abbr.source_page}</td>
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
        const escapeHTML = (str) => {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${escapeHTML(I18n.translate("label.practical_classifications"))}</h2>
            </div>
        `;

        classifications.forEach(c => {
            const nameLoc = I18n.localize(c.name);
            const noteLoc = I18n.localize(c.note);
            const col1Header = c.items[0].range ? I18n.translate("label.rango") : I18n.translate("label.parameter");
            const col2Header = c.items[0].category ? I18n.translate("label.classification") : I18n.translate("label.cutoff_point");

            html += `
                <div class="card" style="margin-bottom: 1.5rem; padding: 1.5rem; background-color: var(--card-bg-light); border: 1px solid var(--border-light); border-radius: 12px;">
                    <h3 style="color: var(--primary-medium); margin-bottom: 0.5rem;">${escapeHTML(nameLoc)}</h3>
                    <table class="clinical-table" style="margin: 0.5rem 0;">
                        <thead>
                            <tr>
                                <th>${escapeHTML(col1Header)}</th>
                                <th>${escapeHTML(col2Header)}</th>
                                ${c.items[0].method ? `<th>${escapeHTML(I18n.translate("label.method"))}</th>` : ""}
                            </tr>
                        </thead>
                        <tbody>
            `;
            c.items.forEach(item => {
                const rangeLoc = I18n.localize(item.range);
                const paramLoc = I18n.localize(item.parameter);
                const catLoc = I18n.localize(item.category);
                const thresholdLoc = I18n.localize(item.threshold);
                const methodLoc = I18n.localize(item.method);

                html += `
                    <tr>
                        <td><strong>${escapeHTML(rangeLoc || paramLoc)}</strong></td>
                        <td>${escapeHTML(catLoc || thresholdLoc)}</td>
                        ${item.method ? `<td>${escapeHTML(methodLoc)}</td>` : ""}
                    </tr>
                `;
            });
            html += `
                        </tbody>
                    </table>
                    ${noteLoc ? `<p style="font-size: 0.85rem; color: var(--text-muted-light); margin-top: 0.5rem;"><strong>${escapeHTML(I18n.translate("label.note"))}:</strong> ${escapeHTML(noteLoc)}</p>` : ""}
                    <div style="font-size: 0.8rem; color: var(--text-muted-light); text-align: right; margin-top: 0.25rem;">${I18n.translate("label.origen")}: ${c.source_page}</div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    // CONJUNTO MÍNIMO POCUS
    async renderMinimumSet(container) {
        const minSet = await DataLoader.getMinimumPocusSet() || [];
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const descText = I18n.translate("label.minimum_set_desc");
        const principleLabel = I18n.translate("label.integration_principle");
        const principleText = I18n.translate("label.integration_principle_text");

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("label.minimum_set")} POCUS</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light);">
                <p style="margin-bottom: 1rem; font-size: 0.95rem; color: var(--text-muted-light);">
                    ${escapeHTML(descText)}
                </p>
                <ol style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
        `;

        minSet.forEach(item => {
            const skillLoc = I18n.localize(item.skill);
            html += `
                <li style="font-size: 0.95rem;">
                    <strong>${escapeHTML(skillLoc)}</strong>
                    <span style="font-size: 0.8rem; color: var(--text-muted-light); margin-left: 0.5rem;">(P. ${item.source_page})</span>
                </li>
            `;
        });

        html += `
                </ol>
                <div class="safety-banner" style="margin-top: 1.5rem;">
                    <strong>${escapeHTML(principleLabel)}:</strong> ${escapeHTML(principleText)}
                </div>
            </div>
        `;
        container.innerHTML = html;
    },

    // UNIDADES Y ERRORES FRECUENTES
    async renderUnitWarnings(container) {
        const warnings = await DataLoader.getUnitWarnings() || [];
        const escapeHTML = (str) => {
            if (str === null || str === undefined) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("label.unit_warnings")}</h2>
            </div>

            <div class="cards-list">
        `;

        warnings.forEach(w => {
            const parameter = I18n.localize(w.parameter);
            const warning = I18n.localize(w.warning);
            html += `
                <div class="card clinical-card warning-card" style="border-left: 4px solid #eab308; background-color: var(--card-bg-light);">
                    <h3 style="color: var(--warning-text); font-size: 1.1rem; margin-bottom: 0.25rem;">${escapeHTML(parameter)}</h3>
                    <p style="font-size: 0.95rem;">${escapeHTML(warning)}</p>
                    <div style="font-size: 0.8rem; color: var(--text-muted-light); margin-top: 0.5rem; text-align: right;">${I18n.translate("label.origen")}: ${escapeHTML(w.source_page)}</div>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
    },

    // MIS FAVORITOS
    async renderFavorites(container) {
        let measurements = [];
        let glossary = [];
        try {
            measurements = await DataLoader.getMeasurements();
        } catch (e) {
            console.warn("DataLoader.getMeasurements failed in renderFavorites", e);
        }
        try {
            glossary = await DataLoader.getGlossary();
        } catch (e) {
            console.warn("DataLoader.getGlossary failed in renderFavorites", e);
        }
        if (!Array.isArray(measurements)) measurements = [];
        if (!Array.isArray(glossary)) glossary = [];

        const measurementMap = {};
        measurements.forEach(m => {
            if (m && typeof m === "object" && typeof m.id === "string" && m.id.trim()) {
                measurementMap[m.id] = m;
            }
        });
        const glossaryMap = {};
        glossary.forEach(g => {
            if (g && typeof g === "object" && typeof g.id === "string" && g.id.trim()) {
                glossaryMap[g.id] = g;
            }
        });

        const escapeHTML = (value) => {
            if (value === null || value === undefined) return "";
            return String(value)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const resolveCurrentTitle = (entry) => {
            if (!entry || typeof entry !== "object") return "";
            let current = "";
            if (entry.type === "medición") {
                const resource = measurementMap[entry.id];
                if (resource) {
                    current = I18n.localize(resource.measurement);
                }
            } else if (entry.type === "término") {
                const resource = glossaryMap[entry.id];
                if (resource) {
                    current = I18n.localize(resource.term);
                }
            }

            if (typeof current === "string" && current.trim()) {
                return current;
            }

            const fallbackTitle = I18n.localize(entry.title);
            if (typeof fallbackTitle === "string" && fallbackTitle.trim()) {
                return fallbackTitle;
            }

            return typeof entry.id === "string" ? entry.id : "";
        };

        const getLocalizedTypeLabel = (type) => {
            if (type === "medición") {
                return I18n.translate("label.measurement");
            }
            if (type === "término") {
                return I18n.translate("label.term");
            }
            return I18n.localize({
                es: "Elemento",
                en: "Item"
            });
        };

        const favs = Storage.getFavorites() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${escapeHTML(I18n.translate("nav.home"))}</a>
                <h2>${escapeHTML(I18n.translate("nav.favorites"))}</h2>
            </div>
        `;

        if (favs.length === 0) {
            html += `
                <div class="card error-card">
                    <p>${escapeHTML(I18n.translate("state.no_favorites"))}</p>
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        const labelClearFavs = escapeHTML(I18n.localize({
            es: "Limpiar favoritos",
            en: "Clear favorites"
        }));

        html += `
            <div style="text-align: right; margin-bottom: 1rem;">
                <button id="clear-all-favs" class="btn-secondary" style="display: inline-flex; min-height: 38px; padding: 0.25rem 1rem;">${labelClearFavs}</button>
            </div>
            <div class="cards-list">
        `;

        favs.forEach((f, index) => {
            const resolvedTitle = resolveCurrentTitle(f);
            let link = "#/";
            let badgeClass = "";

            if (f.type === "medición") {
                link = `#/medicion/${f.id}`;
                badgeClass = "badge-medicion";
            } else if (f.type === "término") {
                link = `#/glosario/${f.id}`;
                badgeClass = "badge-termino";
            }

            const labelRemove = escapeHTML(I18n.translate("action.remove_favorite"));

            html += `
                <div class="card clinical-card" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 1rem;">
                    <div>
                        <a href="${escapeHTML(link)}" style="text-decoration: none; font-weight: 600; color: var(--primary-light); font-size: 1.05rem;">${escapeHTML(resolvedTitle)}</a>
                        <span class="result-badge ${escapeHTML(badgeClass)}" style="margin-left: 0.5rem;">${escapeHTML(getLocalizedTypeLabel(f.type))}</span>
                    </div>
                    <button class="btn-table-action" data-favorite-index="${index}" style="background-color: #fee2e2; color: #991b1b; border: none; border-radius: 6px; padding: 0.35rem 0.75rem; cursor: pointer;">${labelRemove}</button>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;

        const labelConfirm = I18n.localize({
            es: "¿Estás seguro de que deseas borrar todos tus favoritos guardados?",
            en: "Are you sure you want to delete all your saved favorites?"
        });

        document.getElementById("clear-all-favs")?.addEventListener("click", () => {
            if (confirm(labelConfirm)) {
                Storage.clearFavorites();
                Router.route();
            }
        });

        container.querySelectorAll("button[data-favorite-index]").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.getAttribute("data-favorite-index"), 10);
                const originalEntry = favs[idx];
                if (originalEntry) {
                    const resolvedTitle = resolveCurrentTitle(originalEntry);
                    Storage.toggleFavorite(originalEntry.type, originalEntry.id, resolvedTitle);
                    Router.route();
                }
            });
        });
    },

    // VISTOS RECIENTEMENTE
    async renderRecents(container) {
        let measurements = [];
        let glossary = [];
        try {
            measurements = await DataLoader.getMeasurements();
        } catch (e) {
            console.warn("DataLoader.getMeasurements failed in renderRecents", e);
        }
        try {
            glossary = await DataLoader.getGlossary();
        } catch (e) {
            console.warn("DataLoader.getGlossary failed in renderRecents", e);
        }
        if (!Array.isArray(measurements)) measurements = [];
        if (!Array.isArray(glossary)) glossary = [];

        const measurementMap = {};
        measurements.forEach(m => {
            if (m && typeof m === "object" && typeof m.id === "string" && m.id.trim()) {
                measurementMap[m.id] = m;
            }
        });
        const glossaryMap = {};
        glossary.forEach(g => {
            if (g && typeof g === "object" && typeof g.id === "string" && g.id.trim()) {
                glossaryMap[g.id] = g;
            }
        });

        const escapeHTML = (value) => {
            if (value === null || value === undefined) return "";
            return String(value)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const resolveCurrentTitle = (entry) => {
            if (!entry || typeof entry !== "object") return "";
            let current = "";
            if (entry.type === "medición") {
                const resource = measurementMap[entry.id];
                if (resource) {
                    current = I18n.localize(resource.measurement);
                }
            } else if (entry.type === "término") {
                const resource = glossaryMap[entry.id];
                if (resource) {
                    current = I18n.localize(resource.term);
                }
            }

            if (typeof current === "string" && current.trim()) {
                return current;
            }

            const fallbackTitle = I18n.localize(entry.title);
            if (typeof fallbackTitle === "string" && fallbackTitle.trim()) {
                return fallbackTitle;
            }

            return typeof entry.id === "string" ? entry.id : "";
        };

        const getLocalizedTypeLabel = (type) => {
            if (type === "medición") {
                return I18n.translate("label.measurement");
            }
            if (type === "término") {
                return I18n.translate("label.term");
            }
            return I18n.localize({
                es: "Elemento",
                en: "Item"
            });
        };

        const recents = Storage.getRecents() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${escapeHTML(I18n.translate("nav.home"))}</a>
                <h2>${escapeHTML(I18n.translate("nav.recents"))}</h2>
            </div>
        `;

        if (recents.length === 0) {
            html += `
                <div class="card error-card">
                    <p>${escapeHTML(I18n.translate("state.no_recents"))}</p>
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        html += `
            <div style="text-align: right; margin-bottom: 1rem;">
                <button id="clear-all-recs" class="btn-secondary" style="display: inline-flex; min-height: 38px; padding: 0.25rem 1rem;">${escapeHTML(I18n.translate("action.clear_history"))}</button>
            </div>
            <div class="cards-list">
        `;

        recents.forEach(r => {
            const resolvedTitle = resolveCurrentTitle(r);
            let link = "#/";
            let badgeClass = "";

            if (r.type === "medición") {
                link = `#/medicion/${r.id}`;
                badgeClass = "badge-medicion";
            } else if (r.type === "término") {
                link = `#/glosario/${r.id}`;
                badgeClass = "badge-termino";
            }

            html += `
                <div class="card clinical-card" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 1rem;">
                    <div>
                        <a href="${escapeHTML(link)}" style="text-decoration: none; font-weight: 600; color: var(--primary-light); font-size: 1.05rem;">${escapeHTML(resolvedTitle)}</a>
                        <span class="result-badge ${escapeHTML(badgeClass)}" style="margin-left: 0.5rem;">${escapeHTML(getLocalizedTypeLabel(r.type))}</span>
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
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        const refs = await DataLoader.getReferences() || [];

        let html = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${escapeHTML(I18n.translate("label.clinical_references_title"))}</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 1rem;">
        `;

        refs.forEach(r => {
            html += `
                <div style="border-bottom: 1px solid var(--border-light); padding-bottom: 0.75rem; font-size: 0.9rem;">
                    <p style="margin-bottom: 0.25rem;">${escapeHTML(r.citation)}</p>
                    <span style="font-size: 0.75rem; color: var(--text-muted-light);">${escapeHTML(I18n.translate("label.cited_on_pdf_page", { page: r.source_page }))}</span>
                </div>
            `;
        });

        html += `
                <p style="font-size: 0.8rem; color: var(--text-muted-light); font-style: italic; margin-top: 1rem;">
                    <strong>${escapeHTML(I18n.translate("label.editorial_note"))}:</strong> ${escapeHTML(I18n.translate("label.editorial_note_text"))}
                </p>
            </div>
        `;
        container.innerHTML = html;
    },

    renderAbout(container) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        container.innerHTML = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${escapeHTML(I18n.translate("label.about_title"))}</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 1rem; font-size: 0.95rem;">
                <p><strong>${escapeHTML(I18n.translate("app.name"))}</strong> ${escapeHTML(I18n.translate("label.about_app_description"))}</p>
                <p>${escapeHTML(I18n.translate("label.about_training_objective"))}</p>
                <p>${escapeHTML(I18n.translate("label.about_development_prefix"))} <strong>Hospital San Rafael de Alajuela (HSRA)</strong> ${escapeHTML(I18n.translate("label.about_development_course"))} <strong>${escapeHTML(I18n.translate("label.about_internal_medicine_program"))}</strong>.</p>
                <p>${escapeHTML(I18n.translate("label.about_source_prefix"))} <em>Mediciones POCUS Cardiaco Adultos - Glosario</em> ${escapeHTML(I18n.translate("label.about_source_suffix"))}</p>
            </div>
        `;
    },

    async renderQuizzesList(container) {
        let quizzes = [];
        try {
            quizzes = await DataLoader.getQuizzes();
        } catch (e) {
            console.error("Router: Error cargando cuestionarios:", e);
        }
        if (!Array.isArray(quizzes)) {
            quizzes = [];
        }
        QuizEngine.renderQuizList(container, quizzes);
    },

    async renderQuizFlow(container, id) {
        const escapeHTML = (str) => {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        };

        let decodedId = "";
        try {
            decodedId = decodeURIComponent(id || "");
        } catch (e) {
            decodedId = id || "";
        }

        if (!QuizEngine.isValidStableId(decodedId)) {
            this.render404(container);
            return;
        }

        let quizzes = [];
        try {
            quizzes = await DataLoader.getQuizzes();
        } catch (e) {
            console.error("Router: Error al inicializar flujo de cuestionario:", e);
        }

        if (!Array.isArray(quizzes)) {
            quizzes = [];
        }

        const quiz = QuizEngine.getQuizById(quizzes, decodedId);
        if (!quiz || quiz.review_status !== "approved" || !QuizEngine.validateQuizDefinition(quiz)) {
            container.innerHTML = `
                <div class="navigation-header">
                    <a href="#/cuestionarios" class="btn-back">← ${escapeHTML(I18n.translate("nav.back_to_quizzes"))}</a>
                    <h2>${escapeHTML(I18n.translate("error.quiz_unavailable_title"))}</h2>
                </div>
                <div class="card error-card">
                    <h3>${escapeHTML(I18n.translate("error.quiz_unavailable_title"))}</h3>
                    <p>${escapeHTML(I18n.translate("error.quiz_unavailable_text"))}</p>
                    <a href="#/cuestionarios" class="btn-primary" style="display: inline-block; margin-top: 1rem; text-decoration: none;">${escapeHTML(I18n.translate("nav.back_to_list"))}</a>
                </div>
            `;
            return;
        }

        let mediaResources = [];
        const hasMedia = quiz.questions.some(q => Array.isArray(q.media_resource_ids) && q.media_resource_ids.length > 0);
        if (hasMedia) {
            try {
                mediaResources = await DataLoader.getMediaResources() || [];
                if (!Array.isArray(mediaResources)) {
                    mediaResources = [];
                }
            } catch (e) {
                console.warn("Router: Error cargando recursos multimedia:", e);
            }
        }

        const session = QuizEngine.restoreQuizSession(quiz, decodedId);
        QuizEngine.refreshQuizView(container, quiz, session, mediaResources);
    },

    // INSTALACIÓN
    renderInstall(container) {
        container.innerHTML = `
            <div class="navigation-header">
                <a href="#/" class="btn-back">← ${I18n.translate("nav.home")}</a>
                <h2>${I18n.translate("label.install_title")}</h2>
            </div>

            <div style="background-color: var(--card-bg-light); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-light); font-size: 0.95rem; display: flex; flex-direction: column; gap: 1.5rem;">
                <p>${I18n.translate("label.install_text")}</p>

                <div class="install-section">
                    <h3 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🍎</span> ${I18n.translate("label.install_ios_title")}
                    </h3>
                    <p style="margin-bottom: 0.75rem; font-weight: 600;">${I18n.translate("label.inst_iphone_steps")}</p>
                    <ol style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem;">
                        <li>${I18n.translate("label.inst_iphone_step1")}</li>
                        <li>${I18n.translate("label.inst_iphone_step2")}</li>
                        <li>${I18n.translate("label.inst_iphone_step3")}</li>
                        <li>${I18n.translate("label.inst_iphone_step4")}</li>
                        <li>${I18n.translate("label.inst_iphone_step5")}</li>
                        <li>${I18n.translate("label.inst_iphone_step6")}</li>
                    </ol>
                </div>

                <div class="install-section">
                    <h3 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🤖</span> ${I18n.translate("label.install_android_title")}
                    </h3>
                    <p style="margin-bottom: 0.75rem; font-weight: 600;">${I18n.translate("label.install_android_steps")}</p>
                    <ol style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem;">
                        <li>${I18n.translate("label.install_android_step1")}</li>
                        <li>${I18n.translate("label.install_android_step2")}</li>
                        <li>${I18n.translate("label.install_android_step3")}</li>
                        <li>${I18n.translate("label.install_android_step4")}</li>
                        <li>${I18n.translate("label.install_android_step5")}</li>
                    </ol>
                </div>

                <div class="safety-banner" style="margin-top: 0.5rem;">
                    <strong>${I18n.translate("label.pwa_note_title")}:</strong> ${I18n.translate("label.pwa_note_text")}
                </div>
            </div>
        `;
    }
};

// Escuchar cambios de hash en la URL
window.addEventListener("hashchange", () => Router.route());

// Escuchar cambios globales de idioma para volver a renderizar la vista actual sin alterar el historial ni recargar
window.addEventListener("pocus-language-changed", () => {
    const hash = window.location.hash || '#/';
    // Proteger las rutas de cuestionarios activos frente a un rerender de la ruta completa
    if (hash.startsWith('#/cuestionarios/') || hash.startsWith('#/cuestionario')) {
        // En cuestionarios, permitimos que la interfaz de cabecera estática del documento cambie
        // pero NO volvemos a enrutar/destruir el flujo del cuestionario.
        return;
    }
    Router.route();
});
