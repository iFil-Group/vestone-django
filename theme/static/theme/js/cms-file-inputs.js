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

    function setPreviewImage(preview, input, file) {
        if (!preview || !file || file.type.indexOf("image/") !== 0) {
            return;
        }

        if (file.size > MAX_PREVIEW_BYTES) {
            preview.hidden = true;
            preview.removeAttribute("src");
            return;
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
                                return;
                            }
                            var objectUrl = URL.createObjectURL(blob);
                            input._cmsObjectUrl = objectUrl;
                            preview.src = objectUrl;
                            preview.hidden = false;
                        },
                        "image/jpeg",
                        0.82
                    );
                })
                .catch(function () {
                    revokeObjectUrl(input);
                    var objectUrl = URL.createObjectURL(file);
                    input._cmsObjectUrl = objectUrl;
                    preview.src = objectUrl;
                    preview.hidden = false;
                });
            return;
        }

        revokeObjectUrl(input);
        var fallbackUrl = URL.createObjectURL(file);
        input._cmsObjectUrl = fallbackUrl;
        preview.src = fallbackUrl;
        preview.hidden = false;
    }

    function bindFileField(wrapper) {
        if (wrapper.dataset.cmsFileBound === "1") {
            return;
        }
        wrapper.dataset.cmsFileBound = "1";

        var input = wrapper.querySelector(".cms-file__input");
        var trigger = wrapper.querySelector("[data-cms-file-trigger]");
        var nameEl = wrapper.querySelector("[data-cms-file-name]");
        var preview = wrapper.querySelector("[data-cms-file-preview]");
        var clearButton = wrapper.querySelector("[data-cms-file-clear]");
        var clearField = wrapper.querySelector("[data-cms-file-clear-field] input[type='checkbox']");
        var currentBlock = wrapper.querySelector("[data-cms-file-current]");

        if (trigger && input) {
            trigger.addEventListener("click", function (event) {
                event.preventDefault();
                input.click();
            });
        }

        if (input && nameEl) {
            input.addEventListener("change", function () {
                var file = input.files && input.files[0];
                if (!file) {
                    return;
                }

                nameEl.textContent = file.name;

                window.setTimeout(function () {
                    setPreviewImage(preview, input, file);
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
            clearButton.addEventListener("click", function () {
                var marked = clearField.checked;
                clearField.checked = !marked;
                clearButton.textContent = marked ? "Usuń plik" : "Przywróć plik";
                clearButton.classList.toggle("is-active", !marked);
                if (currentBlock) {
                    currentBlock.classList.toggle("is-marked-delete", !marked);
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

        function syncRowState() {
            var marked = deleteField.checked;
            row.classList.toggle("is-marked-delete", marked);
            deleteButton.textContent = marked ? "Przywróć" : "Usuń";
            deleteButton.classList.toggle("is-active", marked);
        }

        deleteButton.addEventListener("click", function () {
            deleteField.checked = !deleteField.checked;
            syncRowState();
        });

        syncRowState();
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
