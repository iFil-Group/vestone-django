(function () {
    "use strict";
    var select = document.querySelector("[data-surface-sort]");
    var list = document.querySelector("[data-product-results]");
    if (!select || !list) return;

    var original = Array.prototype.slice.call(list.children);
    select.addEventListener("change", function () {
        var key = select.value;
        var items = original.slice();
        if (key) {
            items.sort(function (a, b) {
                var aValue = a.getAttribute("data-filter-" + key) || "";
                var bValue = b.getAttribute("data-filter-" + key) || "";
                return aValue.localeCompare(bValue, "pl", { numeric: true, sensitivity: "base" });
            });
        }
        items.forEach(function (item) { list.appendChild(item); });
    });
})();
