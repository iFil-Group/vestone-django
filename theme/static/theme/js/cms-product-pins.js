(function () {
    "use strict";

    var editor = document.querySelector("[data-pin-editor]");
    if (!editor) {
        return;
    }

    var prefix = editor.getAttribute("data-pin-prefix") || "pins";
    var stage = editor.querySelector("[data-pin-stage]");
    var overlay = editor.querySelector("[data-pin-overlay]");
    var image = editor.querySelector("[data-pin-image]");
    var rowsContainer = editor.querySelector("[data-pin-rows]");
    var totalFormsInput = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
    var template = editor.querySelector("[data-pin-empty-template]");
    var imageInput = document.getElementById("id_image");
    var addButton = editor.querySelector("[data-pin-add]");
    var pinObjectUrl = null;
    var PIN_PREVIEW_MAX_WIDTH = 1200;

    function setPinPreviewFromFile(file) {
        if (!file || !image || file.type.indexOf("image/") !== 0) {
            return;
        }

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
                        canvas.toBlob(
                            function (blob) {
                                if (!blob) {
                                    return;
                                }
                                if (pinObjectUrl) {
                                    URL.revokeObjectURL(pinObjectUrl);
                                }
                                pinObjectUrl = URL.createObjectURL(blob);
                                image.src = pinObjectUrl;
                            },
                            "image/jpeg",
                            0.85
                        );
                    })
                    .catch(function () {
                        /* Pin preview is optional — skip on error to keep UI responsive. */
                    });
                return;
            }

            if (file.size > 8 * 1024 * 1024) {
                return;
            }

            if (pinObjectUrl) {
                URL.revokeObjectURL(pinObjectUrl);
            }
            pinObjectUrl = URL.createObjectURL(file);
            image.src = pinObjectUrl;
        }, 0);
    }

    var activeRow = null;
    var dragState = null;
    var suppressNextClick = false;
    var productForm = document.getElementById("product-form");

    function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function getRowFields(row) {
        return {
            x: row.querySelector('[name$="-x"]'),
            y: row.querySelector('[name$="-y"]'),
            text: row.querySelector('[name$="-text"]'),
            sort: row.querySelector('[name$="-sort_order"]'),
            deleteInput: row.querySelector('[name$="-DELETE"]'),
            idInput: row.querySelector('[name$="-id"]'),
        };
    }

    function rowIsDeleted(row) {
        var fields = getRowFields(row);
        return fields.deleteInput && fields.deleteInput.checked;
    }

    function allRows() {
        return Array.prototype.slice.call(rowsContainer.querySelectorAll("[data-pin-row]"));
    }

    function visibleRows() {
        return allRows().filter(function (row) {
            return !row.hidden && !rowIsDeleted(row);
        });
    }

    function reindexRows() {
        var rows = allRows();
        rows.forEach(function (row, index) {
            row.dataset.pinIndex = String(index);
            var labelNum = row.querySelector("[data-pin-label-num]");
            if (labelNum) {
                labelNum.textContent = String(index + 1);
            }

            row.querySelectorAll("input, textarea, select, label").forEach(function (node) {
                if (node.name) {
                    node.name = node.name.replace(new RegExp("^" + prefix + "-\\d+-"), prefix + "-" + index + "-");
                }
                if (node.id) {
                    node.id = node.id.replace(new RegExp("^id_" + prefix + "-\\d+-"), "id_" + prefix + "-" + index + "-");
                }
                if (node.htmlFor) {
                    node.htmlFor = node.htmlFor.replace(
                        new RegExp("^id_" + prefix + "-\\d+-"),
                        "id_" + prefix + "-" + index + "-"
                    );
                }
            });

            var fields = getRowFields(row);
            if (fields.sort) {
                fields.sort.value = String(index);
            }
        });

        if (totalFormsInput) {
            totalFormsInput.value = String(rows.length);
        }
    }

    function setFieldValue(field, value) {
        if (field) {
            field.value = value;
            field.dispatchEvent(new Event("change", { bubbles: true }));
        }
    }

    function renderPins() {
        overlay.innerHTML = "";
        visibleRows().forEach(function (row, index) {
            var fields = getRowFields(row);
            var x = parseFloat(fields.x && fields.x.value ? fields.x.value : "50");
            var y = parseFloat(fields.y && fields.y.value ? fields.y.value : "50");
            var pin = document.createElement("button");
            pin.type = "button";
            pin.className = "cms-pin-editor__pin";
            pin.dataset.editorPin = String(index);
            pin.style.setProperty("--pin-x", x + "%");
            pin.style.setProperty("--pin-y", y + "%");
            pin.setAttribute("aria-label", "Pin " + (index + 1));
            if (row === activeRow) {
                pin.classList.add("is-active");
            }
            overlay.appendChild(pin);
        });
    }

    function selectRow(row, options) {
        options = options || {};
        activeRow = row;
        visibleRows().forEach(function (item) {
            item.classList.toggle("is-active", item === row);
        });
        renderPins();
        if (row && options.focus) {
            var fields = getRowFields(row);
            if (fields.text) {
                fields.text.focus();
            }
        }
    }

    function addRowAt(x, y, text) {
        if (!template || !totalFormsInput) {
            return null;
        }

        var html = template.innerHTML
            .replace(/__prefix__/g, String(allRows().length))
            .replace(/__num__/g, String(visibleRows().length + 1));

        rowsContainer.insertAdjacentHTML("beforeend", html);

        var row = rowsContainer.lastElementChild;
        var fields = getRowFields(row);
        setFieldValue(fields.x, x.toFixed(2));
        setFieldValue(fields.y, y.toFixed(2));
        if (text) {
            setFieldValue(fields.text, text);
        } else if (fields.text) {
            fields.text.value = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
        }

        bindRow(row);
        reindexRows();
        selectRow(row, { focus: false });
        return row;
    }

    function removeRow(row) {
        var fields = getRowFields(row);
        if (fields.idInput && fields.idInput.value) {
            if (fields.deleteInput) {
                fields.deleteInput.checked = true;
            }
            row.hidden = true;
        } else {
            row.remove();
        }

        if (activeRow === row) {
            activeRow = null;
        }
        reindexRows();
        renderPins();
    }

    function positionFromEvent(event) {
        var rect = stage.getBoundingClientRect();
        var x = clamp(((event.clientX - rect.left) / rect.width) * 100, 2, 98);
        var y = clamp(((event.clientY - rect.top) / rect.height) * 100, 2, 98);
        return { x: x, y: y };
    }

    function bindRow(row) {
        var removeButton = row.querySelector("[data-pin-remove]");
        var fields = getRowFields(row);

        if (removeButton) {
            removeButton.addEventListener("click", function () {
                removeRow(row);
            });
        }

        if (fields.text) {
            fields.text.addEventListener("focus", function () {
                selectRow(row, { focus: false });
            });
        }

        row.addEventListener("click", function () {
            selectRow(row, { focus: true });
        });
    }

    overlay.addEventListener("click", function (event) {
        if (suppressNextClick) {
            return;
        }
        if (event.target.closest("[data-editor-pin]")) {
            return;
        }
        var position = positionFromEvent(event);
        addRowAt(position.x, position.y);
    });

    overlay.addEventListener("mousedown", function (event) {
        var pinButton = event.target.closest("[data-editor-pin]");
        if (!pinButton) {
            return;
        }
        event.preventDefault();
        var index = parseInt(pinButton.dataset.editorPin, 10);
        var row = visibleRows()[index];
        if (!row) {
            return;
        }
        selectRow(row, { focus: false });
        dragState = {
            row: row,
            moved: false,
        };
    });

    document.addEventListener("mousemove", function (event) {
        if (!dragState) {
            return;
        }
        dragState.moved = true;
        var position = positionFromEvent(event);
        var fields = getRowFields(dragState.row);
        setFieldValue(fields.x, position.x.toFixed(2));
        setFieldValue(fields.y, position.y.toFixed(2));
        renderPins();
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

    if (addButton) {
        addButton.addEventListener("click", function () {
            addRowAt(50, 50);
        });
    }

    rowsContainer.querySelectorAll("[data-pin-row]").forEach(bindRow);

    visibleRows().forEach(function (row, index) {
        var fields = getRowFields(row);
        if (fields.sort) {
            fields.sort.value = String(index);
        }
        if (fields.text && !fields.text.value) {
            fields.text.value = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
        }
    });

    if (productForm) {
        productForm.addEventListener("cms:file-selected", function (event) {
            var detail = event.detail || {};
            if (detail.input && detail.input.id === "id_image") {
                setPinPreviewFromFile(detail.file);
            }
        });

        productForm.addEventListener("submit", function () {
            reindexRows();
        }, true);
    }

    reindexRows();
    renderPins();

    if (visibleRows().length) {
        selectRow(visibleRows()[0], { focus: false });
    }
})();
