from django.conf import settings
from django.utils.formats import date_format
from django.utils.html import strip_tags


def _media_url(file_field):
    if file_field and hasattr(file_field, "url"):
        return file_field.url
    return None


def _image_url(file_field, fallback):
    url = _media_url(file_field)
    return url or fallback


def _richtext_or_empty(value):
    if not value:
        return ""
    if not strip_tags(value).strip():
        return ""
    return value


def get_placeholder():
    from website.content_data import PLACEHOLDER_IMG

    return PLACEHOLDER_IMG


def get_site_settings():
    from cms.models import SiteSettings

    defaults = {
        "phone": "+48 22 755 50 44",
        "email": "informacja@vestone.pl",
        "infoline": "518 518 518",
        "address": "Budokrusz S.A. Odrano Wola\nul. Osowiecka 47\n05-825 Grodzisk Mazowiecki",
        "footer_tagline": (
            "Kostka brukowa, płyty tarasowe i rozwiązania do przestrzeni na zewnątrz."
        ),
    }
    if not SiteSettings.objects.exists():
        return _site_settings_payload(defaults)

    settings_obj = SiteSettings.load()
    data = {
        "phone": settings_obj.phone or defaults["phone"],
        "email": settings_obj.email or defaults["email"],
        "infoline": settings_obj.infoline or defaults["infoline"],
        "address": settings_obj.address or defaults["address"],
        "footer_tagline": settings_obj.footer_tagline or defaults["footer_tagline"],
    }
    return _site_settings_payload(data)


def _contact_href(value):
    cleaned = "".join(ch for ch in (value or "") if ch.isdigit() or ch == "+")
    return f"tel:{cleaned}" if cleaned else ""


def _site_settings_payload(data):
    email = data["email"]
    return {
        **data,
        "phone_href": _contact_href(data["phone"]),
        "infoline_href": _contact_href(data["infoline"]),
        "email_href": f"mailto:{email}" if email else "",
    }


def _merge_content_block(blocks, key, defaults):
    data = {**defaults, **(blocks.get(key) or {})}
    for field, value in defaults.items():
        if not data.get(field):
            data[field] = value
    return data


def get_content_block(key, fallback=None):
    from cms.models import ContentBlock

    block = ContentBlock.objects.filter(key=key, is_active=True).first()
    if block is None:
        return fallback or {}
    placeholder = get_placeholder()
    return {
        "key": block.key,
        "title": block.title,
        "subtitle": block.subtitle,
        "body": block.body,
        "body_extra": block.body_extra,
        "image": _image_url(block.image, placeholder),
        "button_label": block.button_label,
        "button_url": block.button_url,
    }


def get_content_blocks_by_group(group):
    from cms.models import ContentBlock

    blocks = ContentBlock.objects.filter(group=group, is_active=True)
    placeholder = get_placeholder()
    return {
        block.key: {
            "title": block.title,
            "subtitle": block.subtitle,
            "body": block.body,
            "body_extra": block.body_extra,
            "image": _image_url(block.image, placeholder),
            "button_label": block.button_label,
            "button_url": block.button_url,
        }
        for block in blocks
    }


def get_hero_slides():
    from cms.models import HeroSlide

    placeholder = get_placeholder()
    slides = HeroSlide.objects.filter(is_active=True)
    if not slides.exists():
        return [
            {
                "title": "Lorem ipsum dolor sit amet",
                "lead": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "image": placeholder,
                "mobile_image": placeholder,
                "media_type": "image",
            }
        ]
    return [
        {
            "title": slide.title,
            "lead": slide.lead,
            "image": _image_url(slide.image, placeholder),
            "mobile_image": _image_url(slide.mobile_image, _image_url(slide.image, placeholder)),
            "media_type": slide.media_type,
            "video": _media_url(slide.video) or slide.video_url,
            "button_label": slide.button_label,
            "button_url": slide.button_url,
        }
        for slide in slides
    ]


