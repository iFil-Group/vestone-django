from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    ContentBlockForm,
    ProductsCtaForm,
    DownloadCategoryForm,
    DownloadItemForm,
    EmailAuthenticationForm,
    FloatingPromotionForm,
    FormWidgetForm,
    HeroSlideForm,
    JobOpeningForm,
    LegalDocumentForm,
    NewsPostForm,
    NewsGalleryFormSet,
    ProductForm,
    ProductGalleryFormSet,
    ProductColorFormSet,
    ProductPackshotFormSet,
    ProductGroupForm,
    ProductPinFormSet,
    ProductAttributeAssignmentFormSet,
    PromotionSlideForm,
    ReviewForm,
    SiteSettingsForm,
    SalesPointForm,
    SurfaceCategoryForm,
    SurfaceItemForm,
    SurfaceTypeForm,
    TipForm,
    TipGalleryFormSet,
)
from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    FloatingPromotion,
    FormSubmission,
    FormWidget,
    HeroSlide,
    JobOpening,
    LegalDocument,
    NewsPost,
    Product,
    ProductGroup,
    PromotionSlide,
    Review,
    SiteSettings,
    SalesPoint,
    SurfaceCategory,
    SurfaceItem,
    SurfaceType,
    Tip,
)

CMS_SECTIONS = [
    {"slug": "products", "label": "Produkty", "url_name": "cms_products"},
    {"slug": "surfaces", "label": "Barwy i powierzchnie", "url_name": "cms_surfaces"},
    {"slug": "tips", "label": "Porady", "url_name": "cms_tips"},
    {"slug": "news", "label": "Aktualności", "url_name": "cms_news"},
    {"slug": "downloads", "label": "Pliki do pobrania", "url_name": "cms_downloads"},
    {"slug": "documents", "label": "Dokumenty", "url_name": "cms_documents"},
    {"slug": "sales-points", "label": "Punkty sprzedaży", "url_name": "cms_sales_points"},
    {"slug": "promotions", "label": "Promocje i formularze", "url_name": "cms_promotions"},
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
    active_tab = request.GET.get("tab", "produkty")
    if active_tab not in {"produkty", "kategorie"}:
        active_tab = "produkty"
    cta_block, _ = ContentBlock.objects.get_or_create(
        key="products-cta",
        defaults={
            "group": ContentBlock.GROUP_HOME,
            "label": "Produkty — kafel kontaktowy",
            "title": "Nie wiesz co wybrać?",
            "body": "Skontaktuj się z nami, a pomożemy dobrać rozwiązanie.",
            "button_label": "Skontaktuj się",
            "button_url": "/#kontakt",
            "is_active": True,
        },
    )

    if request.method == "POST" and request.POST.get("_form") == "products-cta":
        cta_form = ProductsCtaForm(request.POST, instance=cta_block)
        if cta_form.is_valid():
            cta_form.save()
            messages.success(request, "Kafel „Nie wiesz co wybrać?” został zapisany.")
            return redirect(f"{reverse('cms_products')}?tab=kategorie")
    else:
        cta_form = ProductsCtaForm(instance=cta_block)

    return render(
        request,
        "cms/product_list.html",
        _panel_context(
            "products",
            "Produkty",
            items=items,
            groups=groups,
            products_cta_form=cta_form,
            active_tab=active_tab,
        ),
    )


@login_required
def product_group_edit(request, pk=None):
    instance = get_object_or_404(ProductGroup, pk=pk) if pk else None
    form = ProductGroupForm(request.POST or None, request.FILES or None, instance=instance)
    categories_url = f"{reverse('cms_products')}?tab=kategorie"
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupa produktów została zapisana.")
        return redirect(categories_url)
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "products",
            "Edycja grupy produktów" if instance else "Nowa grupa produktów",
            form=form,
            back_url=categories_url,
        ),
    )


