(function () {
    "use strict";

    var root = document.querySelector("[data-surface-catalog]");
    if (!root) return;

    var searchInput = root.querySelector("[data-surface-search]");
    var emptyMsg = root.querySelector("[data-surface-empty]");
    var groups = Array.prototype.slice.call(root.querySelectorAll("[data-surface-group]"));

    function normalize(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    function applyFilter() {
        var query = normalize(searchInput ? searchInput.value : "");
        var anyVisible = false;

        groups.forEach(function (group) {
            var items = Array.prototype.slice.call(group.querySelectorAll("[data-surface-item]"));
            var groupVisible = false;

            items.forEach(function (item) {
                var haystack = normalize(item.getAttribute("data-search"));
                var match = !query || haystack.indexOf(query) !== -1;
                item.hidden = !match;
                if (match) groupVisible = true;
            });

            group.hidden = !groupVisible;
            if (groupVisible) anyVisible = true;
        });

        if (emptyMsg) {
            emptyMsg.hidden = anyVisible;
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilter);
        searchInput.addEventListener("search", applyFilter);
    }

    applyFilter();
})();
