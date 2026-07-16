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
    var index = 0;
    var prevButton = root.querySelector("[data-product-gallery-prev]");
    var nextButton = root.querySelector("[data-product-gallery-next]");

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

    function visibleCount() {
        if (!slides[0]) return 1;
        return Math.max(1, Math.round(root.clientWidth / slides[0].getBoundingClientRect().width));
    }

    function update(animate) {
        var maxIndex = Math.max(0, originalCount - visibleCount());
        index = Math.min(index, maxIndex);
        track.style.transition = animate === false ? "none" : "transform 0.4s ease";
        track.style.transform = "translateX(" + -index * slideStep() + "px)";
        var hasOverflow = maxIndex > 0;
        if (prevButton) {
            prevButton.hidden = !hasOverflow;
            prevButton.disabled = index === 0;
        }
        if (nextButton) {
            nextButton.hidden = !hasOverflow;
            nextButton.disabled = index === maxIndex;
        }
    }

    function next() {
        index = Math.min(index + 1, Math.max(0, originalCount - visibleCount()));
        update(true);
    }

    function previous() {
        index = Math.max(0, index - 1);
        update(true);
    }

    if (prevButton) prevButton.addEventListener("click", previous);
    if (nextButton) nextButton.addEventListener("click", next);

    window.addEventListener("resize", function () {
        update(false);
    });

    update(false);
})();
