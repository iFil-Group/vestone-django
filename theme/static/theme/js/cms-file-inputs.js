(function () {
    "use strict";

    function bindFileField(wrapper) {
        var input = wrapper.querySelector(".cms-file__input");
        var nameEl = wrapper.querySelector("[data-cms-file-name]");
        var preview = wrapper.querySelector("[data-cms-file-preview]");
        var clearButton = wrapper.querySelector("[data-cms-file-clear]");
        var clearField = wrapper.querySelector("[data-cms-file-clear-field] input[type='checkbox']");
        var currentBlock = wrapper.querySelector("[data-cms-file-current]");

        if (input && nameEl) {
            input.addEventListener("change", function () {
                var file = input.files && input.files[0];
                if (!file) {
                    return;
                }

                nameEl.textContent = file.name;

                if (preview && file.type.indexOf("image/") === 0) {
                    var reader = new FileReader();
                    reader.onload = function (event) {
                        preview.src = event.target.result;
                        preview.hidden = false;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        if (clearButton && clearField) {
            clearButton.addEventListener("click", function () {
                var marked = clearField.checked;
                clearField.checked = !marked;
                clearButton.textContent = marked ? "Usuń plik" : "Przywróć plik";
                clearButton.classList.toggle("is-active", !marked);
                if (currentBlock) {
                    currentBlock.classList.toggle("is-marked-delete", !marked);
                }
            });
        }
    }

    function bindFormsetRow(row) {
        var deleteButton = row.querySelector("[data-cms-row-delete]");
        var deleteField = row.querySelector("[data-cms-delete-field] input[type='checkbox']");

        if (!deleteButton || !deleteField) {
            return;
        }

        function syncRowState() {
            var marked = deleteField.checked;
            row.classList.toggle("is-marked-delete", marked);
            deleteButton.textContent = marked ? "Przywróć" : "Usuń";
            deleteButton.classList.toggle("is-active", marked);
        }

        deleteButton.addEventListener("click", function () {
            deleteField.checked = !deleteField.checked;
            syncRowState();
        });

        syncRowState();
    }

    function bindToggle(field) {
        var input = field.querySelector('input[type="checkbox"]');
        var text = field.querySelector("[data-cms-toggle-text]");
        if (!input || !text) {
            return;
        }

        function syncToggle() {
            text.textContent = input.checked ? "Tak" : "Nie";
        }

        input.addEventListener("change", syncToggle);
        syncToggle();
    }

    document.querySelectorAll("[data-cms-file]").forEach(bindFileField);
    document.querySelectorAll("[data-cms-formset-row]").forEach(bindFormsetRow);
    document.querySelectorAll(".cms-toggle").forEach(bindToggle);
})();
