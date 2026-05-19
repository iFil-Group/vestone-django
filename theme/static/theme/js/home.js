(function () {
    "use strict";

    function initSlider(root, options) {
        if (!root) {
            return;
        }

        var slides = Array.prototype.slice.call(root.querySelectorAll(options.slideSelector));
        var dotsContainer = root.querySelector("[data-slider-dots]");
        var prevBtn = root.querySelector("[data-slider-prev]");
        var nextBtn = root.querySelector("[data-slider-next]");
        var current = 0;
        var timer = null;
        var autoplayMs = options.autoplayMs || 0;
        var dotClass = options.dotClass || "is-active";

        function goTo(index) {
            if (!slides.length) {
                return;
            }

            current = (index + slides.length) % slides.length;

            slides.forEach(function (slide, i) {
                slide.classList.toggle("is-active", i === current);
            });

            if (dotsContainer) {
                var dots = dotsContainer.querySelectorAll("button");
                dots.forEach(function (dot, i) {
                    dot.classList.toggle(dotClass, i === current);
                    dot.setAttribute("aria-selected", i === current ? "true" : "false");
                });
            }
        }

        function next() {
            goTo(current + 1);
        }

        function prev() {
            goTo(current - 1);
        }

        function resetAutoplay() {
            if (!autoplayMs) {
                return;
            }
            if (timer) {
                clearInterval(timer);
            }
            timer = setInterval(next, autoplayMs);
        }

        if (dotsContainer) {
            slides.forEach(function (_, i) {
                var dot = document.createElement("button");
                dot.type = "button";
                dot.className = options.dotBtnClass + (i === 0 ? " " + dotClass : "");
                dot.setAttribute("role", "tab");
                dot.setAttribute("aria-label", (options.dotLabel || "Slajd") + " " + (i + 1));
                dot.setAttribute("aria-selected", i === 0 ? "true" : "false");
                dot.addEventListener("click", function () {
                    goTo(i);
                    resetAutoplay();
                });
                dotsContainer.appendChild(dot);
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", function () {
                prev();
                resetAutoplay();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", function () {
                next();
                resetAutoplay();
            });
        }

        if (autoplayMs) {
            root.addEventListener("mouseenter", function () {
                if (timer) {
                    clearInterval(timer);
                }
            });
            root.addEventListener("mouseleave", resetAutoplay);
            resetAutoplay();
        }
    }

    var hero = document.querySelector(".home-hero[data-slider]");
    initSlider(hero, {
        slideSelector: "[data-slide]",
        dotBtnClass: "home-hero__dot",
        dotLabel: "Slajd",
        autoplayMs: 7000,
    });

    var reviews = document.querySelector(".home-reviews[data-slider]");
    initSlider(reviews, {
        slideSelector: "[data-slide]",
        dotBtnClass: "home-reviews__dot",
        dotLabel: "Opinia",
        autoplayMs: 6000,
    });
})();
