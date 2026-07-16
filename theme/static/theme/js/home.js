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

    var announcement = document.querySelector(".home-announce[data-slider]");
    initSlider(announcement, {
        slideSelector: "[data-slide]",
        dotBtnClass: "",
        autoplayMs: 3000,
    });

    document.querySelectorAll("[data-card-carousel]").forEach(function (root) {
        var track = root.querySelector("[data-carousel-track]");
        var prev = root.querySelector("[data-carousel-prev]");
        var next = root.querySelector("[data-carousel-next]");
        var controls = root.querySelector(".home-card-carousel__controls");
        if (!track || !prev || !next) return;

        function step(direction) {
            var card = track.querySelector("li");
            if (!card) return;
            track.scrollBy({ left: direction * (card.offsetWidth + 20), behavior: "smooth" });
        }
        prev.addEventListener("click", function () { step(-1); });
        next.addEventListener("click", function () { step(1); });

        function updateControls() {
            var count = track.querySelectorAll("li").length;
            controls.classList.toggle("is-hidden", window.innerWidth >= 768 && count <= 3);
        }
        window.addEventListener("resize", updateControls);
        updateControls();
    });

})();
