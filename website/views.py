from django.conf import settings
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme


def _safe_next_url(request, url):
    if url and url_has_allowed_host_and_scheme(
        url,
        allowed_hosts={request.get_host()},
    ):
        return url
    return "/"


def _site_access_password_ok(password):
    return bool(password) and password in settings.SITE_ACCESS_PASSWORDS


def site_unlock(request):
    if request.session.get("site_access_granted"):
        return redirect(_safe_next_url(request, request.GET.get("next")))

    error = False
    if request.method == "POST":
        if _site_access_password_ok(request.POST.get("password")):
            request.session["site_access_granted"] = True
            request.session.set_expiry(60 * 60 * 24 * 14)
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(_safe_next_url(request, next_url))
        error = True

    return render(
        request,
        "website/site_unlock.html",
        {
            "error": error,
            "next": request.GET.get("next", ""),
        },
    )


def _page(request, page_title, heading=None, lead=None):
    return render(
        request,
        "website/page.html",
        {
            "page_title": page_title,
            "page_heading": heading or page_title,
            "page_lead": lead,
        },
    )


def home(request):
    from .content_data import PRODUCT_GROUPS

    return render(
        request,
        "website/home.html",
        {
            "page_title": "Strona główna",
            "page_heading": "Strona główna",
            "product_groups": PRODUCT_GROUPS,
        },
    )


def products_list(request):
    from .content_data import PLACEHOLDER_IMG, PRODUCT_GROUPS

    return render(
        request,
        "website/products_list.html",
        {
            "page_title": "Produkty",
            "page_heading": "Produkty",
            "page_body_class": "page-body--products-catalog",
            "product_groups": PRODUCT_GROUPS,
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def product_category(request, category_slug):
    from django.http import Http404

    from .content_data import (
        PLACEHOLDER_IMG,
        PRODUCT_FILTERS,
        category_products,
        get_product_group,
    )

    category = get_product_group(category_slug)
    if category is None:
        raise Http404

    return render(
        request,
        "website/product_category.html",
        {
            "page_title": category["title"],
            "page_heading": category["title"],
            "category": category,
            "products": category_products(category_slug),
            "product_filters": PRODUCT_FILTERS,
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def product_detail(request, category_slug, product_slug):
    from django.http import Http404

    from .content_data import (
        PLACEHOLDER_IMG,
        RELATED_PRODUCTS,
        TEST_PRODUCT,
        TEST_PRODUCT_SLUG,
        get_product_group,
    )

    category = get_product_group(category_slug)
    if category is None:
        raise Http404

    if product_slug != TEST_PRODUCT_SLUG:
        raise Http404

    product = {**TEST_PRODUCT, "category_slug": category_slug}

    return render(
        request,
        "website/product_detail.html",
        {
            "page_title": product["title"],
            "page_heading": product["title"],
            "category": category,
            "product": product,
            "related_products": RELATED_PRODUCTS,
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def surfaces(request):
    return _page(request, "Barwy i powierzchnie")


def where_to_buy(request):
    from .content_data import PLACEHOLDER_IMG

    return render(
        request,
        "website/where_to_buy.html",
        {
            "page_title": "Gdzie kupić",
            "page_heading": "Gdzie kupić",
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def tips(request):
    from .content_data import PLACEHOLDER_IMG, TIPS_POSTS

    return render(
        request,
        "website/tips_list.html",
        {
            "page_title": "Porady",
            "page_heading": "Porady",
            "tips": TIPS_POSTS,
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def tip_detail(request, slug):
    from django.http import Http404

    from .content_data import TIPS_POSTS

    tip = next((item for item in TIPS_POSTS if item["slug"] == slug), None)
    if tip is None:
        raise Http404

    return _page(
        request,
        tip["title"],
        heading=tip["title"],
        lead=tip["excerpt"],
    )


def downloads(request):
    from .content_data import DOWNLOAD_CATEGORIES, DOWNLOAD_GROUPS, DOWNLOAD_ITEMS

    return render(
        request,
        "website/downloads.html",
        {
            "page_title": "Do pobrania",
            "page_heading": "Do pobrania",
            "download_categories": DOWNLOAD_CATEGORIES,
            "download_groups": DOWNLOAD_GROUPS,
            "download_items": DOWNLOAD_ITEMS,
        },
    )


def about_company(request):
    return redirect("/#o-nas")


def news(request):
    from .content_data import NEWS_POSTS, PLACEHOLDER_IMG

    return render(
        request,
        "website/news_list.html",
        {
            "page_title": "Aktualności",
            "page_heading": "Aktualności",
            "news_posts": NEWS_POSTS,
            "placeholder_img": PLACEHOLDER_IMG,
        },
    )


def news_detail(request, slug):
    from django.http import Http404

    from .content_data import NEWS_POSTS

    post = next((item for item in NEWS_POSTS if item["slug"] == slug), None)
    if post is None:
        raise Http404

    return _page(
        request,
        post["title"],
        heading=post["title"],
        lead=post["excerpt"],
    )


def careers(request):
    from .content_data import JOB_OPENINGS

    return render(
        request,
        "website/careers.html",
        {
            "page_title": "Praca i kariera",
            "page_heading": "Praca i kariera",
            "jobs": JOB_OPENINGS,
        },
    )


def warranty(request):
    return render(
        request,
        "website/warranty.html",
        {
            "page_title": "Warunki gwarancji",
            "page_heading": "Warunki gwarancji",
        },
    )


def media(request):
    return render(
        request,
        "website/media.html",
        {
            "page_title": "Dla mediów",
            "page_heading": "Dla mediów",
        },
    )


DOCUMENT_PAGES = {
    "polityka-prywatnosci": "Polityka prywatności",
    "regulamin-serwisu": "Regulamin serwisu",
    "obowiazek-informacyjny": "Obowiązek informacyjny",
}


def document(request, slug):
    title = DOCUMENT_PAGES.get(slug)
    if title is None:
        from django.http import Http404

        raise Http404
    return _page(request, title)
