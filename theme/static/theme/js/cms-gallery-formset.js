(function () {
    "use strict";
    var root = document.querySelector("[data-gallery-formset]");
    if (!root) return;
    var rows = root.querySelector("[data-gallery-rows]");
    var template = root.querySelector("[data-gallery-template]");
    var add = root.querySelector("[data-gallery-add]");
    var total = document.getElementById("id_gallery-TOTAL_FORMS");
    if (!rows || !template || !add || !total) return;

    add.addEventListener("click", function () {
        var index = parseInt(total.value, 10);
        var html = template.innerHTML.replace(/__prefix__/g, String(index));
        rows.insertAdjacentHTML("beforeend", html);
        total.value = String(index + 1);
        var row = rows.lastElementChild;
        row.querySelectorAll("[data-cms-file]").forEach(function (field) {
            if (window.cmsBindFileField) window.cmsBindFileField(field);
        });
        if (window.cmsBindFormsetRow) window.cmsBindFormsetRow(row);
    });
})();
