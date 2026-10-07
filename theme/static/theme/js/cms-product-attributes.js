(function () {
    "use strict";

    var root = document.querySelector("[data-product-attributes]");
    if (!root) {
        return;
    }

    var prefix = "attributes";
    var catalogEl = document.getElementById("attribute-catalog");
    var cardsRoot = root.querySelector("[data-attr-cards]");
    var formsetRoot = root.querySelector("[data-attribute-formset-root]");
    var totalInput = root.querySelector('input[name="attributes-TOTAL_FORMS"]');
    var cardTemplate = root.querySelector("[data-attr-card-template]");
    var formRowTemplate = root.querySelector("[data-attr-form-row-template]");
    var addCardButton = root.querySelector("[data-attr-add-card]");

    var catalog = {};
    if (catalogEl) {
        try {
            catalog = JSON.parse(catalogEl.textContent || "{}");
        } catch (error) {
            catalog = {};
        }
    }

    function formRow(index) {
        return formsetRoot.querySelector('[data-form-index="' + index + '"]');
    }

    function rowField(row, name) {
        if (!row) {
            return null;
        }
        return row.querySelector('[name$="-' + name + '"]');
    }

    function cardAttributeId(card) {
        var select = card.querySelector("[data-attr-select]");
        if (select && select.value) {
            return select.value;
        }
        return null;
    }

    function getCsrfToken() {
        var input = document.querySelector("[name=csrfmiddlewaretoken]");
        return input ? input.value : "";
    }

    function attributeEntry(card) {
        var attributeId = cardAttributeId(card);
        return attributeId ? catalog[String(attributeId)] : null;
    }

    function isLoadAttribute(card) {
        var entry = attributeEntry(card);
        if (!entry) {
            return false;
        }
        var slug = (entry.slug || "").toLowerCase();
        var name = (entry.name || "").toLowerCase();
        return slug.indexOf("nosn") !== -1 || name.indexOf("nośno") !== -1 || name.indexOf("nosno") !== -1;
    }

    function sortOptionValues(options) {
        return options.slice().sort(function (a, b) {
            var re = /(\d+)/;
            var am = re.exec(a.value || "");
            var bm = re.exec(b.value || "");
            if (am && bm) {
                var diff = parseInt(am[1], 10) - parseInt(bm[1], 10);
                if (diff !== 0) {
                    return diff;
                }
            }
            return (a.value || "").localeCompare(b.value || "", "pl", { numeric: true });
        });
    }

    function syncLoadCapacityUi(card) {
        var iconSelect = card.querySelector("[data-attr-value-icon]");
        var valueNewInput = card.querySelector("[data-attr-value-new]");
        if (!iconSelect) {
            return;
        }
        var load = isLoadAttribute(card);
        iconSelect.hidden = !load;
        if (valueNewInput && load) {
            valueNewInput.placeholder = "Opcjonalny opis (może być pusty przy samej ikonie)";
        } else if (valueNewInput) {
            valueNewInput.placeholder = "Nowa wartość, np. Opal";
        }
    }

    function cardAttributeLabel(card) {
        var select = card.querySelector("[data-attr-select]");
        if (select && select.selectedIndex > 0) {
            return select.options[select.selectedIndex].text;
        }
        var newInput = card.querySelector("[data-attr-new]");
        return newInput && newInput.value.trim() ? newInput.value.trim() : "Nowy atrybut";
    }

    function plainTextFromHtml(html) {
        var wrapper = document.createElement("div");
        wrapper.innerHTML = html || "";
        return wrapper.textContent.replace(/\s+/g, " ").trim();
    }

    function readValueEditor(card) {
        var editor = card.querySelector("[data-attr-value-new]");
        if (!editor) {
            return "";
        }
        return (editor.innerHTML || "").trim();
    }

    function clearValueEditor(card) {
        var editor = card.querySelector("[data-attr-value-new]");
        if (editor) {
            editor.innerHTML = "";
        }
    }

    function chipValues(card) {
        var values = [];
        card.querySelectorAll("[data-attr-chip]").forEach(function (chip) {
            var label = chip.querySelector(".cms-attr-chip__label");
            if (label) {
                values.push(plainTextFromHtml(label.innerHTML).toLowerCase());
            }
        });
        return values;
    }

    function syncEmptyMessage() {
        var emptyMsg = cardsRoot.querySelector("[data-attr-empty-msg]");
        var hasCards = cardsRoot.querySelector("[data-attr-card]");
        if (emptyMsg) {
            emptyMsg.hidden = !!hasCards;
        }
    }

    function populateValueSelect(card) {
        var select = card.querySelector("[data-attr-value-select]");
        if (!select) {
            return;
        }

        var attributeId = cardAttributeId(card);
        var used = chipValues(card);
        var current = select.value;

        select.innerHTML = "";
        var placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "— wybierz istniejącą wartość —";
        select.appendChild(placeholder);

        var entry = catalog[String(attributeId)];
        if (entry) {
            sortOptionValues(entry.options).forEach(function (option) {
                if (used.indexOf(plainTextFromHtml(option.value).toLowerCase()) !== -1) {
                    return;
                }
                var el = document.createElement("option");
                el.value = String(option.id);
                el.textContent = option.value;
                select.appendChild(el);
            });
        }

        if (current && select.querySelector('option[value="' + current + '"]')) {
            select.value = current;
        }

        var catalogDelete = card.querySelector("[data-attr-catalog-delete]");
        if (catalogDelete) {
            catalogDelete.hidden = !attributeId;
            catalogDelete.disabled = !select.value;
        }
        syncLoadCapacityUi(card);
    }

    function syncCardToRows(card) {
        var attributeSelect = card.querySelector("[data-attr-select]");
        var newAttrInput = card.querySelector("[data-attr-new]");
        var filterCheckbox = card.querySelector("[data-attr-filter]");
        var attributeId = attributeSelect ? attributeSelect.value : "";
        var newName = newAttrInput ? newAttrInput.value.trim() : "";
        var showInFilters = filterCheckbox ? filterCheckbox.checked : false;

        card.querySelectorAll("[data-attr-chip]").forEach(function (chip) {
            var index = chip.getAttribute("data-form-index");
            var row = formRow(index);
            if (!row || row.hidden) {
                return;
            }

            var attrField = rowField(row, "attribute");
            var newAttrField = rowField(row, "new_attribute_name");
            var filterField = rowField(row, "show_in_filters");

            if (attributeId) {
                if (attrField) {
                    attrField.value = attributeId;
                }
                if (newAttrField) {
                    newAttrField.value = "";
                }
            } else if (newName) {
                if (attrField) {
                    attrField.value = "";
                }
                if (newAttrField) {
                    newAttrField.value = newName;
                }
            }

            if (filterField) {
                filterField.checked = showInFilters;
            }
        });
    }

    function reindexFormset() {
        var rows = Array.prototype.slice.call(
            formsetRoot.querySelectorAll("[data-attribute-form-row]")
        );
        var chipIndexMap = {};

        rows.forEach(function (row, newIndex) {
            var oldIndex = row.getAttribute("data-form-index");
            chipIndexMap[oldIndex] = String(newIndex);
            row.setAttribute("data-form-index", String(newIndex));

            row.querySelectorAll("input, select, textarea").forEach(function (node) {
                if (node.name) {
                    node.name = node.name.replace(
                        new RegExp("^" + prefix + "-\\d+-"),
                        prefix + "-" + newIndex + "-"
                    );
                }
                if (node.id) {
                    node.id = node.id.replace(
                        new RegExp("^id_" + prefix + "-\\d+-"),
                        "id_" + prefix + "-" + newIndex + "-"
                    );
                }
            });

            var sortField = rowField(row, "sort_order");
            if (sortField) {
                sortField.value = String(newIndex);
            }
        });

        cardsRoot.querySelectorAll("[data-attr-chip]").forEach(function (chip) {
            var oldIndex = chip.getAttribute("data-form-index");
            if (chipIndexMap[oldIndex] !== undefined) {
                chip.setAttribute("data-form-index", chipIndexMap[oldIndex]);
            }
        });

        if (totalInput) {
            totalInput.value = String(rows.length);
        }
    }

    function nextFormIndex() {
        return formsetRoot.querySelectorAll("[data-attribute-form-row]").length;
    }

    function appendFormRow() {
        if (!formRowTemplate) {
            return null;
        }

        var index = nextFormIndex();
        var wrapper = document.createElement("div");
        wrapper.innerHTML = formRowTemplate.innerHTML.replace(/__prefix__/g, String(index));
        var row = wrapper.firstElementChild;
        row.setAttribute("data-form-index", String(index));
        formsetRoot.appendChild(row);

        if (totalInput) {
            totalInput.value = String(index + 1);
        }

        return row;
    }

    function addValueChip(card, label, optionId, newValue, iconDisplay) {
        var valuesWrap = card.querySelector("[data-attr-values]");
        if (!valuesWrap) {
            return;
        }

        var normalized = label.trim().toLowerCase();
        var exists = chipValues(card).indexOf(normalized) !== -1;
        if (exists) {
            return;
        }

        var row = appendFormRow();
        if (!row) {
            return;
        }

        syncCardToRows(card);

        var optionField = rowField(row, "option");
        var newValueField = rowField(row, "new_option_value");
        if (optionId && optionField) {
            optionField.value = String(optionId);
        } else if (newValue && newValueField) {
            newValueField.value = newValue;
        }
        var iconField = rowField(row, "new_option_icon_display");
        if (iconField && iconDisplay) {
            iconField.value = iconDisplay;
        }

        syncCardToRows(card);

        var index = row.getAttribute("data-form-index");
        var chip = document.createElement("span");
        chip.className = "cms-attr-chip";
        chip.setAttribute("data-attr-chip", "");
        chip.setAttribute("data-form-index", index);
        chip.innerHTML =
            '<span class="cms-attr-chip__label"></span>' +
            '<button type="button" class="cms-attr-chip__remove" data-attr-chip-remove aria-label="Usuń wartość">&times;</button>';
        var labelEl = chip.querySelector(".cms-attr-chip__label");
        if (label.indexOf("<") !== -1) {
            labelEl.innerHTML = label.trim();
        } else {
            labelEl.textContent = label.trim();
        }
        valuesWrap.appendChild(chip);
        bindChip(chip, card);
        populateValueSelect(card);
        syncEmptyMessage();
    }

    function removeChip(chip, card) {
        var index = chip.getAttribute("data-form-index");
        var row = formRow(index);
        if (row) {
            var deleteField = rowField(row, "DELETE");
            if (deleteField) {
                deleteField.checked = true;
                row.hidden = true;
            } else {
                row.remove();
                reindexFormset();
            }
        }
        chip.remove();
        populateValueSelect(card);
        syncEmptyMessage();
    }

    function bindChip(chip, card) {
        var removeButton = chip.querySelector("[data-attr-chip-remove]");
        if (removeButton) {
            removeButton.addEventListener("click", function () {
                removeChip(chip, card);
            });
        }
    }

    function bindCard(card) {
        var attrSelect = card.querySelector("[data-attr-select]");
        var newAttrInput = card.querySelector("[data-attr-new]");
        var filterCheckbox = card.querySelector("[data-attr-filter]");
        var valueSelect = card.querySelector("[data-attr-value-select]");
        var valueNewInput = card.querySelector("[data-attr-value-new]");
        var valueIconSelect = card.querySelector("[data-attr-value-icon]");
        var addValueButton = card.querySelector("[data-attr-value-add]");
        var catalogDeleteButton = card.querySelector("[data-attr-catalog-delete]");
        var removeCardButton = card.querySelector("[data-attr-remove-card]");

        function syncAttributeInputs() {
            var hasAttribute = attrSelect && attrSelect.value;
            if (newAttrInput) {
                newAttrInput.hidden = !!hasAttribute;
                if (hasAttribute) {
                    newAttrInput.value = "";
                }
            }
            populateValueSelect(card);
            syncCardToRows(card);
        }

        if (valueSelect) {
            valueSelect.addEventListener("change", function () {
                populateValueSelect(card);
            });
        }

        if (catalogDeleteButton) {
            catalogDeleteButton.addEventListener("click", function () {
                if (!valueSelect || !valueSelect.value) {
                    return;
                }
                var optionId = valueSelect.value;
                if (
                    !window.confirm(
                        "Usunąć tę wartość z katalogu atrybutów? Zniknie też na wszystkich produktach."
                    )
                ) {
                    return;
                }
                fetch("/ifil-log/panel/atrybuty/opcja/" + optionId + "/usun/", {
                    method: "POST",
                    headers: { "X-CSRFToken": getCsrfToken() },
                    credentials: "same-origin",
                })
                    .then(function (response) {
                        if (!response.ok) {
                            throw new Error("delete failed");
                        }
                        var attributeId = cardAttributeId(card);
                        if (attributeId && catalog[String(attributeId)]) {
                            catalog[String(attributeId)].options = catalog[String(attributeId)].options.filter(
                                function (opt) {
                                    return String(opt.id) !== String(optionId);
                                }
                            );
                        }
                        valueSelect.value = "";
                        populateValueSelect(card);
                        window.alert("Wartość usunięta z katalogu. Zapisz produkt, jeśli edytujesz przypisania.");
                    })
                    .catch(function () {
                        window.alert("Nie udało się usunąć wartości. Odśwież stronę i spróbuj ponownie.");
                    });
            });
        }

        if (attrSelect) {
            attrSelect.addEventListener("change", syncAttributeInputs);
        }

        if (newAttrInput) {
            newAttrInput.addEventListener("input", function () {
                if (attrSelect) {
                    attrSelect.value = "";
                }
                syncAttributeInputs();
            });
        }

        if (filterCheckbox) {
            filterCheckbox.addEventListener("change", function () {
                syncCardToRows(card);
            });
        }

        if (addValueButton) {
            addValueButton.addEventListener("click", function () {
                var attributeId = cardAttributeId(card);
                var newName = newAttrInput ? newAttrInput.value.trim() : "";
                if (!attributeId && !newName) {
                    window.alert("Najpierw wybierz atrybut lub wpisz nazwę nowego.");
                    return;
                }

                var optionId = valueSelect ? valueSelect.value : "";
                var newValueHtml = readValueEditor(card);
                var newValuePlain = plainTextFromHtml(newValueHtml);
                var iconDisplay =
                    valueIconSelect && !valueIconSelect.hidden ? valueIconSelect.value : "";

                if (optionId) {
                    var label = valueSelect.options[valueSelect.selectedIndex].text;
                    addValueChip(card, label, optionId, "", "");
                } else if (newValuePlain || iconDisplay) {
                    var chipLabel = newValueHtml || newValuePlain;
                    if (!chipLabel && iconDisplay && valueIconSelect) {
                        chipLabel = valueIconSelect.options[valueIconSelect.selectedIndex].text;
                    }
                    addValueChip(
                        card,
                        chipLabel || "—",
                        "",
                        newValueHtml || chipLabel,
                        iconDisplay
                    );
                } else {
                    window.alert("Wybierz wartość z listy albo wpisz nową.");
                    return;
                }

                if (valueSelect) {
                    valueSelect.value = "";
                }
                clearValueEditor(card);
                if (valueIconSelect) {
                    valueIconSelect.value = "";
                }
            });
        }

        card.querySelectorAll("[data-attr-cmd]").forEach(function (button) {
            button.addEventListener("click", function () {
                var editor = card.querySelector("[data-attr-value-new]");
                if (!editor) {
                    return;
                }
                editor.focus();
                var command = button.getAttribute("data-attr-cmd");
                if (command === "superscript") {
                    document.execCommand("superscript", false, null);
                } else if (command) {
                    document.execCommand(command, false, null);
                }
            });
        });

        if (valueNewInput) {
            valueNewInput.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    addValueButton.click();
                }
            });
        }

        if (removeCardButton) {
            removeCardButton.addEventListener("click", function () {
                card.querySelectorAll("[data-attr-chip]").forEach(function (chip) {
                    removeChip(chip, card);
                });
                card.remove();
                syncEmptyMessage();
            });
        }

        card.querySelectorAll("[data-attr-chip]").forEach(function (chip) {
            bindChip(chip, card);
        });

        syncAttributeInputs();
    }

    function addCard() {
        if (!cardTemplate) {
            return;
        }

        var key = "new:" + Date.now();
        var wrapper = document.createElement("div");
        wrapper.innerHTML = cardTemplate.innerHTML.replace(/__key__/g, key);
        var card = wrapper.firstElementChild;
        cardsRoot.appendChild(card);
        bindCard(card);
        syncEmptyMessage();

        var select = card.querySelector("[data-attr-select]");
        if (select) {
            select.focus();
        }
    }

    cardsRoot.querySelectorAll("[data-attr-card]").forEach(bindCard);

    if (addCardButton) {
        addCardButton.addEventListener("click", addCard);
    }

    var productForm = document.getElementById("product-form");
    if (productForm) {
        productForm.addEventListener(
            "submit",
            function () {
                cardsRoot.querySelectorAll("[data-attr-card]").forEach(syncCardToRows);
                reindexFormset();
                formsetRoot.querySelectorAll("select:disabled, input:disabled, textarea:disabled").forEach(function (el) {
                    el.disabled = false;
                });
            },
            true
        );
    }

    syncEmptyMessage();
})();
