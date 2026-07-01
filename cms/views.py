from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    ContentBlockForm,
    DownloadCategoryForm,
    DownloadItemForm,
    EmailAuthenticationForm,
    HeroSlideForm,
    JobOpeningForm,
    NewsPostForm,
    ProductForm,
    ProductGalleryFormSet,
    ProductGroupForm,
    ProductPinFormSet,
    ProductAttributeAssignmentFormSet,
    ReviewForm,
    SiteSettingsForm,
    SurfaceItemForm,
    TipForm,
)
from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    HeroSlide,
    JobOpening,
    NewsPost,
    Product,
    ProductGroup,
    Review,
    SiteSettings,
    SurfaceItem,
    Tip,
)

CMS_SECTIONS = [
    {"slug": "products", "label": "Produkty", "url_name": "cms_products"},
    {"slug": "surfaces", "label": "Barwy i powierzchnie", "url_name": "cms_surfaces"},
    {"slug": "tips", "label": "Porady", "url_name": "cms_tips"},
    {"slug": "news", "label": "Aktualności", "url_name": "cms_news"},
    {"slug": "downloads", "label": "Pliki do pobrania", "url_name": "cms_downloads"},
    {"slug": "pages", "label": "Strona", "url_name": "cms_pages"},
]


class CMSLoginView(LoginView):
    template_name = "cms/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("cms_dashboard")


def _panel_context(section, title, **extra):
    return {
        "cms_sections": CMS_SECTIONS,
        "active_section": section,
        "page_title": title,
        **extra,
    }


@login_required
def dashboard(request):
    stats = {
        "products": Product.objects.count(),
        "surfaces": SurfaceItem.objects.count(),
        "tips": Tip.objects.count(),
        "news": NewsPost.objects.count(),
        "downloads": DownloadItem.objects.count(),
        "blocks": ContentBlock.objects.count(),
    }
    return render(
        request,
        "cms/dashboard.html",
        _panel_context(None, "Panel CMS", stats=stats),
    )


@login_required
def product_list(request):
    items = Product.objects.select_related("group").order_by("group__title", "sort_order", "title")
    groups = ProductGroup.objects.order_by("sort_order", "title")
    return render(
        request,
        "cms/product_list.html",
        _panel_context("products", "Produkty", items=items, groups=groups),
    )


@login_required
def product_group_edit(request, pk=None):
    instance = get_object_or_404(ProductGroup, pk=pk) if pk else None
    form = ProductGroupForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupa produktów została zapisana.")
        return redirect("cms_products")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "products",
            "Edycja grupy produktów" if instance else "Nowa grupa produktów",
            form=form,
            back_url=reverse("cms_products"),
        ),
    )


@login_required
def product_edit(request, pk=None):
    instance = get_object_or_404(Product, pk=pk) if pk else None
    product = instance

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            product = form.save()

        attribute_formset = ProductAttributeAssignmentFormSet(
            request.POST, instance=product, prefix="attributes"
        )
        pin_formset = ProductPinFormSet(request.POST, instance=product, prefix="pins")
        gallery_formset = ProductGalleryFormSet(
            request.POST,
            request.FILES,
            instance=product,
            prefix="gallery",
        )

        if (
            form.is_valid()
            and attribute_formset.is_valid()
            and pin_formset.is_valid()
            and gallery_formset.is_valid()
        ):
            attribute_formset.save()
            pin_formset.save()
            gallery_formset.save()
            messages.success(request, "Produkt został zapisany.")
            return redirect("cms_product_edit", pk=product.pk)
    else:
        form = ProductForm(instance=instance)
        attribute_formset = ProductAttributeAssignmentFormSet(
            instance=instance, prefix="attributes"
        )
        pin_formset = ProductPinFormSet(instance=instance, prefix="pins")
        gallery_formset = ProductGalleryFormSet(instance=instance, prefix="gallery")

    return render(
        request,
        "cms/product_form.html",
        _panel_context(
            "products",
            "Edycja produktu" if instance else "Nowy produkt",
            form=form,
            attribute_formset=attribute_formset,
            attribute_options=_attribute_options_data(),
            attribute_cards=_attribute_editor_cards(attribute_formset),
            all_attributes=_all_attributes(),
            pin_formset=pin_formset,
            gallery_formset=gallery_formset,
            back_url=reverse("cms_products"),
            product_image_url=_product_image_url(product),
        ),
    )


