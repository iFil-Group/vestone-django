(function () {
    "use strict";

    var root = document.querySelector("[data-downloads]");
    if (!root) {
        return;
    }

    var searchInput = root.querySelector("[data-downloads-search]");
    var categorySelect = root.querySelector("[data-downloads-categories]");
    var groups = root.querySelectorAll("[data-downloads-group]");
    var emptyState = root.querySelector("[data-downloads-empty]");

    function normalize(value) {
        return (value || "").toLowerCase().trim();
    }

    function selectedCategories() {
        if (!categorySelect) {
            return [];
        }
        return Array.prototype.slice
            .call(categorySelect.selectedOptions)
            .map(function (option) {
                return option.value;
            });
    }

    function applyFilters() {
        var query = normalize(searchInput ? searchInput.value : "");
        var categories = selectedCategories();
        var filterByCategory = categories.length > 0;
        var visibleCount = 0;

        groups.forEach(function (group) {
            var groupId = group.getAttribute("data-downloads-group");
            var groupItems = group.querySelectorAll("[data-download-item]");
            var groupVisible = 0;

            groupItems.forEach(function (item) {
                var itemCategory = item.getAttribute("data-category");
                var matchCategory =
                    !filterByCategory || categories.indexOf(itemCategory) !== -1;
                var searchData = normalize(item.getAttribute("data-search"));
                var matchSearch = !query || searchData.indexOf(query) !== -1;
                var visible = matchCategory && matchSearch;

                item.hidden = !visible;
                if (visible) {
                    groupVisible += 1;
                    visibleCount += 1;
                }
            });

            var showGroup =
                (!filterByCategory || categories.indexOf(groupId) !== -1) && groupVisible > 0;
            group.hidden = !showGroup;
        });

        if (emptyState) {
            emptyState.hidden = visibleCount > 0;
        }
    }

    if (categorySelect) {
        categorySelect.addEventListener("change", applyFilters);
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }

    applyFilters();
})();
