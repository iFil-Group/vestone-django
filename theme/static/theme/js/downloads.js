(function () {
    "use strict";

    var root = document.querySelector("[data-downloads]");
    if (!root) {
        return;
    }

    var searchInput = root.querySelector("[data-downloads-search]");
    var categoryButtons = root.querySelectorAll("[data-downloads-category]");
    var groups = root.querySelectorAll("[data-downloads-group]");
    var items = root.querySelectorAll("[data-download-item]");
    var emptyState = root.querySelector("[data-downloads-empty]");
    var activeCategory = "all";

    function normalize(value) {
        return (value || "").toLowerCase().trim();
    }

    function applyFilters() {
        var query = normalize(searchInput ? searchInput.value : "");
        var visibleCount = 0;

        groups.forEach(function (group) {
            var groupId = group.getAttribute("data-downloads-group");
            var groupItems = group.querySelectorAll("[data-download-item]");
            var groupVisible = 0;

            groupItems.forEach(function (item) {
                var matchCategory =
                    activeCategory === "all" ||
                    item.getAttribute("data-category") === activeCategory;
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
                (activeCategory === "all" || activeCategory === groupId) &&
                groupVisible > 0;
            group.hidden = !showGroup;
        });

        if (emptyState) {
            emptyState.hidden = visibleCount > 0;
        }
    }

    categoryButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            activeCategory = button.getAttribute("data-downloads-category");

            categoryButtons.forEach(function (btn) {
                var isActive = btn === button;
                btn.classList.toggle("is-active", isActive);
                btn.setAttribute("aria-selected", isActive ? "true" : "false");
            });

            applyFilters();
        });
    });

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }

    applyFilters();
})();
