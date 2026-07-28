(function () {
    "use strict";

    var form = document.getElementById("product-form");
    if (!form) return;

    var switchRoot = form.querySelector("[data-card-type-switch]");
    if (!switchRoot) return;

    function currentType() {
        var checked = switchRoot.querySelector('input[type="radio"]:checked');
        return checked ? checked.value : "standard";
    }

    function sync() {
        var type = currentType();
        form.setAttribute("data-product-card-type", type);
        form.querySelectorAll("[data-standard-only]").forEach(function (node) {
            // Prefer attribute-only hide to avoid WebKit blank-page bugs with display toggles.
            node.hidden = type === "descriptive";
            node.classList.remove("is-hidden");
        });
        switchRoot.querySelectorAll(".cms-card-type__option").forEach(function (option) {
            var input = option.querySelector('input[type="radio"]');
            option.classList.toggle("is-selected", !!(input && input.checked));
        });
    }

    switchRoot.querySelectorAll('input[type="radio"]').forEach(function (input) {
        input.addEventListener("change", sync);
    });
    sync();
})();
