(function () {
    "use strict";

    var ALLOWED_TAGS = {
        P: true,
        BR: true,
        STRONG: true,
        B: true,
        EM: true,
        I: true,
        U: true,
        A: true,
        UL: true,
        OL: true,
        LI: true,
        H2: true,
        H3: true,
        H4: true,
        BLOCKQUOTE: true,
        DIV: true,
        SPAN: true,
        SUP: true,
        SUB: true,
        NBSP: true,
    };

    function unwrap(node) {
        var parent = node.parentNode;
        if (!parent) return;
        while (node.firstChild) {
            parent.insertBefore(node.firstChild, node);
        }
        parent.removeChild(node);
    }

    function cleanNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            return;
        }
        if (node.nodeType !== Node.ELEMENT_NODE) {
            node.parentNode && node.parentNode.removeChild(node);
            return;
        }

        var tag = node.tagName;
        if (tag === "STYLE" || tag === "SCRIPT" || tag === "META" || tag === "LINK" || tag === "XML" || tag === "O:P") {
            node.parentNode.removeChild(node);
            return;
        }

        // Word / Office noise
        if (tag.indexOf("O:") === 0 || tag.indexOf("V:") === 0 || tag.indexOf("W:") === 0) {
            unwrap(node);
            return;
        }

        Array.prototype.slice.call(node.childNodes).forEach(cleanNode);

        if (!ALLOWED_TAGS[tag]) {
            unwrap(node);
            return;
        }

        // Strip Word/inline font styles; keep only safe link href.
        if (node.hasAttribute("style")) node.removeAttribute("style");
        if (node.hasAttribute("class")) node.removeAttribute("class");
        Array.prototype.slice.call(node.attributes || []).forEach(function (attr) {
            var name = attr.name.toLowerCase();
            if (name === "href" && tag === "A") return;
            if (name === "target" && tag === "A") return;
            if (name === "rel" && tag === "A") return;
            node.removeAttribute(attr.name);
        });

        if (tag === "A") {
            var href = node.getAttribute("href") || "";
            if (!/^(https?:|mailto:|\/|#)/i.test(href)) {
                unwrap(node);
            }
        }

        if (tag === "SPAN" || tag === "DIV") {
            unwrap(node);
        }
    }

    function sanitizeHtml(html) {
        var container = document.createElement("div");
        container.innerHTML = html;
        Array.prototype.slice.call(container.childNodes).forEach(cleanNode);
        return container.innerHTML
            .replace(/&nbsp;/g, "\u00a0")
            .replace(/\u00a0{2,}/g, "\u00a0");
    }

    function insertHtml(editor, html) {
        editor.focus();
        var cleaned = sanitizeHtml(html);
        if (!cleaned) return;
        if (document.queryCommandSupported && document.queryCommandSupported("insertHTML")) {
            document.execCommand("insertHTML", false, cleaned);
            return;
        }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount) {
            editor.insertAdjacentHTML("beforeend", cleaned);
            return;
        }
        var range = selection.getRangeAt(0);
        range.deleteContents();
        var temp = document.createElement("div");
        temp.innerHTML = cleaned;
        var fragment = document.createDocumentFragment();
        while (temp.firstChild) {
            fragment.appendChild(temp.firstChild);
        }
        range.insertNode(fragment);
        selection.collapseToEnd();
    }

    function insertPlainText(editor, text) {
        editor.focus();
        document.execCommand("insertText", false, text);
    }

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

        editor.addEventListener("paste", function (event) {
            event.preventDefault();
            var clipboard = event.clipboardData || window.clipboardData;
            if (!clipboard) return;
            var html = clipboard.getData("text/html");
            var text = clipboard.getData("text/plain");
            if (html) {
                insertHtml(editor, html);
            } else if (text) {
                insertPlainText(editor, text);
            }
            sync();
        });

        toolbar.addEventListener("mousedown", function (event) {
            var button = event.target.closest("[data-command]");
            if (!button) return;
            event.preventDefault();
            editor.focus();

            var command = button.dataset.command;
            if (command === "nbsp") {
                document.execCommand("insertHTML", false, "&nbsp;");
            } else if (command === "formatBlock") {
                document.execCommand("formatBlock", false, button.dataset.value || "h2");
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
