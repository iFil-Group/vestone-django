(function () {
    var root = document.querySelector("[data-product-filters]");
    if (!root) {
        return;
    }

    var search = root.querySelector("[data-product-search]");
    var resetBtn = root.querySelector("[data-product-filters-reset]");
    var selects = root.querySelectorAll("[data-product-filter]");

    function hasActiveFilters() {
        var searchActive = search && search.value.trim() !== "";
        var selectActive = Array.prototype.some.call(selects, function (select) {
            return select.selectedIndex > 0;
        });
        return searchActive || selectActive;
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
