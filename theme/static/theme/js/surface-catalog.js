(function () {
    "use strict";

    var root = document.querySelector("[data-surface-catalog]");
    if (!root) return;

    var searchInput = root.querySelector("[data-surface-search]");
    var filtersForm = root.querySelector("[data-surface-filters]");
    var resetButton = root.querySelector("[data-surface-reset]");
    var emptyMsg = root.querySelector("[data-surface-empty]");
    var groups = Array.prototype.slice.call(root.querySelectorAll("[data-surface-group]"));

    function normalize(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    function activeFilters() {
        var filters = {};
        if (!filtersForm) return filters;
        filtersForm.querySelectorAll("[data-surface-filter]").forEach(function (select) {
            var key = select.getAttribute("data-surface-filter");
            var value = (select.value || "").trim();
            if (key && value) {
                filters[key] = normalize(value);
            }
        });
        return filters;
    }

    function itemMatchesFilters(item, filters) {
        var keys = Object.keys(filters);
        if (!keys.length) return true;
        return keys.every(function (key) {
            var suffix = key.replace(/^filter_/, "").replace(/_/g, "-");
            var attr = "data-filter-" + suffix;
            return normalize(item.getAttribute(attr)) === filters[key];
        });
    }

    function applyFilter() {
        var query = normalize(searchInput ? searchInput.value : "");
        var filters = activeFilters();
        var anyVisible = false;

        groups.forEach(function (group) {
            var items = Array.prototype.slice.call(group.querySelectorAll("[data-surface-item]"));
            var groupVisible = false;

            items.forEach(function (item) {
                var haystack = normalize(item.getAttribute("data-search"));
                var matchSearch = !query || haystack.indexOf(query) !== -1;
                var matchFilters = itemMatchesFilters(item, filters);
                var match = matchSearch && matchFilters;
                item.hidden = !match;
                if (match) groupVisible = true;
            });

            group.hidden = !groupVisible;
            if (groupVisible) anyVisible = true;
        });

        if (emptyMsg) {
            emptyMsg.hidden = anyVisible;
        }
        if (resetButton) {
            resetButton.hidden = !query && !Object.keys(filters).length;
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilter);
        searchInput.addEventListener("search", applyFilter);
    }

    if (filtersForm) {
        filtersForm.querySelectorAll("[data-surface-filter]").forEach(function (select) {
            select.addEventListener("change", applyFilter);
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", function () {
            if (searchInput) searchInput.value = "";
            if (filtersForm) {
                filtersForm.querySelectorAll("[data-surface-filter]").forEach(function (select) {
                    select.selectedIndex = 0;
                });
            }
            applyFilter();
        });
    }

    applyFilter();
})();
