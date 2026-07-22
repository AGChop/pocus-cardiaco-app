// Manejador del Tema Visual (Claro, Oscuro, Automático)
const Theme = {
    KEY: 'pocus_theme_preference',

    init() {
        const themeSelect = document.getElementById("theme-select");
        const savedTheme = Storage.getPreference(this.KEY, 'auto');

        if (themeSelect) {
            themeSelect.value = savedTheme;
            themeSelect.addEventListener("change", (e) => {
                this.setTheme(e.target.value);
            });
        }

        // Aplicar el tema inicial
        this.setTheme(savedTheme);

        // Escuchar cambios del sistema en tiempo real si está en modo automático
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (Storage.getPreference(this.KEY) === 'auto' || !Storage.getPreference(this.KEY)) {
                this.applySystemTheme();
            }
        });
    },

    setTheme(theme) {
        Storage.setPreference(this.KEY, theme);
        
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.classList.add('dark-mode');
            document.documentElement.classList.remove('light-mode');
        } else if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.add('light-mode');
            document.documentElement.classList.remove('dark-mode');
        } else {
            // Automático (Auto)
            document.documentElement.removeAttribute('data-theme');
            this.applySystemTheme();
        }
    },

    applySystemTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.classList.add('dark-mode');
            document.documentElement.classList.remove('light-mode');
        } else {
            document.documentElement.classList.add('light-mode');
            document.documentElement.classList.remove('dark-mode');
        }
    }
};

// Auto-iniciar al cargar el script
document.addEventListener("DOMContentLoaded", () => Theme.init());
