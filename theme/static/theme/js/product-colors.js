(function () {
    "use strict";

    function jumpToColor(id) {
        var target = document.getElementById(id);
        if (!target) {
            return;
        }
        document.querySelectorAll(".product-colors__item.is-target").forEach(function (item) {
            item.classList.remove("is-target");
        });
        target.classList.add("is-target");
        target.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    document.querySelectorAll("[data-color-jump]").forEach(function (link) {
        var id = link.getAttribute("data-color-jump");
        link.addEventListener("mouseenter", function () {
            jumpToColor(id);
        });
        link.addEventListener("click", function (event) {
            event.preventDefault();
            jumpToColor(id);
        });
    });
})();