def get_promotion_slides():
    from django.db.models import Q
    from django.utils import timezone
    from cms.models import PromotionSlide

    now = timezone.now()
    slides = PromotionSlide.objects.filter(is_active=True).filter(
        Q(active_from__isnull=True) | Q(active_from__lte=now),
        Q(active_until__isnull=True) | Q(active_until__gte=now),
    )
    return [
        {"text": item.text, "link_label": item.link_label, "link_url": item.link_url}
        for item in slides
    ]


def get_sales_points():
    from urllib.parse import quote_plus
    from cms.models import SalesPoint

    return [
        {
            "name": point.name,
            "address": point.address,
            "phone": point.phone,
            "email": point.email,
            "website_url": point.website_url,
            "offer_type": point.offer_type,
            "pin": "img/pin-red.png" if point.offer_type == SalesPoint.OFFER_MUSSO else "img/pin-grey.png",
            "route_url": f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(point.address)}",
        }
        for point in SalesPoint.objects.filter(is_active=True)
    ]


def get_floating_promotions():
    from cms.models import FloatingPromotion

    return [
        {
            "placement": item.placement,
            "image": _media_url(item.image),
            "link_url": item.link_url,
        }
        for item in FloatingPromotion.objects.filter(is_active=True)
        if item.image
    ]


def get_reviews():
    from cms.models import Review

    reviews = Review.objects.filter(is_active=True)
    if not reviews.exists():
        return [
            {"quote": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "author": "Jan K."},
            {"quote": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "author": "Anna M."},
        ]
    return [{"quote": r.quote, "author": r.author} for r in reviews]


def get_product_groups():
    from cms.models import ProductGroup

    groups = ProductGroup.objects.filter(is_active=True)
    placeholder = get_placeholder()
    if groups.exists():
        return [
            {
                "slug": group.slug,
                "title": group.title,
                "image": _image_url(group.image, placeholder),
            }
            for group in groups
        ]
    from website.content_data import PRODUCT_GROUPS

    return [{**group, "image": placeholder} for group in PRODUCT_GROUPS]


def get_product_group(slug):
    for group in get_product_groups():
        if group["slug"] == slug:
            return group
    return None


def _pin_coord(value):
    return format(float(value), ".2f")


def _product_dict(product, placeholder):
    attributes = [
        {
            "label": assignment.option.attribute.name,
            "value": assignment.option.value,
            "slug": assignment.option.attribute.slug,
        }
        for assignment in product.attribute_assignments.select_related(
            "option__attribute"
        ).all()
    ]
    specs = []
    specs_by_slug = {}
    for attribute in attributes:
        if attribute["slug"] not in specs_by_slug:
            spec = {"label": attribute["label"], "values": [], "slug": attribute["slug"]}
            specs_by_slug[attribute["slug"]] = spec
            specs.append(spec)
        if attribute["value"] not in specs_by_slug[attribute["slug"]]["values"]:
            specs_by_slug[attribute["slug"]]["values"].append(attribute["value"])

    return {
        "slug": product.slug,
        "title": product.title,
        "category_slug": product.group.slug,
        "subtitle": product.subtitle,
        "card_type": product.card_type,
        "description": _richtext_or_empty(product.description),
        "description_extra": _richtext_or_empty(product.description_extra),
        "image": _image_url(product.image, placeholder),
        "show_main_image": product.show_main_image,
        "show_packshot": product.show_packshot,
        "packshot_columns": product.packshot_columns,
        "packshots": [
            {
                "image": _media_url(item.image),
                "caption": (item.caption or "").strip(),
            }
            for item in product.packshots.all()
            if item.image and getattr(item.image, "name", None)
        ],
        "attributes": attributes,
        "specs": specs,
        "pins": [
            {"x": _pin_coord(pin.x), "y": _pin_coord(pin.y), "text": pin.text}
            for pin in product.pins.all()
            if pin.gallery_image_id is None
        ],
        "gallery": [
            {
                "alt": image.alt or product.title,
                "image": _image_url(image.image, placeholder),
                "pins": [
                    {"x": _pin_coord(pin.x), "y": _pin_coord(pin.y), "text": pin.text}
                    for pin in image.pins.all()
                ]
                if image.pins_enabled
                else [],
            }
            for image in product.gallery.all()
            if image.image
        ],
    }


