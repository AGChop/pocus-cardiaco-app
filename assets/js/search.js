// Motor de búsqueda inteligente simplificado
const Search = {
    // Función para normalizar texto (remueve tildes, minúsculas, espacios extra)
    normalizeText(text) {
        if (!text) return "";
        let normalized = text.toString().toLowerCase();
        
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

            if (type === "medición") {
                name = item.measurement;
                abbreviation = item.abbreviation;
                aliases = item.aliases || [];
                formula = item.formula_or_method;
                interpretation = item.interpretation_limitations;
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
            }

            const nName = this.normalizeText(name);
            const nAbbr = this.normalizeText(abbreviation);
            const nDef = this.normalizeText(definition);
            const nForm = this.normalizeText(formula);
            const nInterp = this.normalizeText(interpretation);

            // Reglas de puntuación basadas en prioridad
            // 1. Coincidencia exacta
            if (nName === normalizedQuery || (normalizedEquiv && nName === normalizedEquiv)) {
                score += 100;
            }
            // 2. Coincidencia en abreviatura
            else if (abbreviation && (nAbbr === normalizedQuery || nAbbr.includes(normalizedQuery))) {
                score += 90;
            }
            // 3. Coincidencia en alias
            else if (aliases.some(alias => {
                const nAlias = this.normalizeText(alias);
                return nAlias === normalizedQuery || nAlias.includes(normalizedQuery);
            })) {
                score += 85;
            }
            // 4. Coincidencia al inicio del nombre
            else if (nName.startsWith(normalizedQuery)) {
                score += 80;
            }
            // 5. Coincidencia parcial en nombre
            else if (nName.includes(normalizedQuery)) {
                score += 70;
            }
            // 6. Coincidencia en definición
            else if (nDef.includes(normalizedQuery)) {
                score += 50;
            }
            // 7. Coincidencia en fórmula
            else if (nForm.includes(normalizedQuery)) {
                score += 40;
            }
            // 8. Coincidencia en interpretación o limitación
            else if (nInterp.includes(normalizedQuery)) {
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

        // Ordenar de mayor a menor puntuación (relevancia)
        return results.sort((a, b) => b.score - a.score);
    }
};
