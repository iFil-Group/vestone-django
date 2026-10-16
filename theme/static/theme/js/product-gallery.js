(function () {
    "use strict";

    function initCarousel(root, options) {
        var track = root.querySelector(options.trackSelector);
        if (!track) {
            return;
        }

        var slides = Array.prototype.slice.call(
            track.querySelectorAll(options.slideSelector)
        );
        var originalCount = slides.length;
        var index = 0;
        var prevButton = root.querySelector(options.prevSelector);
        var nextButton = root.querySelector(options.nextSelector);

        function perView() {
            return options.perView();
        }

        function getGap() {
            var styles = window.getComputedStyle(track);
            return parseFloat(styles.columnGap || styles.gap) || 16;
        }

        function slideStep() {
            var first = track.querySelector(options.slideSelector);
            if (!first) {
                return 0;
            }
            return first.getBoundingClientRect().width + getGap();
        }

        function updateSlideStates() {
            if (!options.markActive) {
                return;
            }
            var count = perView();
            slides.forEach(function (slide, slideIndex) {
                slide.classList.toggle(
                    "is-active",
                    slideIndex >= index && slideIndex < index + count
                );
            });
        }

        function update(animate) {
            var count = perView();
            var maxIndex = Math.max(0, originalCount - count);
            index = Math.min(Math.max(0, index), maxIndex);
            track.style.transition = animate === false ? "none" : "transform 0.45s ease";
            track.style.transform = "translateX(" + -index * slideStep() + "px)";
            updateSlideStates();
            var hasOverflow = maxIndex > 0;
            if (prevButton) {
                prevButton.hidden = !hasOverflow;
                prevButton.disabled = !hasOverflow || index === 0;
                prevButton.setAttribute("aria-hidden", hasOverflow ? "false" : "true");
            }
            if (nextButton) {
                nextButton.hidden = !hasOverflow;
                nextButton.disabled = !hasOverflow || index === maxIndex;
                nextButton.setAttribute("aria-hidden", hasOverflow ? "false" : "true");
            }
        }

        function next() {
            if (nextButton && nextButton.disabled) return;
            index = Math.min(index + 1, Math.max(0, originalCount - perView()));
            update(true);
        }

        function previous() {
            if (prevButton && prevButton.disabled) return;
            index = Math.max(0, index - 1);
            update(true);
        }

        if (prevButton) prevButton.addEventListener("click", previous);
        if (nextButton) nextButton.addEventListener("click", next);

        window.addEventListener("resize", function () {
            update(false);
        });

        slides.forEach(function (slide) {
            var img = slide.querySelector("img");
            if (img && !img.complete) {
                img.addEventListener("load", function () {
                    update(false);
                });
            }
        });

        update(false);
        window.requestAnimationFrame(function () {
            update(false);
        });
    }

    document.querySelectorAll("[data-product-gallery]").forEach(function (root) {
        initCarousel(root, {
            trackSelector: "[data-product-gallery-track]",
            slideSelector: ".product-gallery__slide",
            prevSelector: "[data-product-gallery-prev]",
            nextSelector: "[data-product-gallery-next]",
            markActive: true,
            perView: function () {
                return window.innerWidth < 768 ? 1 : 2;
            },
        });
    });

    document.querySelectorAll("[data-product-packshot]").forEach(function (root) {
        initCarousel(root, {
            trackSelector: "[data-product-packshot-track]",
            slideSelector: ".product-packshot-strip__item",
            prevSelector: "[data-product-packshot-prev]",
            nextSelector: "[data-product-packshot-next]",
            markActive: false,
            perView: function () {
                if (window.innerWidth < 640) {
                    return 2;
                }
                if (window.innerWidth < 1024) {
                    return 3;
                }
                return 4;
            },
        });
    });
})();
