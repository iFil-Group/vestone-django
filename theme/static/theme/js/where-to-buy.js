(function () {
    "use strict";

    var root = document.querySelector("[data-where-buy]");
    if (!root) return;

    var form = root.querySelector("[data-where-filters]");
    var list = root.querySelector("[data-where-list]");
    var empty = root.querySelector("[data-where-empty]");
    var mapEl = root.querySelector("[data-where-map]");
    if (!form || !list || !mapEl) return;

    var points = Array.prototype.slice.call(root.querySelectorAll("[data-where-point]"));
    var search = form.querySelector("[data-where-search]");
    var reset = root.querySelector("[data-where-reset]");
    var selects = form.querySelectorAll("[data-where-filter]");
    var markers = [];
    var map = null;
    if (typeof window.L !== "undefined") {
        map = window.L.map(mapEl, { scrollWheelZoom: false }).setView([52.0, 19.2], 6);
        window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 18,
            attribution: "&copy; OpenStreetMap",
        }).addTo(map);
    }

    function filters() {
        return {
            offer: (form.querySelector('[data-where-filter="offer"]') || {}).value || "",
            voivodeship: (form.querySelector('[data-where-filter="voivodeship"]') || {}).value || "",
            city: (form.querySelector('[data-where-filter="city"]') || {}).value || "",
            query: ((search && search.value) || "").toLowerCase().trim(),
        };
    }

    function matches(point, current) {
        if (current.offer && point.getAttribute("data-offer") !== current.offer) return false;
        if (current.voivodeship && point.getAttribute("data-voivodeship") !== current.voivodeship) {
            return false;
        }
        if (current.city && point.getAttribute("data-city") !== current.city) return false;
        if (current.query) {
            var haystack = (point.getAttribute("data-search") || point.getAttribute("data-name") || "").toLowerCase();
            if (haystack.indexOf(current.query) === -1) return false;
        }
        return true;
    }

    function hasActiveFilters() {
        var current = filters();
        return Boolean(current.offer || current.voivodeship || current.city || current.query);
    }

    function syncFieldStates() {
        Array.prototype.forEach.call(selects, function (select) {
            var field = select.closest(".product-filters__field");
            if (field) {
                field.classList.toggle("is-active", select.selectedIndex > 0);
            }
        });
        if (reset) {
            reset.hidden = !hasActiveFilters();
        }
    }

    function clearMarkers() {
        if (!map) return;
        markers.forEach(function (marker) {
            map.removeLayer(marker);
        });
        markers = [];
    }

    function pinIcon(url) {
        return window.L.icon({
            iconUrl: url,
            iconSize: [28, 36],
            iconAnchor: [14, 36],
            popupAnchor: [0, -30],
        });
    }

    function apply() {
        var current = filters();
        var visible = [];
        var bounds = [];

        clearMarkers();
        points.forEach(function (point) {
            var show = matches(point, current);
            point.hidden = !show;
            if (!show) return;
            visible.push(point);
            var lat = parseFloat(point.getAttribute("data-lat"));
            var lng = parseFloat(point.getAttribute("data-lng"));
            if (!map || isNaN(lat) || isNaN(lng)) return;
            var marker = window.L.marker([lat, lng], {
                icon: pinIcon(point.getAttribute("data-pin")),
                title: point.getAttribute("data-name") || "",
            }).addTo(map);
            marker.bindPopup(point.getAttribute("data-name") || "");
            marker.on("click", function () {
                point.scrollIntoView({ behavior: "smooth", block: "nearest" });
            });
            markers.push(marker);
            bounds.push([lat, lng]);
        });

        if (empty) empty.hidden = visible.length > 0;
        syncFieldStates();
        if (!map) return;
        if (bounds.length === 1) {
            map.setView(bounds[0], 12);
        } else if (bounds.length > 1) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
        } else {
            map.setView([52.0, 19.2], 6);
        }
        window.setTimeout(function () {
            map.invalidateSize();
        }, 200);
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        apply();
    });

    Array.prototype.forEach.call(selects, function (select) {
        select.addEventListener("change", apply);
    });

    if (search) {
        search.addEventListener("input", apply);
    }

    if (reset) {
        reset.addEventListener("click", function () {
            if (search) search.value = "";
            Array.prototype.forEach.call(selects, function (select) {
                select.selectedIndex = 0;
            });
            apply();
            if (search) search.focus();
        });
    }

    apply();
})();
