// Manejador de almacenamiento local (Favoritos y Recientes)
const Storage = {
    // Claves de localStorage
    KEYS: {
        FAVORITES: 'pocus_favorites',
        RECENTS: 'pocus_recents'
    },

    // --- FAVORITOS ---
    getFavorites() {
        const favs = localStorage.getItem(this.KEYS.FAVORITES);
        return favs ? JSON.parse(favs) : [];
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
            console.log(`Agregado a favoritos: ${title}`);
        }
        localStorage.setItem(this.KEYS.FAVORITES, JSON.stringify(favs));
        return index === -1; // Retorna true si se agregó, false si se removió
    },

    clearFavorites() {
        localStorage.removeItem(this.KEYS.FAVORITES);
        console.log("Todos los favoritos han sido borrados.");
    },

    // --- RECIENTES ---
    getRecents() {
        const recs = localStorage.getItem(this.KEYS.RECENTS);
        return recs ? JSON.parse(recs) : [];
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
        localStorage.setItem(this.KEYS.RECENTS, JSON.stringify(recs));
        console.log(`Visto recientemente: ${title}`);
    },

    clearRecents() {
        localStorage.removeItem(this.KEYS.RECENTS);
        console.log("Historial de elementos recientes borrado.");
    }
};
