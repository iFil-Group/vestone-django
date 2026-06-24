(function () {
    "use strict";

    var root = document.querySelector("[data-product-filters]");
    if (!root) {
        return;
    }

    var search = root.querySelector("[data-product-search]");
    var resetBtn = root.querySelector("[data-product-filters-reset]");
    var selects = root.querySelectorAll("[data-product-filter]");
    var resultsRoot = document.querySelector("[data-product-results]");
    var items = resultsRoot ? resultsRoot.querySelectorAll("[data-product-item]") : [];
    var countEl = document.querySelector("[data-product-count]");
    var emptyEl = document.querySelector("[data-product-empty]");

    function normalize(value) {
        return (value || "").toLowerCase().trim();
    }

    function selectedOptionText(select) {
        if (select.selectedIndex <= 0) {
            return "";
        }
        return select.options[select.selectedIndex].text.trim();
    }

    function hasActiveFilters() {
        var searchActive = search && search.value.trim() !== "";
        var selectActive = Array.prototype.some.call(selects, function (select) {
            return select.selectedIndex > 0;
        });
        return searchActive || selectActive;
    }

    function itemMatchesFilters(item) {
        var searchText = normalize(item.getAttribute("data-search"));
        var query = normalize(search ? search.value : "");
        var matchSearch = !query || searchText.indexOf(query) !== -1;

        var matchSelects = Array.prototype.every.call(selects, function (select) {
            var selected = normalize(selectedOptionText(select));
            if (!selected) {
                return true;
            }

            var filterName = select.getAttribute("name") || "";
            var itemValue = normalize(item.getAttribute("data-filter-" + filterName) || "");
            if (itemValue) {
                return itemValue === selected;
            }

            return searchText.indexOf(selected) !== -1;
        });

        return matchSearch && matchSelects;
    }

    function applyFilters() {
        var visibleCount = 0;

        items.forEach(function (item) {
            var visible = itemMatchesFilters(item);
            item.hidden = !visible;
            if (visible) {
                visibleCount += 1;
            }
        });

        if (countEl) {
            countEl.textContent = visibleCount === 1 ? "1 produkt" : visibleCount + " produktów";
        }

        if (emptyEl) {
            emptyEl.hidden = visibleCount > 0;
        }
    }

    function syncFieldStates() {
        selects.forEach(function (select) {
            var field = select.closest(".product-filters__field");
            if (field) {
                field.classList.toggle("is-active", select.selectedIndex > 0);
            }
        });
    }

    function syncResetVisibility() {
        if (!resetBtn) {
            return;
        }
        resetBtn.hidden = !hasActiveFilters();
    }

    function syncAll() {
        applyFilters();
        syncFieldStates();
        syncResetVisibility();
    }

    selects.forEach(function (select) {
        select.addEventListener("change", syncAll);
    });

    if (search) {
        search.addEventListener("input", syncAll);
    }

    if (resetBtn) {
        resetBtn.addEventListener("click", function () {
            if (search) {
                search.value = "";
            }
            selects.forEach(function (select) {
                select.selectedIndex = 0;
            });
            syncAll();
            if (search) {
                search.focus();
            }
        });
    }

    syncAll();
})();
