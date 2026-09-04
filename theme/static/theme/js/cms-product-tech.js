(function () {
    "use strict";

    var root = document.querySelector("[data-tech-editor]");
    if (!root) return;

    var packsWrap = root.querySelector("[data-tech-packs]");
    var jsonInput = root.querySelector("[data-tech-packs-json]");
    var packTemplate = root.querySelector("[data-tech-pack-template]");
    var rowTemplate = root.querySelector("[data-tech-row-template]");
    var addPackBtn = root.querySelector("[data-tech-add-pack]");
    var copySearch = root.querySelector("[data-tech-copy-search]");
    var copyResults = root.querySelector("[data-tech-copy-results]");
    var sourcesWrap = root.querySelector("[data-tech-sources]");
    var sourceList = root.querySelector("[data-tech-source-list]");
    var searchUrl = root.getAttribute("data-tech-search-url") || "";
    var copyUrlTemplate = root.getAttribute("data-tech-copy-url-template") || "";
    var productId = root.getAttribute("data-product-id") || "";
    var searchTimer = null;

    function readInitial() {
        var node = document.getElementById("tech-packs-data");
        if (!node) return [];
        try {
            var data = JSON.parse(node.textContent || "[]");
            return Array.isArray(data) ? data : [];
        } catch (err) {
            return [];
        }
    }

    function wrapSelection(input, tag) {
        if (!input) return;
        var start = input.selectionStart;
        var end = input.selectionEnd;
        var value = input.value || "";
        var selected = value.slice(start, end) || (tag === "sup" ? "2" : "");
        if (!selected && tag !== "sup") return;
        input.value = value.slice(0, start) + "<" + tag + ">" + selected + "</" + tag + ">" + value.slice(end);
        input.focus();
        var cursor = start + tag.length + 2 + selected.length + tag.length + 3;
        input.setSelectionRange(cursor, cursor);
        syncJson();
    }

    function createRow(data) {
        data = data || {};
        var fragment = rowTemplate.content.cloneNode(true);
        var row = fragment.querySelector("[data-tech-row]");
        var label = row.querySelector("[data-tech-row-label]");
        var value = row.querySelector("[data-tech-row-value]");
        var icon = row.querySelector("[data-tech-row-icon]");
        var remove = row.querySelector("[data-tech-row-remove]");
        if (label) label.value = data.label || "";
        if (value) value.value = data.value || "";
        if (icon) icon.value = data.icon || "";
        if (remove) {
            remove.addEventListener("click", function (event) {
                event.preventDefault();
                row.remove();
                syncJson();
            });
        }
        row.querySelectorAll("[data-tech-wrap]").forEach(function (button) {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                wrapSelection(value, button.getAttribute("data-tech-wrap"));
            });
        });
        [label, value, icon].forEach(function (input) {
            if (input) input.addEventListener("input", syncJson);
            if (input) input.addEventListener("change", syncJson);
        });
        return row;
    }

    function createPack(data) {
        data = data || {};
        var fragment = packTemplate.content.cloneNode(true);
        var pack = fragment.querySelector("[data-tech-pack]");
        var nameInput = pack.querySelector("[data-tech-pack-name]");
        var rowsWrap = pack.querySelector("[data-tech-rows]");
        var addRowBtn = pack.querySelector("[data-tech-add-row]");
        var copyBtn = pack.querySelector("[data-tech-pack-copy]");
        var removeBtn = pack.querySelector("[data-tech-pack-remove]");

        if (data.sourceId) pack.dataset.sourceId = String(data.sourceId);
        if (data.sourceName) pack.dataset.sourceName = data.sourceName;

        if (nameInput) {
            nameInput.value = data.name || "";
            nameInput.addEventListener("input", syncJson);
        }

        (data.rows || [{ label: "", value: "", icon: "" }]).forEach(function (rowData) {
            rowsWrap.appendChild(createRow(rowData));
        });

        if (addRowBtn) {
            addRowBtn.addEventListener("click", function () {
                rowsWrap.appendChild(createRow({ label: "", value: "", icon: "" }));
                syncJson();
            });
        }
        if (copyBtn) {
            copyBtn.addEventListener("click", function () {
                packsWrap.appendChild(createPack(serializePack(pack)));
                syncJson();
            });
        }
        if (removeBtn) {
            removeBtn.addEventListener("click", function () {
                pack.remove();
                renderSources();
                syncJson();
            });
        }

        return pack;
    }

    function serializePack(pack) {
        var nameInput = pack.querySelector("[data-tech-pack-name]");
        var rows = Array.prototype.slice.call(pack.querySelectorAll("[data-tech-row]")).map(function (row) {
            return {
                label: (row.querySelector("[data-tech-row-label]") || {}).value || "",
                value: (row.querySelector("[data-tech-row-value]") || {}).value || "",
                icon: (row.querySelector("[data-tech-row-icon]") || {}).value || "",
            };
        });
        return {
            name: nameInput ? nameInput.value : "",
            rows: rows,
            sourceId: pack.dataset.sourceId || "",
            sourceName: pack.dataset.sourceName || "",
        };
    }

    function syncJson() {
        if (!jsonInput) return;
        var packs = Array.prototype.slice.call(packsWrap.querySelectorAll("[data-tech-pack]")).map(function (pack) {
            var data = serializePack(pack);
            return { name: data.name, rows: data.rows };
        });
        jsonInput.value = JSON.stringify(packs);
    }

    function renderSources() {
        if (!sourceList || !sourcesWrap) return;
        var seen = {};
        var items = [];
        Array.prototype.slice.call(packsWrap.querySelectorAll("[data-tech-pack]")).forEach(function (pack) {
            var id = pack.dataset.sourceId;
            var name = pack.dataset.sourceName;
            if (!id || seen[id]) return;
            seen[id] = true;
            items.push({ id: id, name: name || ("Produkt " + id) });
        });
        sourceList.innerHTML = "";
        items.forEach(function (item) {
            var chip = document.createElement("span");
            chip.className = "cms-related-chip";
            chip.textContent = item.name + " ";
            var button = document.createElement("button");
            button.type = "button";
            button.setAttribute("aria-label", "Usuń dane z tego produktu");
            button.textContent = "×";
            button.addEventListener("click", function () {
                Array.prototype.slice.call(packsWrap.querySelectorAll("[data-tech-pack]")).forEach(function (pack) {
                    if (pack.dataset.sourceId === item.id) pack.remove();
                });
                renderSources();
                syncJson();
            });
            chip.appendChild(button);
            sourceList.appendChild(chip);
        });
        sourcesWrap.hidden = items.length === 0;
    }

    function renderPacks(packs) {
        packsWrap.innerHTML = "";
        (packs || []).forEach(function (pack) {
            packsWrap.appendChild(createPack(pack));
        });
        renderSources();
        syncJson();
    }

    function appendPacks(packs, source) {
        (packs || []).forEach(function (pack) {
            var data = {
                name: pack.name,
                rows: pack.rows || [],
                sourceId: source && source.id ? String(source.id) : "",
                sourceName: source && source.text ? source.text : "",
            };
            packsWrap.appendChild(createPack(data));
        });
        renderSources();
        syncJson();
    }

    if (addPackBtn) {
        addPackBtn.addEventListener("click", function () {
            packsWrap.appendChild(createPack({ name: "", rows: [{ label: "", value: "", icon: "" }] }));
            syncJson();
        });
    }

    function copyUrlFor(id) {
        return copyUrlTemplate.replace(/\/0\/dane-techniczne\/?$/, "/" + id + "/dane-techniczne/");
    }

    if (copySearch && copyResults && searchUrl) {
        copySearch.addEventListener("input", function () {
            window.clearTimeout(searchTimer);
            var query = copySearch.value.trim();
            if (query.length < 2) {
                copyResults.innerHTML = "";
                return;
            }
            searchTimer = window.setTimeout(function () {
                var url = searchUrl + "?q=" + encodeURIComponent(query);
                if (productId) url += "&exclude=" + encodeURIComponent(productId);
                fetch(url, { headers: { Accept: "application/json" } })
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (payload) {
                        copyResults.innerHTML = "";
                        (payload.results || []).forEach(function (item) {
                            var button = document.createElement("button");
                            button.type = "button";
                            button.className = "cms-related-result";
                            button.textContent = item.text;
                            button.addEventListener("click", function () {
                                fetch(copyUrlFor(item.id), { headers: { Accept: "application/json" } })
                                    .then(function (response) {
                                        return response.json();
                                    })
                                    .then(function (data) {
                                        appendPacks(data.packs || [], item);
                                        copyResults.innerHTML = "";
                                        copySearch.value = "";
                                    });
                            });
                            copyResults.appendChild(button);
                        });
                    });
            }, 220);
        });
    }

    var form = document.getElementById("product-form");
    if (form) {
        form.addEventListener("submit", syncJson, true);
    }

    renderPacks(readInitial());
})();