@login_required
def product_edit(request, pk=None):
    instance = get_object_or_404(Product, pk=pk) if pk else None
    product = instance

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=instance)
        form_valid = form.is_valid()
        product = form.save(commit=False) if form_valid else (instance or Product())

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
        packshot_formset = ProductPackshotFormSet(
            request.POST,
            request.FILES,
            instance=product,
            prefix="packshots",
        )
        color_formset = ProductColorFormSet(
            request.POST,
            request.FILES,
            instance=product,
            prefix="colors",
        )

        tech_packs_ok, tech_packs_data = _parse_tech_packs_payload(
            request.POST.get("tech_packs_json")
        )

        if (
            form_valid
            and attribute_formset.is_valid()
            and pin_formset.is_valid()
            and gallery_formset.is_valid()
            and packshot_formset.is_valid()
            and color_formset.is_valid()
            and tech_packs_ok
        ):
            from django.db import transaction

            from cms.services import save_product_tech_packs

            with transaction.atomic():
                product = form.save()
                attribute_formset.instance = product
                pin_formset.instance = product
                gallery_formset.instance = product
                packshot_formset.instance = product
                color_formset.instance = product
                attribute_formset.save()
                gallery_formset.save()
                packshot_formset.save()
                color_formset.save()
                # Resolve pins aimed at not-yet-saved gallery tiles (pending:N).
                pin_formset.apply_pending_gallery_images(gallery_formset)
                pin_formset.save()
                save_product_tech_packs(product, tech_packs_data)
            messages.success(request, "Produkt został zapisany.")
            return redirect("cms_product_edit", pk=product.pk)
        if not tech_packs_ok:
            messages.error(request, "Nie udało się odczytać danych technicznych.")
    else:
        form = ProductForm(instance=instance)
        attribute_formset = ProductAttributeAssignmentFormSet(
            instance=instance, prefix="attributes"
        )
        pin_formset = ProductPinFormSet(instance=instance, prefix="pins")
        gallery_formset = ProductGalleryFormSet(instance=instance, prefix="gallery")
        packshot_formset = ProductPackshotFormSet(instance=instance, prefix="packshots")
        color_formset = ProductColorFormSet(instance=instance, prefix="colors")

    from cms.services import serialize_product_tech_packs

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
            packshot_formset=packshot_formset,
            color_formset=color_formset,
            tech_packs=serialize_product_tech_packs(instance),
            back_url=reverse("cms_products"),
            product_image_url=_product_image_url(product),
            gallery_pin_targets=_gallery_pin_targets(product),
            selected_related_products=_selected_related_products(request, instance),
        ),
    )


def _gallery_pin_targets(product):
    targets = [{"id": "", "label": "Zdjęcie główne", "image": _product_image_url(product)}]
    if product and product.pk:
        targets.extend(
            {
                "id": str(image.pk),
                "label": image.alt or f"Zdjęcie galerii #{index}",
                "image": image.image.url,
            }
            for index, image in enumerate(product.gallery.all(), start=1)
            if image.image
        )
    return targets


def _selected_related_products(request, instance):
    if request.method == "POST":
        ids = [value for value in request.POST.getlist("related_products") if value.isdigit()]
        return list(Product.objects.filter(pk__in=ids).select_related("group"))
    return list(instance.related_products.select_related("group").all()) if instance else []


@login_required
def product_search(request):
    from django.db.models import Q

    query = (request.GET.get("q") or "").strip()
    products = Product.objects.select_related("group")
    exclude_id = request.GET.get("exclude")
    if exclude_id and exclude_id.isdigit():
        products = products.exclude(pk=int(exclude_id))
    if query:
        products = products.filter(Q(title__icontains=query) | Q(group__title__icontains=query))
    results = [
        {"id": item.pk, "text": f"{item.title} — {item.group.title}"}
        for item in products.order_by("title")[:20]
    ]
    return JsonResponse({"results": results})


@login_required
def product_tech_packs_json(request, pk):
    from cms.services import serialize_product_tech_packs

    product = get_object_or_404(Product, pk=pk)
    return JsonResponse({"packs": serialize_product_tech_packs(product)})


def _parse_tech_packs_payload(raw):
    import json

    if raw in (None, ""):
        return True, []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return False, []
    if not isinstance(data, list):
        return False, []
    return True, data


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
    items = SurfaceItem.objects.select_related("surface_type").order_by(
        "surface_type__sort_order", "sort_order", "title"
    )
    return render(
        request,
        "cms/surface_list.html",
        _panel_context(
            "surfaces",
            "Barwy i powierzchnie",
            items=items,
            surface_types=SurfaceType.objects.order_by("sort_order", "name"),
        ),
    )


@login_required
def surface_edit(request, pk=None):
    instance = get_object_or_404(SurfaceItem, pk=pk) if pk else None
    form = SurfaceItemForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Barwa / powierzchnia została zapisana.")
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
def surface_category_edit(request, pk=None):
    return redirect("cms_surfaces")


@login_required
def surface_type_edit(request, pk=None):
    instance = get_object_or_404(SurfaceType, pk=pk) if pk else None
    form = SurfaceTypeForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grupa produktowa została zapisana.")
        return redirect("cms_surfaces")
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "surfaces",
            "Edycja grupy produktowej" if instance else "Nowa grupa produktowa",
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
            delete_model="tip",
            columns=[("title", "Tytuł"), ("published_at", "Data")],
        ),
    )


