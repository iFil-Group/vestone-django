(function () {
    const header = document.querySelector("[data-header]");
    const toggle = document.querySelector("[data-nav-toggle]");
    const panel = document.querySelector("[data-nav-panel]");

    if (!header || !toggle || !panel) return;

    toggle.addEventListener("click", () => {
        const open = header.classList.toggle("site-header--open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    panel.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            header.classList.remove("site-header--open");
            toggle.setAttribute("aria-expanded", "false");
        });
    });

    window.addEventListener("resize", () => {
        if (window.matchMedia("(min-width: 1024px)").matches) {
            header.classList.remove("site-header--open");
            toggle.setAttribute("aria-expanded", "false");
        }
    });
})();
