(function () {
    "use strict";
    document.querySelectorAll("[data-promo-modal]").forEach(function (dialog) {
        var close = dialog.querySelector("[data-promo-close]");
        window.setTimeout(function () {
            if (typeof dialog.showModal === "function") dialog.showModal();
            else dialog.setAttribute("open", "");
        }, 2000);
        if (close) close.addEventListener("click", function () {
            if (typeof dialog.close === "function") dialog.close();
            else dialog.removeAttribute("open");
        });
    });
})();
