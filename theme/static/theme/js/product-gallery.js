(function () {
    "use strict";

    var root = document.querySelector("[data-product-gallery]");
    if (!root) {
        return;
    }

    var track = root.querySelector("[data-product-gallery-track]");
    if (!track) {
        return;
    }

    var slides = Array.prototype.slice.call(
        track.querySelectorAll(".product-gallery__slide")
    );
    var originalCount = slides.length;
    if (originalCount < 4) {
        return;
    }

    slides.forEach(function (slide) {
        track.appendChild(slide.cloneNode(true));
    });

    var index = 0;
    var timer = null;
    var autoplayMs = 4200;

    function getGap() {
        var styles = window.getComputedStyle(track);
        return parseFloat(styles.columnGap || styles.gap) || 16;
    }

    function slideStep() {
        var first = track.querySelector(".product-gallery__slide");
        if (!first) {
            return 0;
        }
        return first.getBoundingClientRect().width + getGap();
    }

    function update(animate) {
        track.style.transition = animate === false ? "none" : "transform 0.55s ease";
        track.style.transform = "translateX(" + -index * slideStep() + "px)";
    }

    function next() {
        index += 1;
        update(true);

        if (index >= originalCount) {
            track.addEventListener(
                "transitionend",
                function onEnd() {
                    track.removeEventListener("transitionend", onEnd);
                    index = 0;
                    update(false);
                },
                { once: true }
            );
        }
    }

    function startAutoplay() {
        if (timer) {
            clearInterval(timer);
        }
        timer = setInterval(next, autoplayMs);
    }

    function stopAutoplay() {
        if (timer) {
            clearInterval(timer);
            timer = null;
        }
    }

    root.addEventListener("mouseenter", stopAutoplay);
    root.addEventListener("mouseleave", startAutoplay);

    window.addEventListener("resize", function () {
        update(false);
    });

    update(false);
    startAutoplay();
})();
