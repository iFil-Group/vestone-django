(function () {
    "use strict";

    var root = document.querySelector("[data-gallery-editor]");
    if (!root) return;

    var tilesWrap = root.querySelector("[data-gallery-tiles]");
    if (!tilesWrap) return;

    var totalFormsInput = document.getElementById("id_gallery-TOTAL_FORMS");
    var addButton = root.querySelector("[data-gallery-add]");
    var template = root.querySelector("[data-gallery-empty-template]");
    var previewUrls = {};

    function tiles() {
        return Array.prototype.slice.call(tilesWrap.querySelectorAll("[data-gallery-tile]")).filter(function (tile) {
            return !tile.hidden && !tile.classList.contains("is-removed");
        });
    }

    function syncSortOrder() {
        tiles().forEach(function (tile, index) {
            var sortInput = tile.querySelector('input[name$="-sort_order"]');
            if (sortInput) sortInput.value = String(index);
            var title = tile.querySelector("[data-gallery-title]");
            if (title) title.textContent = "Zdjęcie nr " + (index + 1);
        });
    }

    function showPreview(tile, url) {
        if (!tile || !url) return;
        var image = tile.querySelector("[data-pin-image]");
        var placeholder = tile.querySelector("[data-pin-placeholder]");
        var stage = tile.querySelector("[data-pin-stage]");
        if (image) {
            image.hidden = false;
            image.src = url;
        }
        if (placeholder) placeholder.hidden = true;
        if (stage) stage.classList.remove("cms-pin-editor__stage--empty");
        var editor = tile.querySelector("[data-pin-editor]");
        if (editor) editor.setAttribute("data-pin-image-url", url);
    }

    function setPreviewFromFile(tile, file) {
        if (!tile || !file || file.type.indexOf("image/") !== 0) return;
        var input = tile.querySelector('input[type="file"][name$="-image"]');
        var key = input ? input.name : String(Math.random());
        if (previewUrls[key]) {
            URL.revokeObjectURL(previewUrls[key]);
        }
        var url = URL.createObjectURL(file);
        previewUrls[key] = url;
        showPreview(tile, url);
    }

    function bindTile(tile) {
        if (tile.dataset.galleryBound === "1") return;
        tile.dataset.galleryBound = "1";

        tile.querySelectorAll("[data-gallery-move]").forEach(function (button) {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                var direction = button.getAttribute("data-gallery-move");
                var list = tiles();
                var index = list.indexOf(tile);
                if (index < 0) return;
                if (direction === "up" && index > 0) {
                    tilesWrap.insertBefore(tile, list[index - 1]);
                }
                if (direction === "down" && index < list.length - 1) {
                    tilesWrap.insertBefore(list[index + 1], tile);
                }
                syncSortOrder();
            });
        });

        if (typeof window.cmsBindFormsetRow === "function") {
            window.cmsBindFormsetRow(tile);
        }
        tile.querySelectorAll("[data-cms-file]").forEach(function (field) {
            if (typeof window.cmsBindFileField === "function") {
                window.cmsBindFileField(field);
            }
        });
    }

    tilesWrap.querySelectorAll("[data-gallery-tile]").forEach(bindTile);
    syncSortOrder();

    window.setTimeout(function () {
        if (typeof window.cmsBindPinEditor !== "function") return;
        tilesWrap.querySelectorAll("[data-pin-editor]").forEach(function (editor) {
            try {
                window.cmsBindPinEditor(editor);
            } catch (err) {
                if (typeof console !== "undefined" && console.error) {
                    console.error("Gallery pin editor failed", err);
                }
            }
        });
    }, 0);

    if (addButton && template && totalFormsInput) {
        addButton.addEventListener("click", function (event) {
            event.preventDefault();
            var index = parseInt(totalFormsInput.value, 10) || 0;
            var html = template.innerHTML
                .replace(/__prefix__/g, String(index))
                .replace(/__num__/g, String(index + 1));
            tilesWrap.insertAdjacentHTML("beforeend", html);
            totalFormsInput.value = String(index + 1);
            var tile = tilesWrap.lastElementChild;
            if (!tile) return;
            bindTile(tile);
            syncSortOrder();
        });
    }

    var form = document.getElementById("product-form");
    if (form) {
        form.addEventListener("cms:file-selected", function (event) {
            var detail = event.detail || {};
            var input = detail.input;
            if (!input || !/-image$/.test(input.name || "") || input.name.indexOf("gallery-") !== 0) {
                return;
            }
            var tile = input.closest("[data-gallery-tile]");
            if (tile) setPreviewFromFile(tile, detail.file);
        });

        form.addEventListener(
            "submit",
            function () {
                syncSortOrder();
                if (totalFormsInput) {
                    totalFormsInput.value = String(
                        tilesWrap.querySelectorAll("[data-gallery-tile]").length
                    );
                }
            },
            true
        );
    }
})();
