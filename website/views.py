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


def site_unlock(request):
    if request.session.get("site_access_granted"):
        return redirect(_safe_next_url(request, request.GET.get("next")))

    error = False
    if request.method == "POST":
        if request.POST.get("password") == settings.SITE_ACCESS_PASSWORD:
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
    return render(
        request,
        "website/home.html",
        {
            "page_title": "Strona główna",
            "page_heading": "Strona główna",
        },
    )


def products_list(request):
    return _page(request, "Produkty")


def product_detail(request, slug):
    return render(
        request,
        "website/page.html",
        {
            "page_title": "Produkt",
            "page_heading": "Produkt",
            "page_lead": f"Podgląd szablonu — slug: {slug}",
        },
    )


def surfaces(request):
    return _page(request, "Barwy i powierzchnie")


def where_to_buy(request):
    return _page(request, "Gdzie kupić")


def tips(request):
    return _page(request, "Porady")


def downloads(request):
    return _page(request, "Do pobrania")


def about_company(request):
    return _page(request, "O firmie", heading="O firmie")


def news(request):
    return _page(request, "Aktualności")


def careers(request):
    return _page(request, "Praca i kariera")


def warranty(request):
    return _page(request, "Warunki gwarancji")


def media(request):
    return _page(request, "Dla mediów")


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
