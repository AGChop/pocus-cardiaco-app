// Cargador de datos clínicos desde archivos JSON
const DataLoader = {
    cache: {},

    // Función para obtener cualquier recurso JSON de forma asíncrona
    async fetchResource(name) {
        if (this.cache[name]) {
            return this.cache[name];
        }
        try {
            if (name === 'protocols') {
                const approvedData = await this.fetchResourceDirect('protocols');
                if (!approvedData) {
                    return null;
                }
                const betaData = await this.fetchResourceDirect('protocols.beta');

                // Fusionar aprobados y beta
                const combined = { ...approvedData };
                combined.protocols = [...(approvedData.protocols || [])];
                combined.references = [...(approvedData.references || [])];
                if (betaData && typeof betaData === 'object' && Array.isArray(betaData.protocols)) {
                    combined.protocols = combined.protocols.concat(betaData.protocols);
                    if (Array.isArray(betaData.references)) {
                        const refIds = new Set(combined.references.map(r => r.id));
                        betaData.references.forEach(ref => {
                            if (ref && ref.id && !refIds.has(ref.id)) {
                                combined.references.push(ref);
                                refIds.add(ref.id);
                            }
                        });
                    }
                }
                this.cache['protocols'] = combined;
                return combined;
            }

            return await this.fetchResourceDirect(name);
        } catch (error) {
            console.error(`Error cargando la base de datos ${name}:`, error);
            return null;
        }
    },

    async fetchResourceDirect(name) {
        try {
            const response = await fetch(`data/${name}.json`);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} al cargar ${name}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error cargando recurso directo ${name}:`, error);
            return null;
        }
    },

    // Cargar borrador/aprobado de prioridades con degradación segura
    async getPriority() {
        if (this.cache['measurement-priority']) {
            return this.cache['measurement-priority'];
        }
        try {
            const response = await fetch('data/measurement-priority.json');
            if (!response.ok) {
                console.warn(`Advertencia: No se pudo cargar data/measurement-priority.json (${response.status}). Se usará el orden original.`);
                return null;
            }
            const data = await response.json();
            this.cache['measurement-priority'] = data;
            return data;
        } catch (error) {
            console.warn('Advertencia: Excepción al cargar data/measurement-priority.json. Se usará el orden original.', error);
            return null;
        }
    },

    async getSections() { return this.fetchResource('sections'); },

    async getMeasurements() {
        const measurements = await this.fetchResource('measurements');
        if (!measurements) return null;

        // Intentar combinar con las prioridades de forma no destructiva
        const priorityData = await this.getPriority();
        if (!priorityData || !Array.isArray(priorityData.priorities)) {
            return measurements;
        }

        const priorityMap = new Map();
        priorityData.priorities.forEach(p => {
            if (p && p.measurement_id) {
                priorityMap.set(p.measurement_id, p);
            }
        });

        return measurements.map(m => {
            const p = priorityMap.get(m.id);
            if (!p) {
                return {
                    ...m,
                    priority_tier: 99,
                    priority_label: "Sin priorizar",
                    pocus_scope: "contextual",
                    display_order: 9999,
                    original_order: m.order || 9999,
                    priority_rationale: "",
                    priority_confidence: "low"
                };
            }
            return {
                ...m,
                priority_tier: p.priority_tier,
                priority_label: p.priority_label,
                pocus_scope: p.pocus_scope,
                display_order: p.display_order,
                original_order: p.original_order !== undefined ? p.original_order : (m.order || 9999),
                priority_rationale: p.rationale || "",
                priority_confidence: p.confidence || "high"
            };
        });
    },

    async getGlossary() { return this.fetchResource('glossary'); },
    async getAbbreviations() { return this.fetchResource('abbreviations'); },
    async getClassifications() { return this.fetchResource('classifications'); },
    async getMinimumPocusSet() { return this.fetchResource('minimum_pocus_set'); },
    async getUnitWarnings() { return this.fetchResource('unit_warnings'); },
    async getReferences() { return this.fetchResource('references'); },
    async getMetadata() { return this.fetchResource('metadata'); },
    async getWindows() { return this.fetchResource('windows'); },
    async getMediaResources() {
        try {
            const data = await this.fetchResource('media-resources');
            if (data && typeof data === 'object' && Array.isArray(data.resources)) {
                return data.resources;
            }
            console.warn("DataLoader: Estructura de media-resources inválida, se esperaba un objeto con una lista 'resources'.");
            return [];
        } catch (error) {
            console.warn("DataLoader: Error al cargar media-resources.json:", error);
            return [];
        }
    },
    async getQuizzes() {
        try {
            const data = await this.fetchResource('quizzes');
            if (data && typeof data === 'object' && Array.isArray(data.quizzes)) {
                return data.quizzes;
            }
            console.warn("DataLoader: Estructura de quizzes inválida, se esperaba un objeto con una lista 'quizzes'.");
            return [];
        } catch (error) {
            console.warn("DataLoader: Error al cargar quizzes.json:", error);
            return [];
        }
    },
    async getTranslations() {
        try {
            const data = await this.fetchResource('translations');
            if (data && typeof data === 'object' && data.translations) {
                return data;
            }
            console.warn("DataLoader: Estructura de translations inválida, se esperaba un objeto con una clave 'translations'.");
        } catch (error) {
            console.warn("DataLoader: Error al cargar translations.json:", error);
        }
        // Retornar estructura mínima segura si falla la carga
        return {
            schema_version: "1.0",
            default_language: "es",
            supported_languages: ["es", "en"],
            translations: {
                "language.selector_label": { "es": "Seleccionar idioma", "en": "Select language" },
                "language.spanish": { "es": "ES", "en": "ES" },
                "language.english": { "es": "EN", "en": "EN" }
            }
        };
    }
};
