(function () {
    "use strict";

    var MAX_PREVIEW_BYTES = 10 * 1024 * 1024;
    var PREVIEW_MAX_WIDTH = 640;

    function revokeObjectUrl(input) {
        var previous = input && input._cmsObjectUrl;
        if (previous) {
            URL.revokeObjectURL(previous);
            input._cmsObjectUrl = null;
        }
    }

    function setHidden(el, hidden) {
        if (!el) return;
        el.classList.toggle("is-hidden", !!hidden);
        el.hidden = !!hidden;
    }

    function setPreviewImage(preview, input, file, callback) {
        if (!preview || !file || file.type.indexOf("image/") !== 0) {
            if (callback) callback(false);
            return;
        }

        if (file.size > MAX_PREVIEW_BYTES) {
            preview.hidden = true;
            preview.removeAttribute("src");
            if (callback) callback(false);
            return;
        }

        function applyUrl(objectUrl) {
            input._cmsObjectUrl = objectUrl;
            preview.src = objectUrl;
            preview.hidden = false;
            if (callback) callback(true);
        }

        if (typeof createImageBitmap === "function") {
            createImageBitmap(file, {
                resizeWidth: PREVIEW_MAX_WIDTH,
                resizeQuality: "medium",
            })
                .then(function (bitmap) {
                    var canvas = document.createElement("canvas");
                    canvas.width = bitmap.width;
                    canvas.height = bitmap.height;
                    canvas.getContext("2d").drawImage(bitmap, 0, 0);
                    bitmap.close();
                    revokeObjectUrl(input);
                    canvas.toBlob(
                        function (blob) {
                            if (!blob) {
                                if (callback) callback(false);
                                return;
                            }
                            applyUrl(URL.createObjectURL(blob));
                        },
                        "image/jpeg",
                        0.82
                    );
                })
                .catch(function () {
                    revokeObjectUrl(input);
                    applyUrl(URL.createObjectURL(file));
                });
            return;
        }

        revokeObjectUrl(input);
        applyUrl(URL.createObjectURL(file));
    }

    function assignFiles(input, files) {
        if (!input || !files || !files.length) return;
        try {
            var transfer = new DataTransfer();
            transfer.items.add(files[0]);
            input.files = transfer.files;
        } catch (err) {
            return;
        }
        input.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function bindFileField(wrapper) {
        if (wrapper.dataset.cmsFileBound === "1") {
            return;
        }
        wrapper.dataset.cmsFileBound = "1";

        var input = wrapper.querySelector(".cms-file__input");
        var trigger = wrapper.querySelector("[data-cms-file-trigger]");
        var dropzone = wrapper.querySelector("[data-cms-file-dropzone]");
        var nameEl = wrapper.querySelector("[data-cms-file-name]");
        var preview = wrapper.querySelector("[data-cms-file-preview]");
        var clearButton = wrapper.querySelector("[data-cms-file-clear]");
        var clearField = wrapper.querySelector("[data-cms-file-clear-field] input[type='checkbox']");
        var currentBlock = wrapper.querySelector("[data-cms-file-current]");
        var pending = wrapper.querySelector("[data-cms-file-pending]");
        var pendingPreview = wrapper.querySelector("[data-cms-file-pending-preview]");
        var pendingName = wrapper.querySelector("[data-cms-file-pending-name]");
        var pendingClear = wrapper.querySelector("[data-cms-file-pending-clear]");

        function showFilled(file) {
            wrapper.classList.add("cms-file--has-file");
            setHidden(dropzone, true);
            setHidden(currentBlock, true);
            setHidden(pending, false);
            if (pendingName) pendingName.textContent = file.name;
            setPreviewImage(pendingPreview || preview, input, file);
        }

        function showEmpty() {
            wrapper.classList.remove("cms-file--has-file");
            setHidden(pending, true);
            setHidden(currentBlock, true);
            setHidden(dropzone, false);
            if (nameEl) nameEl.textContent = "Przeciągnij plik lub kliknij";
            if (preview) {
                preview.hidden = true;
                preview.removeAttribute("src");
            }
            if (pendingPreview) {
                pendingPreview.hidden = true;
                pendingPreview.removeAttribute("src");
            }
        }

        if (trigger && input) {
            trigger.addEventListener("click", function (event) {
                event.preventDefault();
                input.click();
            });
        }

        if (dropzone) {
            ["dragenter", "dragover"].forEach(function (type) {
                dropzone.addEventListener(type, function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    dropzone.classList.add("is-dragover");
                });
            });
            ["dragleave", "drop"].forEach(function (type) {
                dropzone.addEventListener(type, function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    dropzone.classList.remove("is-dragover");
                });
            });
            dropzone.addEventListener("drop", function (event) {
                var files = event.dataTransfer && event.dataTransfer.files;
                assignFiles(input, files);
            });
        }

        if (input) {
            input.addEventListener("change", function () {
                var file = input.files && input.files[0];
                if (!file) {
                    return;
                }
                if (clearField) clearField.checked = false;
                showFilled(file);
                window.setTimeout(function () {
                    input.dispatchEvent(
                        new CustomEvent("cms:file-selected", {
                            bubbles: true,
                            detail: { file: file, input: input },
                        })
                    );
                }, 0);
            });
        }

        if (clearButton && clearField) {
            clearButton.addEventListener("click", function (event) {
                event.preventDefault();
                clearField.checked = true;
                revokeObjectUrl(input);
                if (input) input.value = "";
                showEmpty();
            });
        }

        if (pendingClear) {
            pendingClear.addEventListener("click", function (event) {
                event.preventDefault();
                revokeObjectUrl(input);
                if (input) input.value = "";
                if (clearField) clearField.checked = true;
                if (currentBlock && !clearField) {
                    showEmpty();
                } else if (currentBlock && clearField) {
                    showEmpty();
                } else {
                    showEmpty();
                }
            });
        }
    }

    function bindFormsetRow(row) {
        var deleteButton = row.querySelector("[data-cms-row-delete]");
        var deleteField = row.querySelector("[data-cms-delete-field] input[type='checkbox']");

        if (!deleteButton || !deleteField) {
            return;
        }

        deleteButton.addEventListener("click", function (event) {
            event.preventDefault();
            deleteField.checked = true;
            row.classList.add("is-removed");
            row.hidden = true;
        });
    }

    function bindToggle(field) {
        var input = field.querySelector('input[type="checkbox"]');
        var text = field.querySelector("[data-cms-toggle-text]");
        if (!input || !text) {
            return;
        }

        function syncToggle() {
            text.textContent = input.checked ? "Tak" : "Nie";
        }

        input.addEventListener("change", syncToggle);
        syncToggle();
    }

    document.querySelectorAll("[data-cms-file]").forEach(bindFileField);
    document.querySelectorAll("[data-cms-formset-row]").forEach(bindFormsetRow);
    document.querySelectorAll(".cms-toggle").forEach(bindToggle);
    window.cmsBindFileField = bindFileField;
    window.cmsBindFormsetRow = bindFormsetRow;
})();
