(function () {
    "use strict";

    var DEFAULT_DURATION = 2500;

    function dismissToast(toast, timerId) {
        if (toast.classList.contains("is-leaving")) {
            return;
        }

        if (timerId) {
            window.clearTimeout(timerId);
        }

        toast.classList.add("is-leaving");

        window.setTimeout(function () {
            toast.remove();
        }, 220);
    }

    function bindToast(toast) {
        var duration = parseInt(toast.getAttribute("data-duration"), 10) || DEFAULT_DURATION;
        var progress = toast.querySelector(".cms-toast__progress");
        var closeButton = toast.querySelector("[data-cms-toast-close]");
        var timerId = null;

        if (progress) {
            progress.style.animationDuration = duration + "ms";
        }

        timerId = window.setTimeout(function () {
            dismissToast(toast, timerId);
        }, duration);

        if (closeButton) {
            closeButton.addEventListener("click", function () {
                dismissToast(toast, timerId);
            });
        }
    }

    document.querySelectorAll("[data-cms-toast]").forEach(bindToast);
})();
