(function () {
    "use strict";

    var productForm = document.getElementById("product-form");
    if (!productForm) return;

    var prefix = "pins";
    var bank = productForm.querySelector("[data-pin-bank]");
    var template = productForm.querySelector("[data-pin-empty-template]");
    var totalFormsInput = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
    var pinObjectUrl = null;
    var PIN_PREVIEW_MAX_WIDTH = 1200;
    var activeRow = null;
    var dragState = null;
    var suppressNextClick = false;
    var refreshing = false;

    function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function allRows() {
        return Array.prototype.slice
            .call(productForm.querySelectorAll("[data-pin-row]"))
            .filter(function (row) {
                return !row.closest("template");
            });
    }

    function getRowFields(row) {
        return {
            x: row.querySelector('input[name$="-x"]'),
            y: row.querySelector('input[name$="-y"]'),
            text: row.querySelector('textarea[name$="-text"], input[name$="-text"]'),
            galleryImage: row.querySelector('input[name$="-gallery_image"], select[name$="-gallery_image"]'),
            galleryPending: row.querySelector('input[name$="-gallery_pending"]'),
            sort: row.querySelector('input[name$="-sort_order"]'),
            deleteInput: row.querySelector('input[name$="-DELETE"]'),
            idInput: row.querySelector('input[name$="-id"]'),
        };
    }

    function rowIsDeleted(row) {
        var fields = getRowFields(row);
        return !!(fields.deleteInput && fields.deleteInput.checked);
    }

    function rowTargetId(row) {
        var fields = getRowFields(row);
        if (fields.galleryPending && String(fields.galleryPending.value || "") !== "") {
            return "pending:" + String(fields.galleryPending.value);
        }
        return fields.galleryImage ? String(fields.galleryImage.value || "") : "";
    }

    function editors() {
        return Array.prototype.slice.call(productForm.querySelectorAll("[data-pin-editor]"));
    }

    function editorForTarget(targetId) {
        var id = String(targetId || "");
        var list = editors();
        for (var i = 0; i < list.length; i += 1) {
            if (String(list[i].getAttribute("data-pin-target-id") || "") === id) {
                return list[i];
            }
        }
        return null;
    }

    function rowsForTarget(targetId) {
        var id = String(targetId || "");
        return allRows().filter(function (row) {
            return !rowIsDeleted(row) && rowTargetId(row) === id;
        });
    }

    function safeAppend(parent, node) {
        if (!parent || !node || node.parentNode === parent) return;
        try {
            parent.appendChild(node);
        } catch (err) {
            if (typeof console !== "undefined" && console.error) {
                console.error("Pin row move failed", err);
            }
        }
    }

    function placeRows() {
        allRows().forEach(function (row) {
            if (rowIsDeleted(row)) {
                safeAppend(bank, row);
                row.hidden = true;
                return;
            }
            var editor = editorForTarget(rowTargetId(row));
            var dest = editor && editor.querySelector("[data-pin-rows]");
            if (dest) {
                safeAppend(dest, row);
                row.hidden = false;
            } else {
                safeAppend(bank, row);
                row.hidden = true;
            }
        });
    }

    function rewritePrefix(node, index) {
        var from = new RegExp("^" + prefix + "-__prefix__-");
        var fromIndexed = new RegExp("^" + prefix + "-\\d+-");
        var idFrom = new RegExp("^id_" + prefix + "-__prefix__-");
        var idFromIndexed = new RegExp("^id_" + prefix + "-\\d+-");

        if (node.name) {
            node.name = node.name
                .replace(from, prefix + "-" + index + "-")
                .replace(fromIndexed, prefix + "-" + index + "-");
        }
        if (node.id) {
            node.id = node.id
                .replace(idFrom, "id_" + prefix + "-" + index + "-")
                .replace(idFromIndexed, "id_" + prefix + "-" + index + "-");
        }
        if (node.htmlFor) {
            node.htmlFor = node.htmlFor
                .replace(idFrom, "id_" + prefix + "-" + index + "-")
                .replace(idFromIndexed, "id_" + prefix + "-" + index + "-");
        }
    }

    function reindexRows() {
        var rows = allRows();
        rows.forEach(function (row, index) {
            row.dataset.pinIndex = String(index);
            row.querySelectorAll("input, textarea, select, label").forEach(function (node) {
                rewritePrefix(node, index);
            });
            var fields = getRowFields(row);
            if (fields.sort) fields.sort.value = String(index);
        });

        editors().forEach(function (editor) {
            rowsForTarget(editor.getAttribute("data-pin-target-id") || "").forEach(function (row, index) {
                var labelNum = row.querySelector("[data-pin-label-num]");
                if (labelNum) labelNum.textContent = String(index + 1);
            });
        });

        if (totalFormsInput) totalFormsInput.value = String(rows.length);
    }

    function setFieldValue(field, value) {
        if (!field) return;
        field.value = value == null ? "" : String(value);
    }

    function ensureHiddenField(row, fieldName, value) {
        var selector = 'input[name$="-' + fieldName + '"]';
        var input = row.querySelector(selector);
        if (!input) {
            var index = row.dataset.pinIndex || "0";
            input = document.createElement("input");
            input.type = "hidden";
            input.name = prefix + "-" + index + "-" + fieldName;
            row.insertBefore(input, row.firstChild);
        }
        setFieldValue(input, value);
        return input;
    }

    function ensureTargetFields(row, targetId) {
        var id = String(targetId || "");
        if (id.indexOf("pending:") === 0) {
            ensureHiddenField(row, "gallery_image", "");
            ensureHiddenField(row, "gallery_pending", id.slice("pending:".length));
            return;
        }
        ensureHiddenField(row, "gallery_image", id);
        ensureHiddenField(row, "gallery_pending", "");
    }

    function renderPins(editor) {
        var overlay = editor.querySelector("[data-pin-overlay]");
        if (!overlay) return;
        overlay.innerHTML = "";
        var targetId = editor.getAttribute("data-pin-target-id") || "";
        rowsForTarget(targetId).forEach(function (row, index) {
            var fields = getRowFields(row);
            var x = parseFloat(fields.x && fields.x.value ? fields.x.value : "50");
            var y = parseFloat(fields.y && fields.y.value ? fields.y.value : "50");
            if (isNaN(x)) x = 50;
            if (isNaN(y)) y = 50;
            var pin = document.createElement("button");
            pin.type = "button";
            pin.className = "cms-pin-editor__pin";
            pin.dataset.editorPin = String(index);
            pin.style.setProperty("--pin-x", x + "%");
            pin.style.setProperty("--pin-y", y + "%");
            pin.setAttribute("aria-label", "Pin " + (index + 1));
            if (row === activeRow) pin.classList.add("is-active");
            overlay.appendChild(pin);
        });
    }

    function renderAllPins() {
        editors().forEach(renderPins);
    }

    function selectRow(row, options) {
        options = options || {};
        activeRow = row;
        allRows().forEach(function (item) {
            item.classList.toggle("is-active", item === row);
        });
        renderAllPins();
        if (row && options.focus) {
            var fields = getRowFields(row);
            if (fields.text && typeof fields.text.focus === "function") {
                try {
                    fields.text.focus({ preventScroll: true });
                } catch (err) {
                    try {
                        fields.text.focus();
                    } catch (err2) {
                        /* ignore */
                    }
                }
            }
        }
    }

    function stageHasImage(editor) {
        var stage = editor.querySelector("[data-pin-stage]");
        var image = editor.querySelector("[data-pin-image]");
        if (!stage || stage.classList.contains("cms-pin-editor__stage--empty")) return false;
        if (!image || image.hidden) return false;
        return !!(image.getAttribute("src") || image.currentSrc);
    }

    function enablePinsCheckbox(editor) {
        var targetId = editor.getAttribute("data-pin-target-id") || "";
        if (!targetId) return;
        var tile = editor.closest("[data-gallery-tile]");
        var enableInput = tile && tile.querySelector('input[type="checkbox"][name$="-pins_enabled"]');
        if (enableInput && !enableInput.checked) {
            enableInput.checked = true;
            enableInput.dispatchEvent(new Event("change", { bubbles: true }));
        }
    }

    function addRowAt(editor, x, y) {
        if (!template || !template.content || !totalFormsInput) return null;
        if (!stageHasImage(editor)) return null;

        try {
            var targetId = editor.getAttribute("data-pin-target-id") || "";
            var index = allRows().length;
            var fragment = template.content.cloneNode(true);
            var row = fragment.querySelector("[data-pin-row]");
            if (!row) return null;

            row.dataset.pinIndex = String(index);
            row.querySelectorAll("input, textarea, select, label").forEach(function (node) {
                rewritePrefix(node, index);
            });
            var labelNum = row.querySelector("[data-pin-label-num]");
            if (labelNum) {
                labelNum.textContent = String(rowsForTarget(targetId).length + 1);
            }

            var dest = editor.querySelector("[data-pin-rows]") || bank;
            if (!dest) return null;
            dest.appendChild(row);

            var fields = getRowFields(row);
            ensureTargetFields(row, targetId);
            setFieldValue(fields.x, Number(x).toFixed(2));
            setFieldValue(fields.y, Number(y).toFixed(2));
            if (fields.text && !fields.text.value) {
                fields.text.value = "Opis pinu";
            }

            bindRow(row);
            reindexRows();
            placeRows();
            selectRow(row, { focus: false });
            renderPins(editor);
            enablePinsCheckbox(editor);
            return row;
        } catch (err) {
            if (typeof console !== "undefined" && console.error) {
                console.error("Nie udało się dodać pinu", err);
            }
            return null;
        }
    }

    function removeRow(row) {
        var fields = getRowFields(row);
        if (fields.idInput && fields.idInput.value) {
            if (fields.deleteInput) fields.deleteInput.checked = true;
            row.hidden = true;
            if (bank) bank.appendChild(row);
        } else {
            row.remove();
        }
        if (activeRow === row) activeRow = null;
        reindexRows();
        placeRows();
        renderAllPins();
    }

    function positionFromEvent(stage, event) {
        var rect = stage.getBoundingClientRect();
        if (!rect.width || !rect.height) {
            return { x: 50, y: 50 };
        }
        return {
            x: clamp(((event.clientX - rect.left) / rect.width) * 100, 2, 98),
            y: clamp(((event.clientY - rect.top) / rect.height) * 100, 2, 98),
        };
    }

    function bindRow(row) {
        if (!row || row.dataset.pinBound === "1") return;
        row.dataset.pinBound = "1";
        var removeButton = row.querySelector("[data-pin-remove]");
        var fields = getRowFields(row);

        if (removeButton) {
            removeButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                removeRow(row);
            });
        }
        if (fields.text) {
            fields.text.addEventListener("focus", function () {
                selectRow(row, { focus: false });
            });
        }
        row.addEventListener("click", function (event) {
            if (event.target.closest("[data-pin-remove]")) return;
            selectRow(row, { focus: false });
        });
    }

    function bindEditor(editor) {
        if (!editor || editor.dataset.pinEditorBound === "1") return;
        editor.dataset.pinEditorBound = "1";

        var stage = editor.querySelector("[data-pin-stage]");
        var overlay = editor.querySelector("[data-pin-overlay]");
        var addButton = editor.querySelector("[data-pin-add]");
        var image = editor.querySelector("[data-pin-image]");
        var imageUrl = editor.getAttribute("data-pin-image-url");
        if (image && imageUrl) image.src = imageUrl;

        if (stage) {
            // Click the stage (image/overlay) — more reliable than overlay-only hits.
            stage.addEventListener("click", function (event) {
                if (suppressNextClick) return;
                if (event.target.closest("[data-editor-pin]")) return;
                if (event.target.closest("a, button, input, textarea, label")) return;
                var position = positionFromEvent(stage, event);
                addRowAt(editor, position.x, position.y);
            });

            stage.addEventListener("mousedown", function (event) {
                var pinButton = event.target.closest("[data-editor-pin]");
                if (!pinButton) return;
                event.preventDefault();
                var index = parseInt(pinButton.dataset.editorPin, 10);
                var row = rowsForTarget(editor.getAttribute("data-pin-target-id") || "")[index];
                if (!row) return;
                selectRow(row, { focus: false });
                dragState = { row: row, stage: stage, moved: false };
            });
        }

        if (addButton) {
            addButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                addRowAt(editor, 50, 50);
            });
        }

        if (overlay) {
            overlay.style.pointerEvents = "auto";
        }

        placeRows();
        renderPins(editor);
    }

    function refreshEditors() {
        if (refreshing) return;
        refreshing = true;
        try {
            editors().forEach(bindEditor);
            placeRows();
            reindexRows();
            renderAllPins();
        } finally {
            refreshing = false;
        }
    }

    document.addEventListener("mousemove", function (event) {
        if (!dragState) return;
        dragState.moved = true;
        var position = positionFromEvent(dragState.stage, event);
        var fields = getRowFields(dragState.row);
        setFieldValue(fields.x, position.x.toFixed(2));
        setFieldValue(fields.y, position.y.toFixed(2));
        renderAllPins();
    });

    document.addEventListener("mouseup", function () {
        if (dragState && dragState.moved) {
            suppressNextClick = true;
            window.setTimeout(function () {
                suppressNextClick = false;
            }, 0);
        }
        dragState = null;
    });

    function setPinPreviewFromFile(file) {
        var mainEditor = editorForTarget("");
        var image = mainEditor && mainEditor.querySelector("[data-pin-image]");
        if (!file || !image || file.type.indexOf("image/") !== 0) return;

        window.setTimeout(function () {
            if (typeof createImageBitmap === "function") {
                createImageBitmap(file, {
                    resizeWidth: PIN_PREVIEW_MAX_WIDTH,
                    resizeQuality: "medium",
                })
                    .then(function (bitmap) {
                        var canvas = document.createElement("canvas");
                        canvas.width = bitmap.width;
                        canvas.height = bitmap.height;
                        canvas.getContext("2d").drawImage(bitmap, 0, 0);
                        bitmap.close();
                        canvas.toBlob(function (blob) {
                            if (!blob) return;
                            if (pinObjectUrl) URL.revokeObjectURL(pinObjectUrl);
                            pinObjectUrl = URL.createObjectURL(blob);
                            image.src = pinObjectUrl;
                            var stage = mainEditor.querySelector("[data-pin-stage]");
                            if (stage) stage.classList.remove("cms-pin-editor__stage--empty");
                        }, "image/jpeg", 0.85);
                    })
                    .catch(function () {});
                return;
            }
            if (file.size > 8 * 1024 * 1024) return;
            if (pinObjectUrl) URL.revokeObjectURL(pinObjectUrl);
            pinObjectUrl = URL.createObjectURL(file);
            image.src = pinObjectUrl;
            var stage = mainEditor.querySelector("[data-pin-stage]");
            if (stage) stage.classList.remove("cms-pin-editor__stage--empty");
        }, 0);
    }

    productForm.addEventListener("cms:file-selected", function (event) {
        var detail = event.detail || {};
        if (detail.input && detail.input.id === "id_image") {
            setPinPreviewFromFile(detail.file);
        }
    });

    productForm.addEventListener("submit", function () {
        reindexRows();
    }, true);

    allRows().forEach(bindRow);

    // Bind main-image editor on load. Gallery editors are bound by cms-product-gallery.js.
    var mainEditor = editorForTarget("");
    if (mainEditor) {
        try {
            bindEditor(mainEditor);
        } catch (err) {
            if (typeof console !== "undefined" && console.error) {
                console.error("Main pin editor bind failed", err);
            }
        }
    }
    placeRows();
    reindexRows();
    if (mainEditor) renderPins(mainEditor);

    window.cmsBindPinEditor = function (editor) {
        if (!editor) return;
        try {
            bindEditor(editor);
            placeRows();
            renderPins(editor);
        } catch (err) {
            if (typeof console !== "undefined" && console.error) {
                console.error("Pin editor bind failed", err);
            }
        }
    };
    window.cmsRefreshPinEditors = refreshEditors;
})();
