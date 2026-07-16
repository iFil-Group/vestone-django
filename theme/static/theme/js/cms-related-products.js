(function () {
    "use strict";
    var root = document.querySelector("[data-related-products]");
    if (!root) return;

    var input = root.querySelector("[data-related-search]");
    var results = root.querySelector("[data-related-results]");
    var selected = root.querySelector("[data-related-selected]");
    var timer = null;

    function selectedIds() {
        return Array.prototype.map.call(
            selected.querySelectorAll('input[name="related_products"]'),
            function (item) { return item.value; }
        );
    }

    function addProduct(item) {
        if (selectedIds().indexOf(String(item.id)) !== -1) return;
        var chip = document.createElement("span");
        chip.className = "cms-related-chip";
        chip.dataset.productId = item.id;
        chip.appendChild(document.createTextNode(item.text + " "));
        var button = document.createElement("button");
        button.type = "button";
        button.dataset.relatedRemove = "";
        button.setAttribute("aria-label", "Usuń");
        button.textContent = "×";
        var hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "related_products";
        hidden.value = item.id;
        chip.appendChild(button);
        chip.appendChild(hidden);
        selected.appendChild(chip);
        results.innerHTML = "";
        input.value = "";
    }

    function search() {
        var query = input.value.trim();
        if (query.length < 2) {
            results.innerHTML = "";
            return;
        }
        var url = root.dataset.searchUrl + "?q=" + encodeURIComponent(query);
        if (root.dataset.productId) url += "&exclude=" + root.dataset.productId;
        fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                results.innerHTML = "";
                data.results.forEach(function (item) {
                    if (selectedIds().indexOf(String(item.id)) !== -1) return;
                    var button = document.createElement("button");
                    button.type = "button";
                    button.textContent = item.text;
                    button.addEventListener("click", function () { addProduct(item); });
                    results.appendChild(button);
                });
            });
    }

    input.addEventListener("input", function () {
        window.clearTimeout(timer);
        timer = window.setTimeout(search, 250);
    });
    selected.addEventListener("click", function (event) {
        var button = event.target.closest("[data-related-remove]");
        if (button) button.closest(".cms-related-chip").remove();
    });
})();
