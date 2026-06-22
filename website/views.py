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


def _page(request, page_title, heading=None, lead=None, body=None):
    return render(
        request,
        "website/page.html",
        {
            "page_title": page_title,
            "page_heading": heading or page_title,
            "page_lead": lead,
            "page_body": body,
        },
    )


def home(request):
    from cms.services import get_home_context

    context = get_home_context()
    context.update(
        {
            "page_title": "Strona główna",
            "page_heading": "Strona główna",
        }
    )
    return render(request, "website/home.html", context)


def products_list(request):
    from cms.services import get_placeholder, get_product_groups

    return render(
        request,
        "website/products_list.html",
        {
            "page_title": "Produkty",
            "page_heading": "Produkty",
            "page_body_class": "page-body--products-catalog",
            "product_groups": get_product_groups(),
            "placeholder_img": get_placeholder(),
        },
    )


def product_category(request, category_slug):
    from django.http import Http404

    from cms.services import (
        category_products,
        get_placeholder,
        get_product_filters,
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
            "product_filters": get_product_filters(),
            "placeholder_img": get_placeholder(),
        },
    )


def product_detail(request, category_slug, product_slug):
    from django.http import Http404

    from cms.services import get_placeholder, get_product, get_product_group, get_related_products

    category = get_product_group(category_slug)
    if category is None:
        raise Http404

    product = get_product(category_slug, product_slug)
    if product is None:
        raise Http404

    return render(
        request,
        "website/product_detail.html",
        {
            "page_title": product["title"],
            "page_heading": product["title"],
            "category": category,
            "product": product,
            "related_products": get_related_products(exclude_slug=product_slug),
            "placeholder_img": get_placeholder(),
        },
    )


def surfaces(request):
    from cms.services import get_placeholder, get_product_filters, get_surface_items

    surface_items = get_surface_items()
    return render(
        request,
        "website/surfaces.html",
        {
            "page_title": "Barwy i powierzchnie",
            "page_heading": "Barwy i powierzchnie",
            "product_filters": get_product_filters(),
            "placeholder_img": get_placeholder(),
            "surface_items": surface_items,
        },
    )


def where_to_buy(request):
    from cms.services import get_placeholder

    return render(
        request,
        "website/where_to_buy.html",
        {
            "page_title": "Gdzie kupić",
            "page_heading": "Gdzie kupić",
            "placeholder_img": get_placeholder(),
        },
    )


def tips(request):
    from cms.services import get_placeholder, get_tips

    return render(
        request,
        "website/tips_list.html",
        {
            "page_title": "Porady",
            "page_heading": "Porady",
            "tips": get_tips(),
            "placeholder_img": get_placeholder(),
        },
    )


def tip_detail(request, slug):
    from django.http import Http404

    from cms.services import get_tip

    tip = get_tip(slug)
    if tip is None:
        raise Http404

    return _page(
        request,
        tip["title"],
        heading=tip["title"],
        lead=tip["excerpt"],
        body=tip.get("body"),
    )


def downloads(request):
    from cms.services import get_download_categories, get_download_groups, get_download_items

    return render(
        request,
        "website/downloads.html",
        {
            "page_title": "Do pobrania",
            "page_heading": "Do pobrania",
            "download_categories": get_download_categories(),
            "download_groups": get_download_groups(),
            "download_items": get_download_items(),
        },
    )


def about_company(request):
    return redirect("/#o-nas")


def news(request):
    from cms.services import get_news, get_placeholder

    return render(
        request,
        "website/news_list.html",
        {
            "page_title": "Aktualności",
            "page_heading": "Aktualności",
            "news_posts": get_news(),
            "placeholder_img": get_placeholder(),
        },
    )


def news_detail(request, slug):
    from django.http import Http404

    from cms.services import get_news_post

    post = get_news_post(slug)
    if post is None:
        raise Http404

    return _page(
        request,
        post["title"],
        heading=post["title"],
        lead=post["excerpt"],
        body=post.get("body"),
    )


def careers(request):
    from cms.services import get_content_block, get_job_openings

    intro = get_content_block(
        "page-careers-intro",
        {"body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
    )
    return render(
        request,
        "website/careers.html",
        {
            "page_title": "Praca i kariera",
            "page_heading": "Praca i kariera",
            "jobs": get_job_openings(),
            "page_intro": intro,
        },
    )


def warranty(request):
    from cms.services import get_content_block

    content = get_content_block("page-warranty")
    return render(
        request,
        "website/warranty.html",
        {
            "page_title": "Warunki gwarancji",
            "page_heading": "Warunki gwarancji",
            "page_content": content,
        },
    )


def media(request):
    from cms.services import get_content_block

    content = get_content_block("page-media")
    return render(
        request,
        "website/media.html",
        {
            "page_title": "Dla mediów",
            "page_heading": "Dla mediów",
            "page_content": content,
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