def _product_filter_values(product):
    values = {}
    for assignment in product.attribute_assignments.select_related("option__attribute").all():
        attribute = assignment.option.attribute
        if attribute.show_in_filters:
            values[attribute.slug] = assignment.option.value
    return values


def _product_list_search_text(product):
    parts = [product.title, product.group.title if product.group_id else ""]
    for assignment in product.attribute_assignments.select_related("option").all():
        parts.append(assignment.option.value)
    return " ".join(part for part in parts if part).lower()


def category_products(category_slug):
    from cms.models import Product

    products = Product.objects.filter(
        group__slug=category_slug,
        is_active=True,
        group__is_active=True,
    ).select_related("group").prefetch_related(
        "attribute_assignments__option__attribute",
        "pins",
        "gallery",
    )
    if products.exists():
        return [
            {
                "slug": product.slug,
                "title": product.title,
                "category_slug": category_slug,
                "search_text": _product_list_search_text(product),
                "filter_values": _product_filter_values(product),
                "image": _image_url(product.image, get_placeholder()),
            }
            for product in products
        ]
    from website.content_data import category_products as static_products

    return [
        {
            **item,
            "search_text": item.get("search_text") or item.get("title", "").lower(),
            "filter_values": item.get("filter_values") or {},
        }
        for item in static_products(category_slug)
    ]


def get_product(category_slug, product_slug):
    from cms.models import Product

    placeholder = get_placeholder()
    product = (
        Product.objects.filter(
            group__slug=category_slug,
            slug=product_slug,
            is_active=True,
        )
        .select_related("group")
        .prefetch_related(
            "attribute_assignments__option__attribute",
            "pins",
            "gallery",
            "gallery__pins",
        )
        .first()
    )
    if product:
        data = _product_dict(product, placeholder)
        data["category_slug"] = category_slug
        return data

    from website.content_data import TEST_PRODUCT, TEST_PRODUCT_SLUG

    if product_slug == TEST_PRODUCT_SLUG:
        return {**TEST_PRODUCT, "category_slug": category_slug}
    return None


def get_related_products(product=None, exclude_slug=None, category_slug=None, limit=4):
    from cms.models import Product

    placeholder = get_placeholder()
    if product is None and exclude_slug:
        product = Product.objects.filter(
            slug=exclude_slug,
            group__slug=category_slug,
        ).first()
    if product and product.pk and product.related_products.filter(is_active=True).exists():
        qs = product.related_products.filter(is_active=True, group__is_active=True).select_related("group")
    else:
        qs = Product.objects.filter(is_active=True).select_related("group")
    if exclude_slug:
        qs = qs.exclude(slug=exclude_slug)
    if qs.exists():
        return [
            {
                "slug": product.slug,
                "title": product.title,
                "category_slug": product.group.slug,
                "image": _image_url(product.image, placeholder),
            }
            for product in qs[:limit]
        ]
    from website.content_data import RELATED_PRODUCTS

    return RELATED_PRODUCTS[:limit]


def get_surface_items():
    from cms.models import SurfaceItem

    placeholder = get_placeholder()
    items = SurfaceItem.objects.filter(is_active=True).select_related(
        "category", "category__parent", "surface_type"
    )
    if items.exists():
        return [
            {
                "slug": item.slug,
                "title": item.title,
                "image": _image_url(item.image, placeholder),
                "category": item.category.name if item.category else "",
                "category_section": (
                    item.category.parent.name
                    if item.category and item.category.parent
                    else (item.category.name if item.category else "")
                ),
                "surface_type": item.surface_type.name if item.surface_type else "",
                "surface_icon": _media_url(item.surface_type.icon) if item.surface_type else None,
                "surface_description": item.surface_type.description if item.surface_type else "",
                "product_kind": item.get_product_kind_display() if item.product_kind else "",
                "thickness": item.thickness,
                "application": item.application,
                "load_capacity": item.load_capacity,
                "filter_values": {
                    "grubosc": item.thickness,
                    "powierzchnia": item.surface_type.name if item.surface_type else item.surface,
                    "rodzaj-produktu": item.get_product_kind_display() if item.product_kind else "",
                    "zastosowanie": item.application,
                    "nosnosc": item.load_capacity,
                },
                "search_text": " ".join(
                    part
                    for part in (
                        item.title,
                        item.color,
                        item.surface,
                        item.surface_type.name if item.surface_type else "",
                        item.get_product_kind_display() if item.product_kind else "",
                        item.format_size,
                        item.thickness,
                        item.application,
                        item.load_capacity,
                    )
                    if part
                ).lower(),
            }
            for item in items
        ]
    return []


