def _footer_product_groups():
    from cms.services import get_product_groups

    return get_product_groups()


def _normalize_path(path):
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


ABOUT_LINKS = [
    {"label": "O firmie", "url": "/o-nas/"},
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
                "url": "/o-nas/",
                "active": active("/o-nas"),
                "children": ABOUT_LINKS,
            },
        ],
        "nav_home_active": "is-active" if path == "/" else "",
        "about_footer_links": ABOUT_LINKS,
        "footer_product_groups": _footer_product_groups(),
    }


def page_breadcrumbs(request):
    path = _normalize_path(request.path)
    home = {"label": "Strona główna", "url": "/"}

    if path == "/":
        return {"breadcrumbs": [{"label": "Strona główna", "url": None}]}

    about_parent = {"label": "O nas", "url": "/o-nas/"}

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
        from cms.services import get_product, get_product_group

        parts = [part for part in path.split("/") if part]
        # parts: ["produkty", category_slug] or ["produkty", category_slug, product_slug]
        if len(parts) < 2:
            return {"breadcrumbs": [home, {"label": "Produkty", "url": None}]}

        category = get_product_group(parts[1])
        category_label = category["title"] if category else "Kategoria"
        category_url = f"/produkty/{parts[1]}/"

        if len(parts) == 2:
            return {
                "breadcrumbs": [
                    home,
                    {"label": "Produkty", "url": "/produkty/"},
                    {"label": category_label, "url": None},
                ]
            }

        product = get_product(parts[1], parts[2])
        product_label = product["title"] if product else parts[2]
        return {
            "breadcrumbs": [
                home,
                {"label": "Produkty", "url": "/produkty/"},
                {"label": category_label, "url": category_url},
                {"label": product_label, "url": None},
            ]
        }

    if path.startswith("/porady/") and path != "/porady":
        from .content_data import TIPS_POSTS

        slug = path.rsplit("/", 1)[-1]
        tip = next((item for item in TIPS_POSTS if item["slug"] == slug), None)
        title = tip["title"] if tip else "Porada"
        return {
            "breadcrumbs": [
                home,
                {"label": "Porady", "url": "/porady/"},
                {"label": title, "url": None},
            ]
        }

    if path.startswith("/o-nas/aktualnosci/") and path != "/o-nas/aktualnosci":
        from .content_data import NEWS_POSTS

        slug = path.rsplit("/", 1)[-1]
        post = next((item for item in NEWS_POSTS if item["slug"] == slug), None)
        title = post["title"] if post else "Aktualność"
        return {
            "breadcrumbs": [
                home,
                about_parent,
                {"label": "Aktualności", "url": "/o-nas/aktualnosci/"},
                {"label": title, "url": None},
            ]
        }

    return {"breadcrumbs": [home, {"label": "Strona", "url": None}]}


def site_settings(request):
    from cms.services import get_site_settings

    return {"site_settings": get_site_settings()}


def site_promotions(request):
    from cms.services import get_floating_promotions

    return {"floating_promotions": get_floating_promotions()}
