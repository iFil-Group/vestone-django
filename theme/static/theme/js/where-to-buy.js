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
        };
    }

    function matches(point, current) {
        if (current.offer && point.getAttribute("data-offer") !== current.offer) return false;
        if (current.voivodeship && point.getAttribute("data-voivodeship") !== current.voivodeship) {
            return false;
        }
        if (current.city && point.getAttribute("data-city") !== current.city) return false;
        return true;
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

    var reset = root.querySelector("[data-where-reset]");
    if (reset) {
        reset.addEventListener("click", function () {
            window.setTimeout(apply, 0);
        });
    }

    apply();
})();
