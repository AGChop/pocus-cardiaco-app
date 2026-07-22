// Manejador de almacenamiento local (Favoritos y Recientes)
const Storage = {
    // Claves de localStorage
    KEYS: {
        FAVORITES: 'pocus_favorites',
        RECENTS: 'pocus_recents'
    },

    // Almacenamiento en memoria como respaldo (fallbacks)
    _memoryLocalStorage: {},
    _memorySessionStorage: {},

    // --- FAVORITOS ---
    getFavorites() {
        try {
            const favs = localStorage.getItem(this.KEYS.FAVORITES);
            return favs ? JSON.parse(favs) : (this._memoryLocalStorage[this.KEYS.FAVORITES] || []);
        } catch (e) {
            console.warn("Storage: Error al leer favoritos de localStorage, usando respaldo en memoria:", e);
            return this._memoryLocalStorage[this.KEYS.FAVORITES] || [];
        }
    },

    isFavorite(type, id) {
        const favs = this.getFavorites();
        return favs.some(item => item.type === type && item.id === id);
    },

    toggleFavorite(type, id, title) {
        let favs = this.getFavorites();
        const index = favs.findIndex(item => item.type === type && item.id === id);
        
        if (index > -1) {
            favs.splice(index, 1); // Remover si ya existe
            console.log(`Removido de favoritos: ${title}`);
        } else {
            favs.push({ type, id, title, timestamp: Date.now() }); // Agregar
            console.log(`Agregado de favoritos: ${title}`);
        }
        try {
            localStorage.setItem(this.KEYS.FAVORITES, JSON.stringify(favs));
        } catch (e) {
            console.warn("Storage: Error al guardar favoritos en localStorage, usando respaldo en memoria:", e);
            this._memoryLocalStorage[this.KEYS.FAVORITES] = favs;
        }
        return index === -1; // Retorna true si se agregó, false si se removió
    },

    clearFavorites() {
        try {
            localStorage.removeItem(this.KEYS.FAVORITES);
        } catch (e) {
            console.warn("Storage: Error al remover favoritos de localStorage:", e);
        }
        this._memoryLocalStorage[this.KEYS.FAVORITES] = [];
        console.log("Todos los favoritos han sido borrados.");
    },

    // --- RECIENTES ---
    getRecents() {
        try {
            const recs = localStorage.getItem(this.KEYS.RECENTS);
            return recs ? JSON.parse(recs) : (this._memoryLocalStorage[this.KEYS.RECENTS] || []);
        } catch (e) {
            console.warn("Storage: Error al leer recientes de localStorage, usando respaldo en memoria:", e);
            return this._memoryLocalStorage[this.KEYS.RECENTS] || [];
        }
    },

    addRecent(type, id, title) {
        let recs = this.getRecents();
        // Evitar duplicados
        recs = recs.filter(item => !(item.type === type && item.id === id));
        // Agregar al inicio de la lista
        recs.unshift({ type, id, title, timestamp: Date.now() });
        // Limitar a los últimos 10
        if (recs.length > 10) {
            recs.pop();
        }
        try {
            localStorage.setItem(this.KEYS.RECENTS, JSON.stringify(recs));
        } catch (e) {
            console.warn("Storage: Error al guardar recientes en localStorage, usando respaldo en memoria:", e);
            this._memoryLocalStorage[this.KEYS.RECENTS] = recs;
        }
        console.log(`Visto recientemente: ${title}`);
    },

    clearRecents() {
        try {
            localStorage.removeItem(this.KEYS.RECENTS);
        } catch (e) {
            console.warn("Storage: Error al remover recientes de localStorage:", e);
        }
        this._memoryLocalStorage[this.KEYS.RECENTS] = [];
        console.log("Historial de elementos recientes borrado.");
    },

    // --- PREFERENCIAS (localStorage) ---
    getPreference(key, fallback = null) {
        try {
            const val = localStorage.getItem(key);
            if (val === null) {
                return this._memoryLocalStorage[key] !== undefined ? this._memoryLocalStorage[key] : fallback;
            }
            try {
                return JSON.parse(val);
            } catch (e) {
                return val; // Por si se guardó como string plano (ej. temas anteriores)
            }
        } catch (e) {
            console.warn(`Storage: Error al obtener preferencia para clave ${key}, usando memoria:`, e);
            return this._memoryLocalStorage[key] !== undefined ? this._memoryLocalStorage[key] : fallback;
        }
    },

    setPreference(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn(`Storage: Error al guardar preferencia para clave ${key}, usando memoria:`, e);
        }
        this._memoryLocalStorage[key] = value;
    },

    removePreference(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn(`Storage: Error al eliminar preferencia para clave ${key}:`, e);
        }
        delete this._memoryLocalStorage[key];
    },

    // --- IDIOMA GLOBAL ---
    getLanguage() {
        const lang = this.getPreference('pocus_language', 'es');
        if (lang === 'es' || lang === 'en') {
            return lang;
        }
        return 'es';
    },

    setLanguage(language) {
        if (language === 'es' || language === 'en') {
            this.setPreference('pocus_language', language);
        } else {
            console.warn(`Storage: Intento de establecer idioma inválido: ${language}`);
        }
    },

    // --- ESTADO TEMPORAL (sessionStorage) ---
    getSessionState(key, fallback = null) {
        try {
            const val = sessionStorage.getItem(key);
            if (val === null) {
                return this._memorySessionStorage[key] !== undefined ? this._memorySessionStorage[key] : fallback;
            }
            try {
                return JSON.parse(val);
            } catch (e) {
                return val; // Por si se guardó como string plano
            }
        } catch (e) {
            console.warn(`Storage: Error al obtener estado de sesión para clave ${key}, usando memoria:`, e);
            return this._memorySessionStorage[key] !== undefined ? this._memorySessionStorage[key] : fallback;
        }
    },

    setSessionState(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn(`Storage: Error al guardar estado de sesión para clave ${key}, usando memoria:`, e);
        }
        this._memorySessionStorage[key] = value;
    },

    removeSessionState(key) {
        try {
            sessionStorage.removeItem(key);
        } catch (e) {
            console.warn(`Storage: Error al eliminar estado de sesión para clave ${key}:`, e);
        }
        delete this._memorySessionStorage[key];
    },

    // --- PROGRESO EDUCATIVO FUTURO (localStorage) ---
    getProgress(resourceType, resourceId, fallback = null) {
        const key = `pocus_progress_${resourceType}_${resourceId}`;
        return this.getPreference(key, fallback);
    },

    saveProgress(resourceType, resourceId, value) {
        const key = `pocus_progress_${resourceType}_${resourceId}`;
        this.setPreference(key, value);
    },

    removeProgress(resourceType, resourceId) {
        const key = `pocus_progress_${resourceType}_${resourceId}`;
        this.removePreference(key);
    },

    clearLearningProgress() {
        const prefix = "pocus_progress_";
        try {
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith(prefix)) {
                    keysToRemove.push(key);
                }
            }
            keysToRemove.forEach(k => {
                localStorage.removeItem(k);
                const progressKey = k.replace(prefix, "");
                const underscoreIndex = progressKey.indexOf("_");
                if (underscoreIndex > -1) {
                    const resourceType = progressKey.substring(0, underscoreIndex);
                    const resourceId = progressKey.substring(underscoreIndex + 1);
                    delete this._memoryLocalStorage[`pocus_progress_${resourceType}_${resourceId}`];
                }
            });
        } catch (e) {
            console.warn("Storage: Error al limpiar progreso en localStorage:", e);
        }
        // Limpiar también en memoria de de respaldo
        Object.keys(this._memoryLocalStorage).forEach(k => {
            if (k.startsWith(prefix)) {
                delete this._memoryLocalStorage[k];
            }
        });
        console.log("Progreso educativo de aprendizaje borrado.");
    }
};
