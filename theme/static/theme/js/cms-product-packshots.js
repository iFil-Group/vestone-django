(function () {
    "use strict";

    var root = document.querySelector("[data-packshot-editor]");
    if (!root) return;

    var tilesWrap = root.querySelector("[data-packshot-tiles]");
    var addButton = root.querySelector("[data-packshot-add]");
    var template = root.querySelector("[data-packshot-empty-template]");
    var totalFormsInput = document.getElementById("id_packshots-TOTAL_FORMS");
    var columnsRoot = root.querySelector("[data-packshot-columns]");
    if (!tilesWrap || !totalFormsInput) return;

    function tiles() {
        return Array.prototype.slice.call(tilesWrap.querySelectorAll("[data-packshot-tile]")).filter(function (tile) {
            return !tile.hidden && !tile.classList.contains("is-removed");
        });
    }

    function tileHasImage(tile) {
        var idInput = tile.querySelector('input[name$="-id"]');
        var fileInput = tile.querySelector('input[type="file"][name$="-image"]');
        var clearInput = tile.querySelector('input[type="checkbox"][name$="-image-clear"]');
        if (clearInput && clearInput.checked) return false;
        if (fileInput && fileInput.files && fileInput.files.length) return true;
        if (idInput && idInput.value) {
            var existingPreview = tile.querySelector("[data-cms-file-existing-preview], .cms-file--has-file .cms-file__preview");
            if (existingPreview) return true;
            return true;
        }
        return false;
    }

    function syncSortOrder() {
        var index = 0;
        tiles().forEach(function (tile) {
            var title = tile.querySelector("[data-packshot-title]");
            if (title) title.textContent = "Packshot nr " + (index + 1);
            var sortInput = tile.querySelector('input[name$="-sort_order"]');
            if (sortInput && tileHasImage(tile)) {
                sortInput.value = String(index);
            }
            index += 1;
        });
    }

    function markEmptyForDelete() {
        tilesWrap.querySelectorAll("[data-packshot-tile]").forEach(function (tile) {
            if (tileHasImage(tile)) return;
            var deleteInput = tile.querySelector("[data-cms-delete-field] input[type='checkbox']");
            var idInput = tile.querySelector('input[name$="-id"]');
            if (deleteInput && idInput && idInput.value) {
                deleteInput.checked = true;
                tile.classList.add("is-removed");
                tile.hidden = true;
            }
        });
    }

    function bindTile(tile) {
        if (tile.dataset.packshotBound === "1") return;
        tile.dataset.packshotBound = "1";

        tile.querySelectorAll("[data-packshot-move]").forEach(function (button) {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                var direction = button.getAttribute("data-packshot-move");
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

    tilesWrap.querySelectorAll("[data-packshot-tile]").forEach(bindTile);
    syncSortOrder();

    if (columnsRoot) {
        columnsRoot.querySelectorAll(".cms-card-type__option").forEach(function (option) {
            var input = option.querySelector('input[type="radio"]');
            if (!input) return;
            input.addEventListener("change", function () {
                columnsRoot.querySelectorAll(".cms-card-type__option").forEach(function (item) {
                    var radio = item.querySelector('input[type="radio"]');
                    item.classList.toggle("is-selected", !!(radio && radio.checked));
                });
            });
            option.classList.toggle("is-selected", input.checked);
        });
    }

    if (addButton && template) {
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
        form.addEventListener(
            "submit",
            function () {
                markEmptyForDelete();
                syncSortOrder();
                totalFormsInput.value = String(
                    tilesWrap.querySelectorAll("[data-packshot-tile]").length
                );
            },
            true
        );
    }
})();
