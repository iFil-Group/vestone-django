(function () {
    "use strict";
    document.querySelectorAll("[data-article-gallery]").forEach(function (root) {
        var track = root.querySelector("[data-article-gallery-track]");
        var prev = root.querySelector("[data-article-prev]");
        var next = root.querySelector("[data-article-next]");
        if (!track || !prev || !next) return;
        function move(direction) {
            var slide = track.querySelector(".article-gallery__slide");
            if (slide) track.scrollBy({ left: direction * (slide.offsetWidth + 16), behavior: "smooth" });
        }
        prev.addEventListener("click", function () { move(-1); });
        next.addEventListener("click", function () { move(1); });
        var overflow = track.children.length > 1;
        prev.hidden = !overflow;
        next.hidden = !overflow;
    });
})();