@login_required
def tip_edit(request, pk=None):
    instance = get_object_or_404(Tip, pk=pk) if pk else None
    form = TipForm(request.POST or None, request.FILES or None, instance=instance)
    gallery_bound = request.method == "POST" and "gallery-TOTAL_FORMS" in request.POST
    gallery_formset = TipGalleryFormSet(
        request.POST if gallery_bound else None,
        request.FILES if gallery_bound else None,
        instance=instance, prefix="gallery",
    )
    if request.method == "POST" and form.is_valid() and (
        not gallery_bound or gallery_formset.is_valid()
    ):
        article = form.save()
        if gallery_bound:
            gallery_formset.instance = article
            gallery_formset.save()
        messages.success(request, "Porada została zapisana.")
        return redirect("cms_tips")
    return render(
        request,
        "cms/article_form.html",
        _panel_context(
            "tips",
            "Edycja porady" if instance else "Nowa porada",
            form=form,
            gallery_formset=gallery_formset,
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
            delete_model="news",
            columns=[("title", "Tytuł"), ("published_at", "Data")],
        ),
    )


@login_required
def news_edit(request, pk=None):
    instance = get_object_or_404(NewsPost, pk=pk) if pk else None
    form = NewsPostForm(request.POST or None, request.FILES or None, instance=instance)
    gallery_bound = request.method == "POST" and "gallery-TOTAL_FORMS" in request.POST
    gallery_formset = NewsGalleryFormSet(
        request.POST if gallery_bound else None,
        request.FILES if gallery_bound else None,
        instance=instance, prefix="gallery",
    )
    if request.method == "POST" and form.is_valid() and (
        not gallery_bound or gallery_formset.is_valid()
    ):
        article = form.save()
        if gallery_bound:
            gallery_formset.instance = article
            gallery_formset.save()
        messages.success(request, "Aktualność została zapisana.")
        return redirect("cms_news")
    return render(
        request,
        "cms/article_form.html",
        _panel_context(
            "news",
            "Edycja aktualności" if instance else "Nowa aktualność",
            form=form,
            gallery_formset=gallery_formset,
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
def download_move(request, pk, direction):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    item = get_object_or_404(DownloadItem, pk=pk)
    siblings = list(
        DownloadItem.objects.filter(category=item.category).order_by("sort_order", "title", "pk")
    )
    index = siblings.index(item)
    target_index = index - 1 if direction == "up" else index + 1
    if 0 <= target_index < len(siblings):
        siblings[index], siblings[target_index] = siblings[target_index], siblings[index]
        for order, sibling in enumerate(siblings):
            if sibling.sort_order != order:
                sibling.sort_order = order
                sibling.save(update_fields=["sort_order"])
    return redirect("cms_downloads")


@login_required
def document_list(request):
    return render(
        request, "cms/list.html",
        _panel_context(
            "documents", "Dokumenty",
            items=LegalDocument.objects.all(),
            add_url=reverse("cms_document_add"),
            edit_url_name="cms_document_edit",
            delete_model="document",
            columns=[("title", "Tytuł"), ("slug", "Slug")],
        ),
    )


@login_required
def document_edit(request, pk=None):
    instance = get_object_or_404(LegalDocument, pk=pk) if pk else None
    form = LegalDocumentForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dokument został zapisany.")
        return redirect("cms_documents")
    return render(
        request, "cms/form.html",
        _panel_context(
            "documents", "Edycja dokumentu" if instance else "Nowy dokument",
            form=form, back_url=reverse("cms_documents"),
        ),
    )


@login_required
def page_index(request):
    home_blocks = ContentBlock.objects.filter(group=ContentBlock.GROUP_HOME)
    about_blocks = ContentBlock.objects.filter(group=ContentBlock.GROUP_ABOUT)
    hero_slides = HeroSlide.objects.order_by("sort_order")
    sales_points = SalesPoint.objects.order_by("sort_order", "name")
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
            sales_points=sales_points,
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
            delete_model="job",
            columns=[("title", "Stanowisko"), ("location", "Lokalizacja")],
            back_url=reverse("cms_pages"),
        ),
    )


@login_required
def job_edit(request, pk=None):
    instance = get_object_or_404(JobOpening, pk=pk) if pk else None
    form = JobOpeningForm(request.POST or None, request.FILES or None, instance=instance)
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


