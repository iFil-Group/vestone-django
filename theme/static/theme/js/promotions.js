(function () {
    "use strict";

    var THREE_DAYS = 3 * 24 * 60 * 60 * 1000;

    function storageKey(kind, id) {
        return "vestone-promo-" + kind + "-" + (id || "0");
    }

    function wasSeenRecently(kind, id) {
        try {
            var raw = window.localStorage.getItem(storageKey(kind, id));
            if (!raw) return false;
            var seen = parseInt(raw, 10);
            if (isNaN(seen)) return false;
            return Date.now() - seen < THREE_DAYS;
        } catch (err) {
            return false;
        }
    }

    function markSeen(kind, id) {
        try {
            window.localStorage.setItem(storageKey(kind, id), String(Date.now()));
        } catch (err) {
            /* ignore */
        }
    }

    document.querySelectorAll("[data-promo-modal]").forEach(function (dialog) {
        var id = dialog.getAttribute("data-promo-id") || "0";
        var close = dialog.querySelector("[data-promo-close]");
        if (wasSeenRecently("modal", id)) {
            return;
        }
        window.setTimeout(function () {
            if (typeof dialog.showModal === "function") dialog.showModal();
            else dialog.setAttribute("open", "");
        }, 2000);
        if (close) {
            close.addEventListener("click", function () {
                markSeen("modal", id);
                if (typeof dialog.close === "function") dialog.close();
                else dialog.removeAttribute("open");
            });
        }
        dialog.addEventListener("cancel", function () {
            markSeen("modal", id);
        });
    });

    document.querySelectorAll("[data-promo-side]").forEach(function (widget) {
        var id = widget.getAttribute("data-promo-id") || "0";
        if (wasSeenRecently("side", id)) {
            return;
        }
        widget.hidden = false;
        window.requestAnimationFrame(function () {
            widget.classList.add("is-visible");
        });
        window.setTimeout(function () {
            widget.classList.remove("is-visible");
            widget.classList.add("is-hiding");
            markSeen("side", id);
        }, 8000);
    });
})();
