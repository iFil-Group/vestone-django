(function () {
    "use strict";

    var root = document.querySelector("[data-product-attributes]");
    if (!root) {
        return;
    }

    var catalogEl = root.querySelector("[data-attribute-catalog]");
    var rowsRoot = root.querySelector("[data-attribute-rows]");
    var addButton = root.querySelector("[data-attribute-add]");
    var emptyTemplate = root.querySelector("[data-attribute-empty-template]");
    var totalInput = root.querySelector('input[name="attributes-TOTAL_FORMS"]');
    var prefix = "attributes";

    var catalog = {};
    if (catalogEl) {
        try {
            catalog = JSON.parse(catalogEl.textContent || "{}");
        } catch (error) {
            catalog = {};
        }
    }

    function optionElements(attributeId, selectedId) {
        var fragment = document.createDocumentFragment();
        var placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "— wybierz wartość —";
        fragment.appendChild(placeholder);

        var entry = catalog[String(attributeId)];
        if (!entry) {
            return fragment;
        }

        entry.options.forEach(function (option) {
            var el = document.createElement("option");
            el.value = String(option.id);
            el.textContent = option.value;
            if (selectedId && String(selectedId) === String(option.id)) {
                el.selected = true;
            }
            fragment.appendChild(el);
        });
        return fragment;
    }

    function field(row, namePart) {
        return row.querySelector('[name^="' + prefix + '-"][name$="-' + namePart + '"]');
    }

    function syncOptionSelect(row) {
        var attributeSelect = field(row, "attribute");
        var optionSelect = field(row, "option");
        if (!attributeSelect || !optionSelect) {
            return;
        }

        var selected = optionSelect.value;
        optionSelect.innerHTML = "";
        optionSelect.appendChild(optionElements(attributeSelect.value, selected));
    }

    function syncShowInFilters(row) {
        var attributeSelect = field(row, "attribute");
        var checkbox = field(row, "show_in_filters");
        if (!attributeSelect || !checkbox || !attributeSelect.value) {
            return;
        }
        var entry = catalog[String(attributeSelect.value)];
        if (entry) {
            checkbox.checked = !!entry.show_in_filters;
        }
    }

    function toggleField(row, selector, visible) {
        var wrap = row.querySelector(selector);
        if (!wrap) {
            return;
        }
        wrap.hidden = !visible;
        var input = wrap.querySelector("input, select, textarea");
        if (input) {
            input.disabled = !visible;
        }
    }

    function syncNewAttributeMode(row, forceNew) {
        var attributeSelect = field(row, "attribute");
        var isNew = forceNew || (attributeSelect && !attributeSelect.value);
        toggleField(row, "[data-new-attribute-field]", isNew);
        if (attributeSelect) {
            attributeSelect.disabled = !!forceNew;
        }
    }

    function syncNewValueMode(row, forceNew) {
        var optionSelect = field(row, "option");
        var isNew = forceNew || (optionSelect && !optionSelect.value);
        toggleField(row, "[data-new-value-field]", isNew);
        if (optionSelect) {
            optionSelect.disabled = !!forceNew;
        }
    }

    function bindRow(row) {
        var attributeSelect = field(row, "attribute");
        var optionSelect = field(row, "option");
        var toggleNewAttribute = row.querySelector("[data-attribute-toggle-new-atrybut]");
        var toggleNewValue = row.querySelector("[data-attribute-toggle-new-value]");

        if (attributeSelect) {
            attributeSelect.addEventListener("change", function () {
                syncOptionSelect(row);
                syncShowInFilters(row);
                syncNewAttributeMode(row, false);
                syncNewValueMode(row, false);
            });
        }

        if (optionSelect) {
            optionSelect.addEventListener("change", function () {
                syncNewValueMode(row, false);
            });
        }

        if (toggleNewAttribute) {
            toggleNewAttribute.addEventListener("click", function () {
                if (attributeSelect) {
                    attributeSelect.value = "";
                    attributeSelect.disabled = true;
                }
                syncOptionSelect(row);
                syncNewAttributeMode(row, true);
            });
        }

        if (toggleNewValue) {
            toggleNewValue.addEventListener("click", function () {
                if (optionSelect) {
                    optionSelect.value = "";
                    optionSelect.disabled = true;
                }
                syncNewValueMode(row, true);
            });
        }

        syncOptionSelect(row);
        syncShowInFilters(row);
        syncNewAttributeMode(row, false);
        syncNewValueMode(row, false);
    }

    function nextIndex() {
        return rowsRoot ? rowsRoot.querySelectorAll("[data-attribute-row]").length : 0;
    }

    function addRow() {
        if (!emptyTemplate || !rowsRoot || !totalInput) {
            return;
        }

        var index = nextIndex();
        var html = emptyTemplate.innerHTML
            .replace(/__prefix__/g, String(index))
            .replace(/attributes-__prefix__/g, prefix + "-" + index);

        var wrapper = document.createElement("div");
        wrapper.innerHTML = html.trim();
        var row = wrapper.firstElementChild;
        rowsRoot.appendChild(row);
        totalInput.value = String(index + 1);
        bindRow(row);

        if (window.cmsBindFormsetRow) {
            window.cmsBindFormsetRow(row);
        }
    }

    rowsRoot.querySelectorAll("[data-attribute-row]").forEach(bindRow);

    if (addButton) {
        addButton.addEventListener("click", addRow);
    }
})();
