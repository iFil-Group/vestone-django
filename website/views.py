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


def form_widget(request, slug):
    from django.core.mail import send_mail
    from django.shortcuts import get_object_or_404
    from cms.models import FormWidget
    from website.forms import WidgetSubmissionForm

    widget = get_object_or_404(FormWidget, slug=slug, is_active=True)
    submitted = False
    form = WidgetSubmissionForm(request.POST or None, widget=widget)
    if request.method == "POST" and form.is_valid():
        submission = form.save()
        send_mail(
            subject=f"Nowe zgłoszenie — {widget.title}",
            message=(
                f"Imię i nazwisko: {submission.first_name} {submission.last_name}\n"
                f"Adres: {submission.street} {submission.house_number}, "
                f"{submission.postal_code} {submission.city}\n"
                f"Firma: {submission.company or '—'}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[widget.recipient_email],
            fail_silently=True,
        )
        submitted = True
        form = WidgetSubmissionForm(widget=widget)

    return render(
        request,
        "website/form_widget.html",
        {
            "page_title": widget.title,
            "page_heading": widget.title,
            "widget": widget,
            "form": form,
            "submitted": submitted,
        },
    )


def products_list(request):
    from cms.services import get_content_block, get_placeholder, get_product_groups

    return render(
        request,
        "website/products_list.html",
        {
            "page_title": "Produkty",
            "page_heading": "Produkty",
            "page_body_class": "page-body--products-catalog",
            "product_groups": get_product_groups(),
            "products_cta": get_content_block(
                "products-cta",
                {
                    "title": "Nie wiesz co wybrać?",
                    "body": "Skontaktuj się z nami, a pomożemy dobrać rozwiązanie.",
                    "button_label": "Skontaktuj się",
                    "button_url": "/#kontakt",
                },
            ),
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
            "product_filters": get_product_filters(category_slug),
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
            "related_products": get_related_products(
                exclude_slug=product_slug, category_slug=category_slug
            ),
            "placeholder_img": get_placeholder(),
        },
    )


def surfaces(request):
    from cms.services import get_placeholder, get_surface_groups

    return render(
        request,
        "website/surfaces.html",
        {
            "page_title": "Barwy i powierzchnie",
            "page_heading": "Barwy i powierzchnie",
            "placeholder_img": get_placeholder(),
            "surface_groups": get_surface_groups(),
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

    return render(
        request,
        "website/article_detail.html",
        {
            "page_title": tip["title"],
            "page_heading": tip["title"],
            "page_lead": tip["excerpt"],
            "page_body": tip.get("body"),
            "article": tip,
        },
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
    from cms.services import get_content_block

    content = get_content_block("page-about-company")
    return _page(
        request,
        "O nas",
        heading=content.get("title") or "O nas",
        lead=content.get("subtitle"),
        body=(content.get("body") or "") + (content.get("body_extra") or ""),
    )


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

    return render(
        request,
        "website/article_detail.html",
        {
            "page_title": post["title"],
            "page_heading": post["title"],
            "page_lead": post["excerpt"],
            "page_body": post.get("body"),
            "article": post,
        },
    )


def careers(request):
    from django.core.mail import EmailMessage
    from cms.services import get_content_block, get_job_openings, get_site_settings
    from website.forms import JobApplicationForm

    intro = get_content_block(
        "page-careers-intro",
        {"body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
    )
    application_sent = False
    application_job_id = request.POST.get("job", "") if request.method == "POST" else ""
    application_form = JobApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and application_form.is_valid():
        application = application_form.save()
        email = EmailMessage(
            subject=f"Aplikacja: {application.job.title}",
            body=(
                f"Kandydat: {application.name}\nE-mail: {application.email}\n"
                f"Telefon: {application.phone}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[get_site_settings()["email"] or settings.DEFAULT_FROM_EMAIL],
        )
        application.cv.open("rb")
        email.attach(application.cv.name.rsplit("/", 1)[-1], application.cv.read())
        email.send(fail_silently=True)
        application.cv.close()
        application_sent = True
        application_form = JobApplicationForm()
    return render(
        request,
        "website/careers.html",
        {
            "page_title": "Praca i kariera",
            "page_heading": "Praca i kariera",
            "jobs": get_job_openings(),
            "page_intro": intro,
            "application_form": application_form,
            "application_job_id": application_job_id,
            "application_sent": application_sent,
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
    from cms.models import LegalDocument

    document_obj = LegalDocument.objects.filter(slug=slug, is_active=True).first()
    title = document_obj.title if document_obj else DOCUMENT_PAGES.get(slug)
    if title is None:
        from django.http import Http404

        raise Http404
    return _page(request, title, body=document_obj.body if document_obj else None)


def page_not_found(request, exception=None):
    return render(
        request,
        "404.html",
        {
            "page_title": "404",
            "page_heading": "404",
            "page_lead": "Taka strona nie istnieje.",
            "breadcrumbs": [
                {"label": "Strona główna", "url": "/"},
                {"label": "404", "url": None},
            ],
        },
        status=404,
    )
