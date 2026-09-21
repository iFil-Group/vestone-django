(function () {
    "use strict";

    function setCollapsed(card, collapsed) {
        var toggle = card.querySelector("[data-cms-collapse-toggle]");
        var title = card.querySelector(".cms-card__title");
        var label = title ? title.textContent.trim() : "sekcję";

        card.classList.toggle("is-collapsed", collapsed);
        if (toggle) {
            toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
            toggle.setAttribute("aria-label", (collapsed ? "Rozwiń: " : "Zwiń: ") + label);
        }
        if (!collapsed && typeof window.cmsRefreshPinEditors === "function") {
            window.setTimeout(function () {
                window.cmsRefreshPinEditors();
            }, 0);
        }
    }

    function cardHasErrors(card) {
        return Boolean(card.querySelector(".cms-field__error, .cms-form-errors, .cms-pin-row--error"));
    }

    function cardHasMedia(card) {
        return Boolean(
            card.querySelector(
                ".cms-file--has-file, [data-cms-file-existing-preview], [data-gallery-tile], [data-packshot-tile], [data-color-tile]"
            )
        );
    }

    function initCard(card) {
        if (card.dataset.cmsCollapseReady === "1") {
            return;
        }
        card.dataset.cmsCollapseReady = "1";

        var head = card.querySelector(".cms-card__head--collapsible");
        if (!head) {
            return;
        }

        var wantsCollapsed = card.classList.contains("is-collapsed");
        setCollapsed(card, wantsCollapsed && !cardHasErrors(card) && !cardHasMedia(card));

        head.addEventListener("click", function (event) {
            if (event.target.closest("a, input, select, textarea, label")) {
                return;
            }
            event.preventDefault();
            setCollapsed(card, !card.classList.contains("is-collapsed"));
        });
    }

    function init(root) {
        (root || document).querySelectorAll(".cms-product-form .cms-card").forEach(initCard);
    }

    var form = document.getElementById("product-form");
    if (form) {
        form.addEventListener(
            "submit",
            function () {
                form.querySelectorAll(".cms-card.is-collapsed").forEach(function (card) {
                    setCollapsed(card, false);
                });
            },
            true
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            init();
        });
    } else {
        init();
    }
})();
