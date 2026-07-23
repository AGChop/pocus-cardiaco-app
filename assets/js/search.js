// Motor de búsqueda inteligente simplificado
const Search = {
    // Función auxiliar defensiva para obtener todo el texto indexable de un valor
    getSearchableText(value) {
        if (value === null || value === undefined) return "";
        if (typeof value === "string") return value;
        if (typeof value === "number" || typeof value === "boolean") return value.toString();
        if (Array.isArray(value)) {
            return value.map(item => this.getSearchableText(item)).filter(t => t !== "").join(" ");
        }
        if (typeof value === "object") {
            // Comprobar si es un objeto localizado con es o en
            if ("es" in value || "en" in value) {
                const parts = [];
                if (value.es) parts.push(this.getSearchableText(value.es));
                if (value.en) parts.push(this.getSearchableText(value.en));
                return parts.join(" ");
            }
            // Objeto técnico no localizado: retornar una cadena vacía para evitar conversiones no deseadas de objetos
            return "";
        }
        return "";
    },

    // Función para normalizar texto (remueve tildes, minúsculas, espacios extra)
    normalizeText(text) {
        const searchable = this.getSearchableText(text);
        if (!searchable) return "";
        let normalized = searchable.toLowerCase();
        
        // Remover tildes y diacríticos comunes
        normalized = normalized.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        
        // Normalizar apóstrofes y comillas simples
        normalized = normalized.replace(/['’´‘]/g, "'");
        
        // Reemplazar espacios múltiples por uno solo y limpiar extremos
        normalized = normalized.replace(/\s+/g, " ").trim();
        
        return normalized;
    },

    // Buscar equivalencias clínicas comunes para enriquecer la consulta
    getEquivalences(query) {
        const normalizedQuery = this.normalizeText(query);
        const equivalences = {
            "ventriculo": "ventrículo",
            "fraccion": "fracción",
            "e prima": "e'",
            "s prima": "s'",
            "vi": "lv",
            "lv": "vi",
            "vd": "rv",
            "rv": "vd",
            "tsvi": "lvot",
            "lvot": "tsvi",
            "tsvd": "rvot",
            "rvot": "tsvd",
            "rvp": "pvr",
            "pvr": "rvp",
            "fevi": "lvef",
            "lvef": "fevi",
            "pasp": "presion sistolica de arteria pulmonar"
        };
        return equivalences[normalizedQuery] || "";
    },

    // Buscar coincidencias ordenando por relevancia
    async searchGlobal(query) {
        if (!query || query.trim() === "") return [];

        const normalizedQuery = this.normalizeText(query);
        const equiv = this.getEquivalences(query);
        const normalizedEquiv = equiv ? this.normalizeText(equiv) : "";

        // Cargar bases de datos clínicas
        const measurements = await DataLoader.getMeasurements() || [];
        const glossary = await DataLoader.getGlossary() || [];
        const abbreviations = await DataLoader.getAbbreviations() || [];
        const classifications = await DataLoader.getClassifications() || [];
        const windows = await DataLoader.getWindows() || [];
        const protocolsData = await DataLoader.fetchResource("protocols") || { protocols: [] };
        const protocols = protocolsData.protocols || [];

        const results = [];

        // Función interna para evaluar y puntuar coincidencia
        const calculateScore = (item, type) => {
            let score = 0;
            
            // Campos a examinar según tipo de elemento
            let name = "";
            let abbreviation = "";
            let aliases = [];
            let definition = "";
            let formula = "";
            let interpretation = "";
            let extraFields = "";

            if (type === "medición") {
                name = item.measurement;
                abbreviation = item.abbreviation;
                aliases = item.aliases || [];
                formula = item.formula_or_method;
                interpretation = item.interpretation_limitations;
                // Campos de ventana asociados a la medición
                extraFields = [
                    item.section_id || "",
                    item.primary_window || "",
                    item.preferred_view || "",
                    item.modality || "",
                    item.acquisition_timing || "",
                    item.acquisition_key || "",
                    Array.isArray(item.alternate_windows) ? item.alternate_windows.join(" ") : ""
                ].join(" ");
            } else if (type === "término") {
                name = item.term;
                aliases = item.aliases || [];
                definition = item.definition;
                interpretation = item.acquisition_utility_limitation;
            } else if (type === "abreviatura") {
                name = item.abbreviation;
                definition = item.meaning;
            } else if (type === "clasificación") {
                name = item.name;
                definition = item.note || "";
            } else if (type === "ventana") {
                name = item.window;
                abbreviation = item.abbreviation;
                definition = [
                    item.typical_probe_position || "",
                    item.typical_marker_orientation || "",
                    item.favored_structures || "",
                    item.favored_measurements || ""
                ].join(" ");
            } else if (type === "protocolo") {
                name = item.name_es;
                abbreviation = item.acronym;
                aliases = [item.name_en || ""];
                definition = [
                    item.purpose || "",
                    item.clinical_context || "",
                    item.target_population || "",
                    Array.isArray(item.components) ? item.components.map(c => [
                        c.name_es || "",
                        c.name_en || "",
                        (c.clinical_questions || []).join(" "),
                        (c.targets || []).join(" ")
                    ].join(" ")).join(" ") : ""
                ].join(" ");
            }

            // Función auxiliar interna para ver si hay coincidencia exacta o parcial en campos bilingües/strings/arrays
            const matchField = (field, queryNormalized, mode) => {
                if (!field) return false;
                if (typeof field === "string") {
                    const norm = Search.normalizeText(field);
                    if (mode === "exact") return norm === queryNormalized;
                    if (mode === "startsWith") return norm.startsWith(queryNormalized);
                    if (mode === "includes") return norm.includes(queryNormalized);
                }
                if (typeof field === "number" || typeof field === "boolean") {
                    const norm = field.toString().toLowerCase();
                    if (mode === "exact") return norm === queryNormalized;
                    if (mode === "startsWith") return norm.startsWith(queryNormalized);
                    if (mode === "includes") return norm.includes(queryNormalized);
                }
                if (Array.isArray(field)) {
                    return field.some(item => matchField(item, queryNormalized, mode));
                }
                if (typeof field === "object") {
                    if ("es" in field || "en" in field) {
                        const normEs = Search.normalizeText(field.es);
                        const normEn = Search.normalizeText(field.en);
                        if (mode === "exact") return normEs === queryNormalized || normEn === queryNormalized;
                        if (mode === "startsWith") return normEs.startsWith(queryNormalized) || normEn.startsWith(queryNormalized);
                        if (mode === "includes") return normEs.includes(queryNormalized) || normEn.includes(queryNormalized);
                    }
                }
                return false;
            };

            // Reglas de puntuación basadas en prioridad
            // 1. Coincidencia exacta
            if (matchField(name, normalizedQuery, "exact") || (normalizedEquiv && matchField(name, normalizedEquiv, "exact"))) {
                score += 100;
            }
            // 2. Coincidencia en abreviatura
            else if (abbreviation && (matchField(abbreviation, normalizedQuery, "exact") || matchField(abbreviation, normalizedQuery, "includes"))) {
                score += 90;
            }
            // 3. Coincidencia en alias
            else if (aliases && matchField(aliases, normalizedQuery, "includes")) {
                score += 85;
            }
            // 4. Coincidencia al inicio del nombre
            else if (matchField(name, normalizedQuery, "startsWith")) {
                score += 80;
            }
            // 5. Coincidencia parcial en nombre
            else if (matchField(name, normalizedQuery, "includes")) {
                score += 70;
            }
            // 6. Coincidencia en definición / estructuras / mediciones / posición / orientación
            else if (matchField(definition, normalizedQuery, "includes")) {
                score += 50;
            }
            // 7. Coincidencia en campos adicionales de ventana en medición
            else if (matchField(extraFields, normalizedQuery, "includes")) {
                score += 45;
            }
            // 8. Coincidencia en fórmula
            else if (matchField(formula, normalizedQuery, "includes")) {
                score += 40;
            }
            // 9. Coincidencia en interpretación o limitación
            else if (matchField(interpretation, normalizedQuery, "includes")) {
                score += 30;
            }

            return score;
        };

        // Procesar mediciones
        measurements.forEach(item => {
            const score = calculateScore(item, "medición");
            if (score > 0) results.push({ type: "medición", item, score });
        });

        // Procesar glosario
        glossary.forEach(item => {
            const score = calculateScore(item, "término");
            if (score > 0) results.push({ type: "término", item, score });
        });

        // Procesar abreviaturas
        abbreviations.forEach(item => {
            const score = calculateScore(item, "abreviatura");
            if (score > 0) results.push({ type: "abreviatura", item, score });
        });

        // Procesar clasificaciones
        classifications.forEach(item => {
            const score = calculateScore(item, "clasificación");
            if (score > 0) results.push({ type: "clasificación", item, score });
        });

        // Procesar ventanas ecocardiográficas
        windows.forEach(item => {
            const score = calculateScore(item, "ventana");
            if (score > 0) results.push({ type: "ventana", item, score });
        });

        // Procesar protocolos
        protocols.forEach(item => {
            const score = calculateScore(item, "protocolo");
            if (score > 0) results.push({ type: "protocolo", item, score });
        });

        // Ordenar de mayor a menor puntuación (relevancia). Desempate secundario por prioridad clínica.
        return results.sort((a, b) => {
            if (b.score !== a.score) {
                return b.score - a.score;
            }
            // Desempate por priority_tier ascendente (si el elemento es una medición priorizada)
            const tierA = (a.item && a.item.priority_tier !== undefined) ? a.item.priority_tier : 99;
            const tierB = (b.item && b.item.priority_tier !== undefined) ? b.item.priority_tier : 99;
            if (tierA !== tierB) return tierA - tierB;

            const orderA = (a.item && a.item.display_order !== undefined) ? a.item.display_order : 9999;
            const orderB = (b.item && b.item.display_order !== undefined) ? b.item.display_order : 9999;
            return orderA - orderB;
        });
    }
};