def _attribute_options_data():
    from .models import ProductAttribute

    payload = {}
    attributes = ProductAttribute.objects.prefetch_related("options").order_by(
        "sort_order", "name"
    )
    for attribute in attributes:
        payload[str(attribute.pk)] = {
            "name": attribute.name,
            "show_in_filters": attribute.show_in_filters,
            "options": [
                {"id": option.pk, "value": option.value}
                for option in attribute.options.all()
            ],
        }
    return payload


def _all_attributes():
    from .models import ProductAttribute

    return list(
        ProductAttribute.objects.order_by("sort_order", "name").values("id", "name", "show_in_filters")
    )


def _attribute_form_is_empty(form):
    if form.instance.pk:
        return False
    if form.data:
        prefix = form.prefix
        keys = (f"{prefix}-attribute", f"{prefix}-new_attribute_name", f"{prefix}-option", f"{prefix}-new_option_value")
        return not any((form.data.get(key) or "").strip() for key in keys)
    return not any(
        [
            form["attribute"].value(),
            (form["new_attribute_name"].value() or "").strip(),
            form["option"].value(),
            (form["new_option_value"].value() or "").strip(),
        ]
    )


def _attribute_form_attribute_id(form):
    value = form["attribute"].value()
    if value:
        return str(value)
    if form.instance.pk and form.instance.option_id:
        return str(form.instance.option.attribute_id)
    return None


def _attribute_form_value_label(form):
    new_value = (form["new_option_value"].value() or "").strip()
    if new_value:
        return new_value
    option_id = form["option"].value()
    if option_id:
        from .models import ProductAttributeOption

        option = ProductAttributeOption.objects.filter(pk=option_id).first()
        if option:
            return option.value
    if form.instance.pk and form.instance.option_id:
        return form.instance.option.value
    return ""


def _attribute_editor_cards(formset):
    cards = []
    lookup = {}

    for index, form in enumerate(formset.forms):
        if _attribute_form_is_empty(form):
            continue

        attribute_id = _attribute_form_attribute_id(form)
        new_attribute_name = (form["new_attribute_name"].value() or "").strip()
        key = attribute_id or f"new:{index}"

        if key not in lookup:
            show_in_filters = bool(form["show_in_filters"].value())
            if not show_in_filters and attribute_id:
                from .models import ProductAttribute

                attr = ProductAttribute.objects.filter(pk=attribute_id).first()
                show_in_filters = bool(attr and attr.show_in_filters)

            card = {
                "key": key,
                "attribute_id": attribute_id,
                "new_attribute_name": new_attribute_name if not attribute_id else "",
                "show_in_filters": show_in_filters,
                "values": [],
            }
            lookup[key] = card
            cards.append(card)

        label = _attribute_form_value_label(form)
        if not label:
            continue

        lookup[key]["values"].append(
            {
                "form_index": index,
                "label": label,
            }
        )

    return cards


def _product_image_url(product):
    from cms.services import get_placeholder

    if product and product.image:
        return product.image.url
    return get_placeholder()


@login_required
def surface_list(request):
    items = SurfaceItem.objects.order_by("sort_order", "title")
    return render(
        request,
        "cms/list.html",
        _panel_context(
            "surfaces",
            "Barwy i powierzchnie",
            items=items,
            add_url=reverse("cms_surface_add"),
            edit_url_name="cms_surface_edit",
            columns=[("title", "Nazwa"), ("color", "Kolor"), ("surface", "Powierzchnia")],
        ),
    )


@login_required
def surface_edit(request, pk=None):
    instance = get_object_or_404(SurfaceItem, pk=pk) if pk else None
    form = SurfaceItemForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pozycja została zapisana.")
        return redirect("cms_surfaces")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "surfaces",
            "Edycja barwy / powierzchni" if instance else "Nowa barwa / powierzchnia",
            form=form,
            back_url=reverse("cms_surfaces"),
        ),
    )


@login_required
def tip_list(request):
    items = Tip.objects.order_by("-published_at")
    return render(
        request,
        "cms/list.html",
        _panel_context(
            "tips",
            "Porady",
            items=items,
            add_url=reverse("cms_tip_add"),
            edit_url_name="cms_tip_edit",
            columns=[("title", "Tytuł"), ("published_at", "Data")],
        ),
    )


@login_required
def tip_edit(request, pk=None):
    instance = get_object_or_404(Tip, pk=pk) if pk else None
    form = TipForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Porada została zapisana.")
        return redirect("cms_tips")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "tips",
            "Edycja porady" if instance else "Nowa porada",
            form=form,
            back_url=reverse("cms_tips"),
        ),
    )


