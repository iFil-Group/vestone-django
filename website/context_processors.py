def _normalize_path(path):
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


ABOUT_LINKS = [
    {"label": "O firmie", "url": "/o-nas/o-firmie/"},
    {"label": "Aktualności", "url": "/o-nas/aktualnosci/"},
    {"label": "Praca i kariera", "url": "/o-nas/praca-i-kariera/"},
    {"label": "Warunki gwarancji", "url": "/o-nas/warunki-gwarancji/"},
    {"label": "Dla mediów", "url": "/o-nas/dla-mediow/"},
]


def site_navigation(request):
    path = request.path

    def active(prefix):
        base = prefix.rstrip("/")
        if path == base or path == base + "/":
            return "is-active"
        if path.startswith(base + "/"):
            return "is-active"
        return ""

    return {
        "nav_items": [
            {"label": "Produkty", "url": "/produkty/", "active": active("/produkty")},
            {
                "label": "Barwy i powierzchnie",
                "url": "/barwy-i-powierzchnie/",
                "active": active("/barwy-i-powierzchnie"),
            },
            {"label": "Porady", "url": "/porady/", "active": active("/porady")},
            {"label": "Do pobrania", "url": "/do-pobrania/", "active": active("/do-pobrania")},
            {
                "label": "O nas",
                "url": "/o-nas/o-firmie/",
                "active": active("/o-nas"),
                "children": ABOUT_LINKS,
            },
        ],
        "nav_home_active": "is-active" if path == "/" else "",
        "about_footer_links": ABOUT_LINKS,
    }


def page_breadcrumbs(request):
    path = _normalize_path(request.path)
    home = {"label": "Strona główna", "url": "/"}

    if path == "/":
        return {"breadcrumbs": [{"label": "Strona główna", "url": None}]}

    about_parent = {"label": "O nas", "url": "/o-nas/o-firmie/"}

    static_trails = {
        "/produkty": [home, {"label": "Produkty", "url": None}],
        "/barwy-i-powierzchnie": [home, {"label": "Barwy i powierzchnie", "url": None}],
        "/gdzie-kupic": [home, {"label": "Gdzie kupić", "url": None}],
        "/porady": [home, {"label": "Porady", "url": None}],
        "/do-pobrania": [home, {"label": "Do pobrania", "url": None}],
        "/o-nas/o-firmie": [home, about_parent, {"label": "O firmie", "url": None}],
        "/o-nas/aktualnosci": [home, about_parent, {"label": "Aktualności", "url": None}],
        "/o-nas/praca-i-kariera": [home, about_parent, {"label": "Praca i kariera", "url": None}],
        "/o-nas/warunki-gwarancji": [
            home,
            about_parent,
            {"label": "Warunki gwarancji", "url": None},
        ],
        "/o-nas/dla-mediow": [home, about_parent, {"label": "Dla mediów", "url": None}],
        "/dokumenty/polityka-prywatnosci": [
            home,
            {"label": "Polityka prywatności", "url": None},
        ],
        "/dokumenty/regulamin-serwisu": [
            home,
            {"label": "Regulamin serwisu", "url": None},
        ],
        "/dokumenty/obowiazek-informacyjny": [
            home,
            {"label": "Obowiązek informacyjny", "url": None},
        ],
    }

    if path in static_trails:
        return {"breadcrumbs": static_trails[path]}

    if path.startswith("/produkty/") and path != "/produkty":
        return {
            "breadcrumbs": [
                home,
                {"label": "Produkty", "url": "/produkty/"},
                {"label": "Produkt", "url": None},
            ]
        }

    return {"breadcrumbs": [home, {"label": "Strona", "url": None}]}
