(function () {
    "use strict";

    function openDialog(dialog) {
        if (!dialog) return;
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
    }

    document.querySelectorAll("[data-job-open]").forEach(function (button) {
        button.addEventListener("click", function () {
            openDialog(document.querySelector('[data-job-modal="' + button.dataset.jobOpen + '"]'));
        });
    });
    document.querySelectorAll("[data-job-close]").forEach(function (button) {
        button.addEventListener("click", function () {
            var dialog = button.closest("dialog");
            if (dialog && typeof dialog.close === "function") dialog.close();
            else if (dialog) dialog.removeAttribute("open");
        });
    });

    function bindFileDrop(fileDrop) {
        var fileInput = fileDrop.querySelector("[data-file-input]");
        var fileLabel = fileDrop.querySelector("[data-file-label]");
        function updateFileLabel() {
        if (!fileInput || !fileLabel || !fileDrop) {
            return;
        }

        var file = fileInput.files && fileInput.files[0];
        if (file) {
            fileDrop.classList.add("has-file");
            fileLabel.textContent = file.name;
        } else {
            fileDrop.classList.remove("has-file");
            fileLabel.textContent = "Przeciągnij plik lub kliknij, aby wybrać";
        }
        }
        if (fileInput) fileInput.addEventListener("change", updateFileLabel);
        ["dragenter", "dragover"].forEach(function (eventName) {
            fileDrop.addEventListener(eventName, function (event) {
                event.preventDefault();
                fileDrop.classList.add("is-dragover");
            });
        });

        ["dragleave", "drop"].forEach(function (eventName) {
            fileDrop.addEventListener(eventName, function (event) {
                event.preventDefault();
                fileDrop.classList.remove("is-dragover");
            });
        });

        fileDrop.addEventListener("drop", function (event) {
            if (fileInput && event.dataTransfer && event.dataTransfer.files.length) {
                fileInput.files = event.dataTransfer.files;
                updateFileLabel();
            }
        });
    }
    document.querySelectorAll("[data-file-drop]").forEach(bindFileDrop);

    var errorList = document.querySelector(".career-modal .errorlist");
    if (errorList) openDialog(errorList.closest("[data-job-modal]"));
    var thanks = document.querySelector("[data-career-thanks]");
    if (thanks) openDialog(thanks);
})();
