(function () {
    "use strict";

    var THREE_DAYS = 3 * 24 * 60 * 60 * 1000;
    var THREE_DAYS_SEC = 3 * 24 * 60 * 60;

    function storageKey(kind, id) {
        return "vestone-promo-" + kind + "-" + (id || "0");
    }

    function cookieName(kind, id) {
        return "vestone_promo_" + kind + "_" + (id || "0");
    }

    function readCookie(name) {
        var parts = ("; " + document.cookie).split("; " + name + "=");
        if (parts.length < 2) return "";
        return parts.pop().split(";").shift();
    }

    function wasSeenRecently(kind, id) {
        try {
            var raw = window.localStorage.getItem(storageKey(kind, id));
            if (raw) {
                var seen = parseInt(raw, 10);
                if (!isNaN(seen) && Date.now() - seen < THREE_DAYS) return true;
            }
        } catch (err) {
            /* ignore */
        }
        var cookie = readCookie(cookieName(kind, id));
        if (!cookie) return false;
        var cookieSeen = parseInt(cookie, 10);
        return !isNaN(cookieSeen) && Date.now() - cookieSeen < THREE_DAYS;
    }

    function markSeen(kind, id) {
        var now = String(Date.now());
        try {
            window.localStorage.setItem(storageKey(kind, id), now);
        } catch (err) {
            /* ignore */
        }
        document.cookie = cookieName(kind, id) + "=" + now +
            "; max-age=" + THREE_DAYS_SEC + "; path=/; SameSite=Lax";
    }

    var bar = document.querySelector("[data-promo-bar]");
    if (bar) {
        var lines = bar.querySelectorAll("[data-promo-line]");
        var lineIndex = 0;
        if (lines.length > 1) {
            window.setInterval(function () {
                lines[lineIndex].classList.remove("is-active");
                lineIndex = (lineIndex + 1) % lines.length;
                lines[lineIndex].classList.add("is-active");
            }, 3500);
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
            markSeen("modal", id);
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
        window.setTimeout(function () {
            widget.classList.add("is-visible");
            markSeen("side", id);
        }, 400);
        window.setTimeout(function () {
            widget.classList.remove("is-visible");
            widget.classList.add("is-hiding");
        }, 10400);
    });
})();