def get_surface_filters():
    items = get_surface_items()
    definitions = [
        ("grubosc", "Grubość"),
        ("powierzchnia", "Rodzaj powierzchni"),
        ("rodzaj-produktu", "Rodzaj produktu"),
        ("zastosowanie", "Zastosowanie"),
        ("nosnosc", "Nośność"),
    ]
    filters = []
    for name, label in definitions:
        values = sorted(
            {item["filter_values"].get(name, "") for item in items if item["filter_values"].get(name)}
        )
        if values:
            filters.append({"name": name, "label": label, "options": [label, *values]})
    return filters


def _article_dict(article, placeholder):
    return {
        "slug": article.slug,
        "title": article.title,
        "excerpt": article.excerpt,
        "body": article.body,
        "date": article.published_at.isoformat(),
        "date_display": date_format(article.published_at, "d.m.Y"),
        "image": _image_url(article.image, placeholder),
        "gallery": [
            {
                "image": _media_url(item.image),
                "alt": item.alt or article.title,
                "layout": item.layout,
            }
            for item in article.gallery.all()
            if item.image
        ],
    }


def get_tips():
    from cms.models import Tip

    placeholder = get_placeholder()
    tips = Tip.objects.filter(is_published=True).prefetch_related("gallery")
    if tips.exists():
        return [_article_dict(tip, placeholder) for tip in tips]
    from website.content_data import TIPS_POSTS

    return TIPS_POSTS


def get_tip(slug):
    for tip in get_tips():
        if tip["slug"] == slug:
            return tip
    return None


def get_news():
    from cms.models import NewsPost

    placeholder = get_placeholder()
    posts = NewsPost.objects.filter(is_published=True).prefetch_related("gallery")
    if posts.exists():
        return [_article_dict(post, placeholder) for post in posts]
    from website.content_data import NEWS_POSTS

    return NEWS_POSTS


def get_news_post(slug):
    for post in get_news():
        if post["slug"] == slug:
            return post
    return None


def get_job_openings():
    from cms.models import JobOpening

    jobs = JobOpening.objects.filter(is_active=True)
    if jobs.exists():
        return [
            {
                "id": job.pk,
                "slug": job.slug,
                "title": job.title,
                "location": job.location,
                "type": job.employment_type,
                "excerpt": job.excerpt,
                "body": job.body,
                "image": _media_url(job.image),
            }
            for job in jobs
        ]
    from website.content_data import JOB_OPENINGS

    return JOB_OPENINGS


def get_download_categories():
    from cms.models import DownloadCategory

    categories = DownloadCategory.objects.all()
    if categories.exists():
        return [{"id": "all", "label": "Wszystkie"}] + [
            {"id": category.slug, "label": category.label} for category in categories
        ]
    from website.content_data import DOWNLOAD_CATEGORIES

    return DOWNLOAD_CATEGORIES


def get_download_groups():
    from cms.models import DownloadCategory

    categories = DownloadCategory.objects.all()
    if categories.exists():
        return [{"id": category.slug, "label": category.label} for category in categories]
    from website.content_data import DOWNLOAD_GROUPS

    return DOWNLOAD_GROUPS


