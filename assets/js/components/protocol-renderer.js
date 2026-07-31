const ProtocolRenderer = {
    renderQuickReference(protocol, helpers) {
        if (!protocol || typeof protocol !== "object" || Array.isArray(protocol)) {
            throw new TypeError("protocol debe ser un objeto");
        }
        if (!protocol.components || !Array.isArray(protocol.components)) {
            throw new TypeError("protocol.components debe ser un array");
        }
        if (!helpers || typeof helpers !== "object" || Array.isArray(helpers)) {
            throw new TypeError("helpers debe ser un objeto");
        }
        const { escapeHTML, localize, translate } = helpers;
        if (typeof escapeHTML !== "function") {
            throw new TypeError("escapeHTML debe ser una función");
        }
        if (typeof localize !== "function") {
            throw new TypeError("localize debe ser una función");
        }
        if (typeof translate !== "function") {
            throw new TypeError("translate debe ser una función");
        }

        const titleText = translate("label.protocol_quick_title");
        const descText = translate("label.protocol_quick_description");
        const sequenceTitle = translate("label.protocol_quick_sequence");
        const expandHint = translate("label.protocol_quick_expand_hint");
        const noLinkedItems = translate("label.no_linked_items");
        const assessLabel = translate("label.protocol_quick_assess");
        const alertsLabel = translate("label.protocol_quick_alerts");

        let html = `
        <article class="protocol-quick-card" aria-labelledby="protocol-quick-title-id">
            <header class="protocol-quick-header">
                <h3 id="protocol-quick-title-id">${escapeHTML(titleText)}</h3>
                <p class="protocol-quick-description">${escapeHTML(descText)}</p>
            </header>
        `;

        const compNames = protocol.components.map(comp => localize({ es: comp.name_es, en: comp.name_en }));

        html += `
            <section class="protocol-quick-sequence" aria-labelledby="protocol-quick-seq-title">
                <h4 id="protocol-quick-seq-title">${escapeHTML(sequenceTitle)}</h4>
                <ol>
                    ${compNames.map(name => `
                        <li class="protocol-quick-sequence-item">
                            <span>${escapeHTML(name)}</span>
                        </li>
                    `).join("")}
                </ol>
            </section>
        `;

        html += `
            <section class="protocol-quick-components" aria-label="${escapeHTML(translate("label.components"))}">
        `;

        protocol.components.forEach(comp => {
            const localizedCompName = localize({ es: comp.name_es, en: comp.name_en });

            let assessText = noLinkedItems;
            let alertsText = noLinkedItems;

            if (comp.quick_reference) {
                if (comp.quick_reference.assess) {
                    assessText = localize(comp.quick_reference.assess);
                }
                if (comp.quick_reference.alerts) {
                    alertsText = localize(comp.quick_reference.alerts);
                }
            }

            html += `
                <section class="protocol-quick-component">
                    <h4>${escapeHTML(localizedCompName)}</h4>
                    <div class="protocol-quick-section protocol-quick-assess">
                        <strong>${escapeHTML(assessLabel)}</strong>
                        <p>${escapeHTML(assessText)}</p>
                    </div>
                    <div class="protocol-quick-section protocol-quick-alerts">
                        <strong>${escapeHTML(alertsLabel)}</strong>
                        <p>${escapeHTML(alertsText)}</p>
                    </div>
                </section>
            `;
        });

        html += `
            </section>
            <footer class="protocol-quick-expand-hint">
                ${escapeHTML(expandHint)}
            </footer>
        </article>
        `;

        return html;
    }
};
