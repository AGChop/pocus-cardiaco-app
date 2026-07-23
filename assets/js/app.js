// Archivo lógico principal de la aplicación POCUS Cardíaco
document.addEventListener("DOMContentLoaded", async () => {
    // Inicializar I18n
    if (typeof I18n !== "undefined") {
        await I18n.init();
    }

    // Conectar el selector de idioma
    const languageSelect = document.getElementById("language-select");
    if (languageSelect && typeof I18n !== "undefined") {
        languageSelect.value = I18n.getLanguage();
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

    function escapeHTML(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

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
            appContent.innerHTML = `<div class="loading">${escapeHTML(I18n.translate("search.loading"))}</div>`;

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

        // Escuchar cambio global de idioma para volver a renderizar búsqueda activa
        window.addEventListener("pocus-language-changed", async () => {
            const query = searchInput.value;
            if (query && query.trim() !== "") {
                const results = await Search.searchGlobal(query);
                renderSearchResults(results, query);
            }
        });
    }

    // Función para renderizar los resultados de la búsqueda
    function renderSearchResults(results, query) {
        const escapedQuery = escapeHTML(query);
        if (results.length === 0) {
            appContent.innerHTML = `
                <div class="card error-card">
                    <h3>${escapeHTML(I18n.translate("search.no_results_title"))}</h3>
                    <p>${I18n.translate("search.no_results_message", { query: `<strong>${escapedQuery}</strong>` })}</p>
                    <button id="search-reset-btn" class="btn-primary">${escapeHTML(I18n.translate("search.clear"))}</button>
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
                ${I18n.translate("search.results_count", { count: results.length, query: escapedQuery })}
            </div>
            <div class="search-results-list">
        `;

        results.forEach(({ type, item }) => {
            let title = "";
            let description = "";
            let link = "";
            let badgeClass = `badge-${type.replace("ó", "o")}`;
            let translatedType = "";

            if (type === "medición") {
                title = I18n.localize(item.measurement);
                description = `<strong>${escapeHTML(I18n.translate("label.formula_or_method"))}:</strong> ${escapeHTML(I18n.localize(item.formula_or_method))}<br><strong>${escapeHTML(I18n.translate("label.normal_values"))}:</strong> ${escapeHTML(I18n.localize(item.normal_values))}`;
                link = `#/medicion/${item.id}`;
                translatedType = I18n.translate("label.measurement");
            } else if (type === "término") {
                title = I18n.localize(item.term);
                description = escapeHTML(I18n.localize(item.definition));
                link = `#/glosario/${item.id}`;
                translatedType = I18n.translate("label.term");
            } else if (type === "abreviatura") {
                title = I18n.localize(item.abbreviation);
                description = escapeHTML(I18n.localize(item.meaning));
                link = `#/abreviaturas`;
                translatedType = I18n.translate("label.abbreviation");
            } else if (type === "clasificación") {
                title = I18n.localize(item.name);
                description = item.note ? escapeHTML(I18n.localize(item.note)) : escapeHTML(I18n.translate("label.classification"));
                link = `#/clasificaciones`;
                translatedType = I18n.translate("label.classification");
            } else if (type === "ventana") {
                title = I18n.localize(item.window);
                description = `<strong>${escapeHTML(I18n.translate("label.abbreviation"))}:</strong> ${escapeHTML(I18n.localize(item.abbreviation))}<br><strong>${escapeHTML(I18n.translate("label.targets"))}:</strong> ${escapeHTML(I18n.localize(item.favored_structures))}`;
                link = `#/ventanas/${item.id}`;
                translatedType = I18n.translate("label.window");
            } else if (type === "protocolo") {
                title = I18n.localize({ es: item.name_es, en: item.name_en || item.name_es });
                description = `<strong>${escapeHTML(I18n.translate("label.acronym"))}:</strong> ${escapeHTML(I18n.localize(item.acronym))}<br><strong>${escapeHTML(I18n.translate("label.purpose"))}:</strong> ${escapeHTML(I18n.localize(item.purpose))}`;
                link = `#/protocolos/${item.id}`;
                translatedType = I18n.translate("label.protocol");
            }

            html += `
                <a href="${link}" class="search-result-card" style="text-decoration: none; color: inherit;">
                    <div class="search-result-header">
                        <span class="search-result-title">${escapeHTML(title)}</span>
                        <span class="result-badge ${badgeClass}">${escapeHTML(translatedType)}</span>
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