@login_required
def news_list(request):
    items = NewsPost.objects.order_by("-published_at")
    return render(
        request,
        "cms/list.html",
        _panel_context(
            "news",
            "Aktualności",
            items=items,
            add_url=reverse("cms_news_add"),
            edit_url_name="cms_news_edit",
            columns=[("title", "Tytuł"), ("published_at", "Data")],
        ),
    )


@login_required
def news_edit(request, pk=None):
    instance = get_object_or_404(NewsPost, pk=pk) if pk else None
    form = NewsPostForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Aktualność została zapisana.")
        return redirect("cms_news")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "news",
            "Edycja aktualności" if instance else "Nowa aktualność",
            form=form,
            back_url=reverse("cms_news"),
        ),
    )


@login_required
def download_list(request):
    categories = DownloadCategory.objects.prefetch_related("items").order_by("sort_order")
    items = DownloadItem.objects.select_related("category").order_by("category__sort_order", "sort_order")
    return render(
        request,
        "cms/download_list.html",
        _panel_context(
            "downloads",
            "Pliki do pobrania",
            categories=categories,
            items=items,
        ),
    )


@login_required
def download_category_edit(request, pk=None):
    instance = get_object_or_404(DownloadCategory, pk=pk) if pk else None
    form = DownloadCategoryForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Kategoria została zapisana.")
        return redirect("cms_downloads")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "downloads",
            "Edycja kategorii" if instance else "Nowa kategoria",
            form=form,
            back_url=reverse("cms_downloads"),
        ),
    )


@login_required
def download_item_edit(request, pk=None):
    instance = get_object_or_404(DownloadItem, pk=pk) if pk else None
    form = DownloadItemForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Plik został zapisany.")
        return redirect("cms_downloads")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "downloads",
            "Edycja pliku" if instance else "Nowy plik",
            form=form,
            back_url=reverse("cms_downloads"),
        ),
    )


@login_required
def page_index(request):
    home_blocks = ContentBlock.objects.filter(group=ContentBlock.GROUP_HOME)
    about_blocks = ContentBlock.objects.filter(group=ContentBlock.GROUP_ABOUT)
    hero_slides = HeroSlide.objects.order_by("sort_order")
    reviews = Review.objects.order_by("sort_order")
    settings_form = SiteSettingsForm(request.POST or None, instance=SiteSettings.load())
    if request.method == "POST" and settings_form.is_valid():
        settings_form.save()
        messages.success(request, "Ustawienia strony zostały zapisane.")
        return redirect("cms_pages")

    return render(
        request,
        "cms/page_index.html",
        _panel_context(
            "pages",
            "Strona — treści i mapowanie",
            home_blocks=home_blocks,
            about_blocks=about_blocks,
            hero_slides=hero_slides,
            reviews=reviews,
            settings_form=settings_form,
        ),
    )


@login_required
def content_block_edit(request, pk=None):
    instance = get_object_or_404(ContentBlock, pk=pk) if pk else None
    form = ContentBlockForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blok treści został zapisany.")
        return redirect("cms_pages")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "pages",
            "Edycja bloku treści" if instance else "Nowy blok treści",
            form=form,
            back_url=reverse("cms_pages"),
        ),
    )


@login_required
def hero_slide_edit(request, pk=None):
    instance = get_object_or_404(HeroSlide, pk=pk) if pk else None
    form = HeroSlideForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Slajd został zapisany.")
        return redirect("cms_pages")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "pages",
            "Edycja slajdu" if instance else "Nowy slajd hero",
            form=form,
            back_url=reverse("cms_pages"),
        ),
    )


@login_required
def review_edit(request, pk=None):
    instance = get_object_or_404(Review, pk=pk) if pk else None
    form = ReviewForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Opinia została zapisana.")
        return redirect("cms_pages")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "pages",
            "Edycja opinii" if instance else "Nowa opinia",
            form=form,
            back_url=reverse("cms_pages"),
        ),
    )


@login_required
def job_list(request):
    items = JobOpening.objects.order_by("title")
    return render(
        request,
        "cms/list.html",
        _panel_context(
            "pages",
            "Oferty pracy",
            items=items,
            add_url=reverse("cms_job_add"),
            edit_url_name="cms_job_edit",
            columns=[("title", "Stanowisko"), ("location", "Lokalizacja")],
            back_url=reverse("cms_pages"),
        ),
    )


@login_required
def job_edit(request, pk=None):
    instance = get_object_or_404(JobOpening, pk=pk) if pk else None
    form = JobOpeningForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Oferta pracy została zapisana.")
        return redirect("cms_jobs")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "pages",
            "Edycja oferty pracy" if instance else "Nowa oferta pracy",
            form=form,
            back_url=reverse("cms_jobs"),
        ),
    )
