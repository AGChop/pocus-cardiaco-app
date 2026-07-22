// Archivo lógico principal de la aplicación POCUS Cardíaco
document.addEventListener("DOMContentLoaded", async () => {
    // Inicializar I18n
    if (typeof I18n !== "undefined") {
        await I18n.init();
    }

    // Conectar el selector de idioma
    const languageSelect = document.getElementById("language-select");
    if (languageSelect && typeof I18n !== "undefined") {
        languageSelect.addEventListener("change", (e) => {
            I18n.setLanguage(e.target.value);
        });
    }

    console.log("Aplicación POCUS Cardíaco inicializada correctamente.");
    
    // Iniciar la ruta actual al cargar la aplicación
    if (typeof Router !== "undefined") {
        Router.route();
    } else {
        console.error("Error: El enrutador (Router) no está definido.");
    }

    // Configurar la barra de búsqueda global
    const searchInput = document.getElementById("global-search");
    const clearBtn = document.getElementById("clear-search");
    const appContent = document.getElementById("app-content");

    if (searchInput && clearBtn && appContent) {
        // Escuchar la escritura en el buscador
        searchInput.addEventListener("input", async (e) => {
            const query = e.target.value;
            
            if (query.trim() === "") {
                clearBtn.style.display = "none";
                Router.route(); // Volver al estado de la ruta activa
                return;
            }

            clearBtn.style.display = "block";
            appContent.innerHTML = `<div class="loading">Buscando en la base de datos médica...</div>`;

            // Ejecutar la búsqueda inteligente
            const results = await Search.searchGlobal(query);
            renderSearchResults(results, query);
        });

        // Escuchar el clic para limpiar la búsqueda
        clearBtn.addEventListener("click", () => {
            searchInput.value = "";
            clearBtn.style.display = "none";
            Router.route(); // Restaurar vista original
        });
    }

    // Función para renderizar los resultados de la búsqueda
    function renderSearchResults(results, query) {
        if (results.length === 0) {
            appContent.innerHTML = `
                <div class="card error-card">
                    <h3>No se encontraron resultados</h3>
                    <p>No se encontraron términos ni mediciones relacionados con "<strong>${query}</strong>".</p>
                    <button id="search-reset-btn" class="btn-primary">Limpiar búsqueda</button>
                </div>
            `;
            
            document.getElementById("search-reset-btn")?.addEventListener("click", () => {
                searchInput.value = "";
                clearBtn.style.display = "none";
                Router.route();
            });
            return;
        }

        let html = `
            <div class="search-summary" style="margin-bottom: 1rem; font-weight: 600;">
                Se encontraron ${results.length} resultados para "${query}":
            </div>
            <div class="search-results-list">
        `;

        results.forEach(({ type, item }) => {
            let title = "";
            let description = "";
            let link = "";
            let badgeClass = `badge-${type.replace("ó", "o")}`;

            if (type === "medición") {
                title = item.measurement;
                description = `<strong>Fórmula/Método:</strong> ${item.formula_or_method}<br><strong>Valores normales:</strong> ${item.normal_values}`;
                link = `#/medicion/${item.id}`;
            } else if (type === "término") {
                title = item.term;
                description = item.definition;
                link = `#/glosario/${item.id}`;
            } else if (type === "abreviatura") {
                title = item.abbreviation;
                description = item.meaning;
                link = `#/abreviaturas`;
            } else if (type === "clasificación") {
                title = item.name;
                description = item.note || "Clasificación práctica de referencia.";
                link = `#/clasificaciones`;
            } else if (type === "ventana") {
                title = item.window;
                description = `<strong>Abreviatura:</strong> ${item.abbreviation}<br><strong>Estructuras favorecidas:</strong> ${item.favored_structures}`;
                link = `#/ventanas/${item.id}`;
            } else if (type === "protocolo") {
                title = item.name_es;
                description = `<strong>Acrónimo:</strong> ${item.acronym}<br><strong>Propósito:</strong> ${item.purpose}`;
                link = `#/protocolos/${item.id}`;
            }

            html += `
                <a href="${link}" class="search-result-card" style="text-decoration: none; color: inherit;">
                    <div class="search-result-header">
                        <span class="search-result-title">${title}</span>
                        <span class="result-badge ${badgeClass}">${type}</span>
                    </div>
                    <p style="font-size: 0.9rem; margin-top: 0.25rem;">${description}</p>
                </a>
            `;
        });

        html += `</div>`;
        appContent.innerHTML = html;
    }
});

// Registro del Service Worker para capacidades Offline de la PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
            .then((registration) => {
                console.log('PWA: Service Worker registrado con éxito en el ámbito:', registration.scope);
            })
            .catch((error) => {
                console.error('PWA: Error al registrar el Service Worker:', error);
            });
    });
}

