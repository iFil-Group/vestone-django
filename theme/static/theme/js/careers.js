(function () {
    "use strict";

    var form = document.querySelector("[data-careers-form]");
    if (!form) {
        return;
    }

    var positionSelect = form.querySelector("[data-careers-position]");
    var fileDrop = form.querySelector("[data-file-drop]");
    var fileInput = form.querySelector("[data-file-input]");
    var fileLabel = form.querySelector("[data-file-label]");
    var applyLinks = document.querySelectorAll("[data-job-apply]");

    applyLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            var jobId = link.getAttribute("data-job-apply");
            if (positionSelect && jobId) {
                positionSelect.value = jobId;
            }

            document.querySelectorAll(".job-card").forEach(function (card) {
                card.classList.remove("is-highlighted");
            });
            var card = document.getElementById("oferta-" + jobId);
            if (card) {
                card.classList.add("is-highlighted");
            }
        });
    });

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

    if (fileInput) {
        fileInput.addEventListener("change", updateFileLabel);
    }

    if (fileDrop) {
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
})();
