(function () {
    "use strict";

    var root = document.querySelector("[data-media-library]");
    if (!root) {
        return;
    }

    var search = root.querySelector("[data-media-search]");
    var cards = Array.prototype.slice.call(root.querySelectorAll("[data-media-card]"));

    function applySearch() {
        var query = search ? search.value.trim().toLowerCase() : "";
        cards.forEach(function (card) {
            if (card.classList.contains("is-removed")) {
                return;
            }
            var haystack = (card.getAttribute("data-media-name") || "").toLowerCase();
            card.hidden = Boolean(query) && haystack.indexOf(query) === -1;
        });
    }

    if (search) {
        search.addEventListener("input", applySearch);
    }

    root.querySelectorAll("[data-media-delete]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            if (!window.confirm("Usunąć ten plik z serwera?")) {
                return;
            }
            var body = new FormData(form);
            fetch(form.action || window.location.href, {
                method: "POST",
                body: body,
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin",
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("delete failed");
                    }
                    var card = form.closest("[data-media-card]");
                    if (card) {
                        card.classList.add("is-removed");
                        card.hidden = true;
                    }
                })
                .catch(function () {
                    window.alert("Nie udało się usunąć pliku. Odśwież stronę i spróbuj ponownie.");
                });
        });
    });
})();
