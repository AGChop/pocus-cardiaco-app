// Cargador de datos clínicos desde archivos JSON
const DataLoader = {
    cache: {},

    // Función para obtener cualquier recurso JSON de forma asíncrona
    async fetchResource(name) {
        if (this.cache[name]) {
            return this.cache[name];
        }
        try {
            // Usamos rutas relativas para compatibilidad con subcarpetas en GitHub Pages
            const response = await fetch(`data/${name}.json`);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} al cargar ${name}`);
            }
            const data = await response.json();
            this.cache[name] = data;
            return data;
        } catch (error) {
            console.error(`Error cargando la base de datos ${name}:`, error);
            return null;
        }
    },

    async getSections() { return this.fetchResource('sections'); },
    async getMeasurements() { return this.fetchResource('measurements'); },
    async getGlossary() { return this.fetchResource('glossary'); },
    async getAbbreviations() { return this.fetchResource('abbreviations'); },
    async getClassifications() { return this.fetchResource('classifications'); },
    async getMinimumPocusSet() { return this.fetchResource('minimum_pocus_set'); },
    async getUnitWarnings() { return this.fetchResource('unit_warnings'); },
    async getReferences() { return this.fetchResource('references'); },
    async getMetadata() { return this.fetchResource('metadata'); }
};
