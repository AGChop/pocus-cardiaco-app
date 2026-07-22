// Módulo de analítica educativa inactiva para POCUS Cardíaco
const Analytics = {
    // Lista permitida de eventos futuros
    ALLOWED_EVENTS: [
        'app_opened',
        'route_viewed',
        'protocol_opened',
        'protocol_step_viewed',
        'protocol_completed',
        'window_opened',
        'measurement_opened',
        'quiz_started',
        'quiz_completed',
        'media_opened'
    ],

    // Clave de almacenamiento para consentimiento
    CONSENT_KEY: 'pocus_analytics_consent',

    // Inicializa la analítica leyendo el consentimiento (inactivo en esta fase)
    initializeAnalytics() {
        try {
            // El consentimiento inicial por defecto es false si no está guardado
            const consent = this.getAnalyticsConsent();
            // No realiza inicializaciones de red ni rastreos activos
        } catch (e) {
            // Silencioso ante errores
        }
    },

    // Registra un evento educativo (inactivo y seguro, no envía a la red ni logea actividad de usuario)
    trackEvent(eventName, metadata = {}) {
        try {
            if (!this.isAnalyticsEnabled()) {
                return;
            }

            // Validar si el evento está en la lista de permitidos
            if (!this.ALLOWED_EVENTS.includes(eventName)) {
                return; // Ignorar silenciosamente eventos no permitidos
            }

            // En esta fase de preparación, trackEvent no guarda, envía ni imprime en consola
            // los metadatos o rutas del usuario para mantener la privacidad.
        } catch (e) {
            // Silencioso ante errores
        }
    },

    // Registra la vista de una ruta (inactivo y seguro)
    trackPageView(route) {
        try {
            this.trackEvent('route_viewed', { route });
        } catch (e) {
            // Silencioso ante errores
        }
    },

    // Guarda el consentimiento en el almacenamiento centralizado
    setAnalyticsConsent(value) {
        try {
            const consentValue = !!value;
            if (typeof Storage !== 'undefined' && typeof Storage.setPreference === 'function') {
                Storage.setPreference(this.CONSENT_KEY, consentValue);
            }
        } catch (e) {
            // Silencioso ante errores
        }
    },

    // Obtiene el consentimiento desde el almacenamiento centralizado (por defecto false)
    getAnalyticsConsent() {
        try {
            if (typeof Storage !== 'undefined' && typeof Storage.getPreference === 'function') {
                return !!Storage.getPreference(this.CONSENT_KEY, false);
            }
        } catch (e) {
            // Silencioso ante errores
        }
        return false;
    },

    // Determina si el consentimiento está habilitado
    isAnalyticsEnabled() {
        return this.getAnalyticsConsent();
    }
};
