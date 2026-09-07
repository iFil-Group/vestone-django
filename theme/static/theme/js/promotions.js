(function () {
    "use strict";

    var THREE_DAYS = 3 * 24 * 60 * 60 * 1000;
    var THREE_DAYS_SEC = 3 * 24 * 60 * 60;

    function storageKey(kind, id, reset) {
        return "vestone-promo-" + kind + "-" + (id || "0") + "-" + (reset || "0");
    }

    function cookieName(kind, id, reset) {
        return "vestone_promo_" + kind + "_" + (id || "0") + "_" + (reset || "0");
    }

    function readCookie(name) {
        var parts = ("; " + document.cookie).split("; " + name + "=");
        if (parts.length < 2) return "";
        return parts.pop().split(";").shift();
    }

    function wasSeenRecently(kind, id, reset) {
        try {
            var raw = window.localStorage.getItem(storageKey(kind, id, reset));
            if (raw) {
                var seen = parseInt(raw, 10);
                if (!isNaN(seen) && Date.now() - seen < THREE_DAYS) return true;
            }
        } catch (err) {
            /* ignore */
        }
        var cookie = readCookie(cookieName(kind, id, reset));
        if (!cookie) return false;
        var cookieSeen = parseInt(cookie, 10);
        return !isNaN(cookieSeen) && Date.now() - cookieSeen < THREE_DAYS;
    }

    function markSeen(kind, id, reset) {
        var now = String(Date.now());
        try {
            window.localStorage.setItem(storageKey(kind, id, reset), now);
        } catch (err) {
            /* ignore */
        }
        document.cookie = cookieName(kind, id, reset) + "=" + now +
            "; max-age=" + THREE_DAYS_SEC + "; path=/; SameSite=Lax";
    }

    var bar = document.querySelector("[data-promo-bar]");
    if (bar) {
        var lines = Array.prototype.slice.call(bar.querySelectorAll("[data-promo-line]"));
        var lineIndex = 0;
        var animating = false;

        function resetSlide(slide) {
            slide.classList.add("is-reset");
            slide.classList.remove("is-leaving", "is-active");
            void slide.offsetWidth;
            slide.classList.remove("is-reset");
        }

        function goTo(nextIndex) {
            if (animating || nextIndex === lineIndex) return;
            animating = true;
            var outgoing = lines[lineIndex];
            var incoming = lines[nextIndex];
            resetSlide(incoming);
            outgoing.classList.remove("is-active");
            outgoing.classList.add("is-leaving");
            incoming.classList.add("is-active");
            lineIndex = nextIndex;
            window.setTimeout(function () {
                resetSlide(outgoing);
                animating = false;
            }, 820);
        }

        if (lines.length > 1) {
            window.setInterval(function () {
                goTo((lineIndex + 1) % lines.length);
            }, 3800);
        }
    }

    document.querySelectorAll("[data-promo-modal]").forEach(function (dialog) {
        var id = dialog.getAttribute("data-promo-id") || "0";
        var reset = dialog.getAttribute("data-promo-reset") || "0";
        var close = dialog.querySelector("[data-promo-close]");
        if (wasSeenRecently("modal", id, reset)) {
            return;
        }
        window.setTimeout(function () {
            if (typeof dialog.showModal === "function") dialog.showModal();
            else dialog.setAttribute("open", "");
            markSeen("modal", id, reset);
        }, 2000);
        if (close) {
            close.addEventListener("click", function () {
                markSeen("modal", id, reset);
                if (typeof dialog.close === "function") dialog.close();
                else dialog.removeAttribute("open");
            });
        }
        dialog.addEventListener("cancel", function () {
            markSeen("modal", id, reset);
        });
    });

    document.querySelectorAll("[data-promo-side]").forEach(function (widget) {
        var id = widget.getAttribute("data-promo-id") || "0";
        var reset = widget.getAttribute("data-promo-reset") || "0";
        if (wasSeenRecently("side", id, reset)) {
            return;
        }
        widget.hidden = false;
        window.setTimeout(function () {
            widget.classList.add("is-visible");
            markSeen("side", id, reset);
        }, 400);
        window.setTimeout(function () {
            widget.classList.remove("is-visible");
            widget.classList.add("is-hiding");
        }, 10400);
    });
})();