def get_download_items():
    from cms.models import DownloadItem

    placeholder = get_placeholder()
    items = DownloadItem.objects.filter(is_published=True).select_related("category")
    if items.exists():
        result = []
        for item in items:
            file_url = _media_url(item.file) or "#"
            result.append(
                {
                    "category": item.category.slug,
                    "title": item.title,
                    "file_number": item.file_number,
                    "file": file_url,
                    "kind": item.kind,
                }
            )
        return result
    from website.content_data import DOWNLOAD_ITEMS

    return DOWNLOAD_ITEMS


def get_product_filters(category_slug=None):
    from cms.models import Product, ProductAttribute

    attributes = ProductAttribute.objects.filter(show_in_filters=True).order_by(
        "sort_order", "name"
    )
    if category_slug:
        product_ids = Product.objects.filter(
            group__slug=category_slug,
            is_active=True,
            group__is_active=True,
        ).values_list("pk", flat=True)
        attributes = attributes.filter(
            options__assignments__product_id__in=product_ids
        ).distinct()

    filters = []
    for attribute in attributes:
        values_qs = attribute.options.filter(
            assignments__product__is_active=True,
        )
        if category_slug:
            values_qs = values_qs.filter(
                assignments__product__group__slug=category_slug,
                assignments__product__group__is_active=True,
            )
        values = list(
            values_qs.order_by("sort_order", "value")
            .values_list("value", flat=True)
            .distinct()
        )
        if not values:
            continue
        filters.append(
            {
                "name": attribute.slug,
                "label": attribute.name,
                "options": [attribute.name, *values],
            }
        )
    return filters


def get_home_context():
    placeholder = get_placeholder()
    blocks = get_content_blocks_by_group("home")
    about_blocks = get_content_blocks_by_group("about")
    return {
        "placeholder_img": placeholder,
        "product_groups": get_product_groups(),
        "hero_slides": get_hero_slides(),
        "promotion_slides": get_promotion_slides(),
        "floating_promotions": get_floating_promotions(),
        "sales_points": get_sales_points(),
        "products_section": _merge_content_block(
            blocks,
            "home-products-lead",
            {
                "title": "Nasze produkty",
                "body": (
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio "
                    "praesent libero sed cursus ante dapibus diam."
                ),
                "button_label": "Zobacz wszystkie",
                "button_url": "/produkty/",
            },
        ),
        "about_section": _merge_content_block(
            blocks,
            "home-about",
            {
                "title": "O nas",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "body_extra": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "image": placeholder,
                "button_label": "Czytaj więcej",
                "button_url": "/#o-nas",
            },
        ),
        "news_section": _merge_content_block(
            blocks,
            "home-news-lead",
            {
                "title": "Aktualności",
                "body": (
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                    "Praesent commodo cursus magna."
                ),
                "button_label": "Zobacz wszystkie",
                "button_url": "/o-nas/aktualnosci/",
            },
        ),
        "map_section": _merge_content_block(
            blocks,
            "home-map",
            {
                "title": "Gdzie kupić",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "button_label": "Sprawdź",
                "button_url": "/gdzie-kupic/",
                "image": placeholder,
            },
        ),
        "tips_section": _merge_content_block(
            blocks,
            "home-tips-lead",
            {
                "title": "Porady",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "button_label": "Zobacz wszystkie",
                "button_url": "/porady/",
            },
        ),
        "contact_section": _merge_content_block(
            blocks,
            "home-contact",
            {
                "title": "Kontakt",
                "body": (
                    "<p><strong>DZIAŁ HANDLOWY i DZIAŁ KSIĘGOWY</strong><br>"
                    '<a href="tel:+48227555440">48 755 54 40</a><br>'
                    '<a href="mailto:informacja@vestone.pl">informacja@vestone.pl</a></p>'
                ),
                "image": placeholder,
            },
        ),
        "about_pages": about_blocks,
        "featured_tips": get_tips(),
        "featured_news": get_news(),
    }


def _review_slides(reviews):
    if not reviews:
        return [
            [
                {"quote": "Lorem ipsum dolor sit amet.", "author": "Jan K."},
                {"quote": "Sed do eiusmod tempor incididunt.", "author": "Anna M."},
            ]
        ]
    slides = []
    for index in range(0, len(reviews), 2):
        slides.append(reviews[index : index + 2])
    return slides
