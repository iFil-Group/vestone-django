(function () {
    "use strict";

    document.querySelectorAll("[data-richtext]").forEach(function (root) {
        var source = root.querySelector(".cms-richtext-source");
        var editor = root.querySelector(".cms-richtext__editor");
        var toolbar = root.querySelector(".cms-richtext__toolbar");
        if (!source || !editor || !toolbar) return;

        editor.innerHTML = source.value || "";

        function sync() {
            source.value = editor.innerHTML;
        }

        editor.addEventListener("input", sync);
        editor.closest("form").addEventListener("submit", sync);

        toolbar.addEventListener("mousedown", function (event) {
            var button = event.target.closest("[data-command]");
            if (!button) return;
            event.preventDefault();
            editor.focus();

            var command = button.dataset.command;
            if (command === "nbsp") {
                document.execCommand("insertHTML", false, "&nbsp;");
            } else if (command === "createLink") {
                var url = window.prompt("Adres linku:");
                if (url) document.execCommand("createLink", false, url);
            } else {
                document.execCommand(command, false, null);
            }
            sync();
        });
    });
})();
