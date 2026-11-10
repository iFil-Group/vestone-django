(function () {
    "use strict";

    var catalog = document.querySelector("[data-surface-catalog]");
    if (catalog) {
        var search = catalog.querySelector("[data-surface-search]");
        var items = Array.prototype.slice.call(catalog.querySelectorAll("[data-surface-color]"));
        var empty = catalog.querySelector("[data-surface-empty]");

        function apply() {
            var query = search ? search.value.trim().toLowerCase() : "";
            var visible = 0;
            items.forEach(function (item) {
                var haystack = item.getAttribute("data-search") || "";
                var show = !query || haystack.indexOf(query) !== -1;
                item.hidden = !show;
                if (show) {
                    visible += 1;
                }
            });
            if (empty) {
                empty.hidden = visible > 0;
            }
        }

        if (search) {
            search.addEventListener("input", apply);
        }
        apply();
    }

    var zoomRoot = document.querySelector("[data-surface-zoom]");
    if (!zoomRoot) {
        return;
    }

    var lightbox = zoomRoot.querySelector("[data-surface-lightbox]");
    var lightboxImage = zoomRoot.querySelector("[data-surface-lightbox-image]");
    var tiles = Array.prototype.slice.call(zoomRoot.querySelectorAll("[data-surface-zoom-item]"));

    function closeLightbox() {
        if (lightbox && lightbox.open) {
            lightbox.close();
        }
    }

    function openLightbox(src, alt) {
        if (!lightbox || !lightboxImage) {
            return;
        }
        lightboxImage.src = src;
        lightboxImage.alt = alt || "";
        if (typeof lightbox.showModal === "function") {
            lightbox.showModal();
        }
    }

    tiles.forEach(function (tile) {
        var button = tile.querySelector("[data-surface-zoom-open]");
        if (!button) {
            return;
        }
        button.addEventListener("click", function () {
            if (tile.classList.contains("is-featured")) {
                openLightbox(
                    button.getAttribute("data-zoom-src"),
                    button.getAttribute("data-zoom-alt")
                );
                return;
            }
            tiles.forEach(function (other) {
                other.classList.toggle("is-featured", other === tile);
            });
        });
    });

    zoomRoot.querySelectorAll("[data-surface-lightbox-close]").forEach(function (button) {
        button.addEventListener("click", closeLightbox);
    });
    if (lightbox) {
        lightbox.addEventListener("click", function (event) {
            if (event.target === lightbox) {
                closeLightbox();
            }
        });
    }
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeLightbox();
        }
    });
})();
