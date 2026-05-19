(function () {
    "use strict";

    var pins = document.querySelectorAll("[data-product-pin]");
    if (!pins.length) {
        return;
    }

    pins.forEach(function (pin) {
        pin.addEventListener("click", function (event) {
            event.preventDefault();
            var isActive = pin.classList.contains("is-active");
            pins.forEach(function (other) {
                other.classList.remove("is-active");
            });
            if (!isActive) {
                pin.classList.add("is-active");
            }
        });
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest("[data-product-pin]")) {
            pins.forEach(function (pin) {
                pin.classList.remove("is-active");
            });
        }
    });
})();
