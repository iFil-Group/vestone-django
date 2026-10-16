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
        H1: true,
        H2: true,
        H3: true,
        H4: true,
        H5: true,
        H6: true,
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

    function normalizeListHtml(html) {
        if (!html || html.indexOf("<ol") === -1) {
            return html;
        }
        var container = document.createElement("div");
        container.innerHTML = html;
        var nested;
        do {
            nested = false;
            container.querySelectorAll("li").forEach(function (li) {
                var childOl = li.querySelector(":scope > ol");
                if (!childOl) return;
                nested = true;
                var before = document.createDocumentFragment();
                var after = document.createDocumentFragment();
                var foundOl = false;
                Array.prototype.slice.call(li.childNodes).forEach(function (child) {
                    if (child === childOl) {
                        foundOl = true;
                        return;
                    }
                    if (!foundOl) {
                        before.appendChild(child.cloneNode(true));
                    } else if (child !== childOl) {
                        after.appendChild(child.cloneNode(true));
                    }
                });
                var parentList = li.parentNode;
                var insertAfter = li;
                if (before.textContent && before.textContent.trim()) {
                    var liBefore = document.createElement("li");
                    liBefore.appendChild(before);
                    parentList.insertBefore(liBefore, li);
                    insertAfter = liBefore;
                }
                Array.prototype.slice.call(childOl.children).forEach(function (innerLi) {
                    parentList.insertBefore(innerLi, li);
                    insertAfter = innerLi;
                });
                if (after.textContent && after.textContent.trim()) {
                    var liAfter = document.createElement("li");
                    liAfter.appendChild(after);
                    parentList.insertBefore(liAfter, li);
                }
                li.parentNode.removeChild(li);
            });
        } while (nested);

        var manualBr = /<br\s*\/?>\s*(?=(?:\d+\.)+\d+\s)/gi;
        var manualPrefix = /^(\s*(?:<[^>]+>)*\s*)(?:\d+\.)+\d+\s+/i;
        container.querySelectorAll("li").forEach(function (li) {
            var inner = li.innerHTML;
            if (!manualBr.test(inner) && !manualPrefix.test(li.textContent || "")) {
                return;
            }
            manualBr.lastIndex = 0;
            var parts = inner.split(manualBr);
            if (parts.length <= 1) {
                li.innerHTML = inner.replace(manualPrefix, "$1");
                return;
            }
            var parent = li.parentNode;
            parts.forEach(function (part, index) {
                part = part.trim();
                if (!part) return;
                part = part.replace(manualPrefix, "$1");
                if (index === 0) {
                    li.innerHTML = part;
                } else {
                    var newLi = document.createElement("li");
                    newLi.innerHTML = part;
                    parent.insertBefore(newLi, li.nextSibling);
                }
            });
        });
        return container.innerHTML;
    }

    function removeListFormatting(editor) {
        editor.focus();
        var attempts = 0;
        while (attempts < 8) {
            var parent = window.getSelection && window.getSelection().anchorNode;
            while (parent && parent !== editor && parent.nodeName !== "LI") {
                parent = parent.parentNode;
            }
            if (!parent || parent.nodeName !== "LI") {
                break;
            }
            document.execCommand("outdent", false, null);
            document.execCommand("insertOrderedList", false, null);
            document.execCommand("insertUnorderedList", false, null);
            document.execCommand("formatBlock", false, "p");
            attempts += 1;
        }
        document.execCommand("removeFormat", false, null);
        document.execCommand("formatBlock", false, "p");
    }

    document.querySelectorAll("[data-richtext]").forEach(function (root) {
        var source = root.querySelector(".cms-richtext-source");
        var editor = root.querySelector(".cms-richtext__editor");
        var toolbar = root.querySelector(".cms-richtext__toolbar");
        if (!source || !editor || !toolbar) return;

        editor.innerHTML = source.value || "";

        function sync() {
            source.value = normalizeListHtml(editor.innerHTML);
        }

        editor.addEventListener("input", sync);
        editor.closest("form").addEventListener("submit", sync);

        function selectionInListItem() {
            var selection = window.getSelection();
            if (!selection || !selection.anchorNode) {
                return null;
            }
            var node = selection.anchorNode;
            if (node.nodeType === Node.TEXT_NODE) {
                node = node.parentNode;
            }
            while (node && node !== editor && node.nodeName !== "LI") {
                node = node.parentNode;
            }
            return node && node.nodeName === "LI" ? node : null;
        }

        editor.addEventListener("keydown", function (event) {
            if (event.key !== "Enter") {
                return;
            }
            var listItem = selectionInListItem();
            if (event.shiftKey) {
                if (listItem) {
                    event.preventDefault();
                    document.execCommand("insertLineBreak");
                    sync();
                }
                return;
            }
            if (listItem && !(listItem.textContent || "").trim()) {
                event.preventDefault();
                removeListFormatting(editor);
                sync();
            }
        });

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

        function applyBlock(tag) {
            editor.focus();
            var applied = document.execCommand("formatBlock", false, tag);
            if (!applied) {
                document.execCommand("formatBlock", false, "<" + tag + ">");
            }
            sync();
        }

        toolbar.addEventListener("mousedown", function (event) {
            if (event.target.closest("select")) return;
            var button = event.target.closest("[data-command]");
            if (!button) return;
            event.preventDefault();
            editor.focus();

            var command = button.dataset.command;
            if (command === "nbsp") {
                document.execCommand("insertHTML", false, "&nbsp;");
            } else if (command === "outdent" || command === "paragraph") {
                removeListFormatting(editor);
            } else if (command === "formatBlock") {
                applyBlock(button.dataset.value || "p");
            } else if (command === "createLink") {
                var url = window.prompt("Adres linku:");
                if (url) document.execCommand("createLink", false, url);
            } else {
                document.execCommand(command, false, null);
            }
            sync();
        });

        var headingSelect = toolbar.querySelector("[data-heading-select]");
        if (headingSelect) {
            headingSelect.addEventListener("change", function () {
                applyBlock(headingSelect.value || "p");
            });
        }
    });
})();