@login_required
def promotions(request):
    return render(
        request,
        "cms/promotions.html",
        _panel_context(
            "promotions",
            "Promocje i formularze",
            promotion_slides=PromotionSlide.objects.all(),
            form_widgets=FormWidget.objects.all(),
            floating_promotions=FloatingPromotion.objects.all(),
        ),
    )


def _edit_model(request, model, form_class, pk, title, back_url, success):
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success)
        return redirect(back_url)
    return render(
        request,
        "cms/form.html",
        _panel_context(
            "promotions" if back_url == "cms_promotions" else "sales-points",
            title,
            form=form,
            back_url=reverse(back_url),
        ),
    )


@login_required
def promotion_slide_edit(request, pk=None):
    return _edit_model(
        request, PromotionSlide, PromotionSlideForm, pk,
        "Edycja komunikatu" if pk else "Nowy komunikat",
        "cms_promotions", "Komunikat został zapisany.",
    )


@login_required
def form_widget_edit(request, pk=None):
    return _edit_model(
        request, FormWidget, FormWidgetForm, pk,
        "Edycja widgetu formularza" if pk else "Nowy widget formularza",
        "cms_promotions", "Widget formularza został zapisany.",
    )


@login_required
def floating_promotion_edit(request, pk=None):
    return _edit_model(
        request, FloatingPromotion, FloatingPromotionForm, pk,
        "Edycja widgetu promocyjnego" if pk else "Nowy widget promocyjny",
        "cms_promotions", "Widget promocyjny został zapisany.",
    )


@login_required
def sales_point_list(request):
    return render(
        request,
        "cms/list.html",
        _panel_context(
            "sales-points", "Punkty sprzedaży",
            items=SalesPoint.objects.all().order_by("sort_name", "name"),
            add_url=reverse("cms_sales_point_add"),
            edit_url_name="cms_sales_point_edit",
            delete_model="sales-point",
            columns=[
                ("name", "Nazwa"),
                ("city", "Miejscowość"),
                ("voivodeship", "Województwo"),
                ("offer_type", "Oferta"),
            ],
        ),
    )


@login_required
def sales_point_edit(request, pk=None):
    return _edit_model(
        request, SalesPoint, SalesPointForm, pk,
        "Edycja punktu sprzedaży" if pk else "Nowy punkt sprzedaży",
        "cms_sales_points", "Punkt sprzedaży został zapisany.",
    )


@login_required
def submissions_export(request, pk):
    import csv

    widget = get_object_or_404(FormWidget, pk=pk)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="zgloszenia-{widget.slug}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "Data", "Imię", "Nazwisko", "Ulica", "Nr domu/mieszkania",
        "Kod pocztowy", "Miejscowość", "Firma", "Zgoda",
    ])
    for item in widget.submissions.all():
        writer.writerow([
            item.created_at.strftime("%Y-%m-%d %H:%M"), item.first_name,
            item.last_name, item.street, item.house_number, item.postal_code,
            item.city, item.company, "Tak" if item.consent else "Nie",
        ])
    return response


DELETE_MODELS = {
    "product": (Product, "cms_products"),
    "product-group": (ProductGroup, "cms_products"),
    "surface": (SurfaceItem, "cms_surfaces"),
    "surface-category": (SurfaceCategory, "cms_surfaces"),
    "surface-type": (SurfaceType, "cms_surfaces"),
    "tip": (Tip, "cms_tips"),
    "news": (NewsPost, "cms_news"),
    "download": (DownloadItem, "cms_downloads"),
    "download-category": (DownloadCategory, "cms_downloads"),
    "document": (LegalDocument, "cms_documents"),
    "content-block": (ContentBlock, "cms_pages"),
    "hero": (HeroSlide, "cms_pages"),
    "job": (JobOpening, "cms_jobs"),
    "promotion-slide": (PromotionSlide, "cms_promotions"),
    "form-widget": (FormWidget, "cms_promotions"),
    "floating-promotion": (FloatingPromotion, "cms_promotions"),
    "sales-point": (SalesPoint, "cms_sales_points"),
}


@login_required
def delete_object(request, model_name, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    model_config = DELETE_MODELS.get(model_name)
    if model_config is None:
        return HttpResponse(status=404)
    model, redirect_name = model_config
    get_object_or_404(model, pk=pk).delete()
    messages.success(request, "Pozycja została usunięta.")
    if model_name == "product-group":
        return redirect(f"{reverse(redirect_name)}?tab=kategorie")
    return redirect(redirect_name)
