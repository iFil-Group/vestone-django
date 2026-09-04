from datetime import date

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from cms.models import (
    ContentBlock,
    FormWidget,
    HeroSlide,
    NewsPost,
    Product,
    ProductGroup,
    ProductAttribute,
    ProductAttributeAssignment,
    ProductAttributeOption,
    ProductPin,
    Review,
    SiteSettings,
    Tip,
)
from website import content_data

LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
LOREM_LONG = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
)


class Command(BaseCommand):
    help = "Uzupełnia brakujące dane startowe. Nie kasuje i nie nadpisuje treści z CMS."

    def handle(self, *args, **options):
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                pk=1,
                phone="+48 22 755 50 44",
                email="informacja@vestone.pl",
                infoline="518 518 518",
                address=(
                    "Budokrusz S.A. Odrano Wola\n"
                    "ul. Osowiecka 47\n"
                    "05-825 Grodzisk Mazowiecki"
                ),
                footer_tagline=(
                    "Kostka brukowa, płyty tarasowe i rozwiązania do przestrzeni na zewnątrz."
                ),
            )

        self._seed_content_blocks()
        self._seed_hero_slides()
        self._seed_reviews()
        self._seed_product_groups()
        self._seed_test_product()
        self._seed_tips()
        self._seed_news()
        self._seed_catalog_form()
        self.stdout.write(self.style.SUCCESS("CMS seed completed (missing defaults only)."))

    def _seed_content_blocks(self):
        blocks = [
            ("home-announce", ContentBlock.GROUP_HOME, "Pasek ogłoszeń", "", "", LOREM, "", "Sprawdź", "/porady/"),
            ("home-products-lead", ContentBlock.GROUP_HOME, "Nasze produkty — lead", "Nasze produkty", "", LOREM, "", "Zobacz wszystkie", "/produkty/"),
            ("home-about", ContentBlock.GROUP_HOME, "O nas (sekcja)", "O nas", "", LOREM, "", "VESTONE - TWOJA PRZESTRZEŃ", "/o-nas/"),
            ("home-news-lead", ContentBlock.GROUP_HOME, "Aktualności — lead", "Aktualności", "", LOREM, "", "Zobacz wszystkie", "/o-nas/aktualnosci/"),
            ("home-map", ContentBlock.GROUP_HOME, "Gdzie kupić (sekcja)", "Gdzie kupić", "", LOREM, "", "Sprawdź", "/gdzie-kupic/"),
            ("home-tips-lead", ContentBlock.GROUP_HOME, "Porady — lead", "Porady", "", LOREM, "", "Zobacz wszystkie", "/porady/"),
            (
                "home-contact",
                ContentBlock.GROUP_HOME,
                "Kontakt — treść",
                "Kontakt",
                "",
                '<p><strong>DZIAŁ HANDLOWY i DZIAŁ KSIĘGOWY</strong><br>'
                '<a href="tel:+48227555440">48 755 54 40</a><br>'
                '<a href="mailto:informacja@vestone.pl">informacja@vestone.pl</a></p>',
                "",
                "",
                "",
            ),
            (
                "products-cta", ContentBlock.GROUP_HOME, "Produkty — kafel kontaktowy",
                "Nie wiesz co wybrać?", "",
                "Skontaktuj się z nami, a pomożemy dobrać rozwiązanie.", "",
                "Skontaktuj się", "/#kontakt",
            ),
            ("page-warranty", ContentBlock.GROUP_ABOUT, "Warunki gwarancji", "Warunki gwarancji", "", LOREM_LONG, "", "", ""),
            ("page-media", ContentBlock.GROUP_ABOUT, "Dla mediów", "Dla mediów", "", LOREM_LONG, "", "", ""),
            ("page-careers-intro", ContentBlock.GROUP_ABOUT, "Praca i kariera — intro", "Praca i kariera", "", LOREM, "", "", ""),
            ("page-about-company", ContentBlock.GROUP_ABOUT, "O nas — pełna treść", "O nas", "VESTONE - TWOJA PRZESTRZEŃ", LOREM_LONG, LOREM, "", ""),
        ]
        for key, group, label, title, subtitle, body, body_extra, button_label, button_url in blocks:
            ContentBlock.objects.get_or_create(
                key=key,
                defaults={
                    "group": group,
                    "label": label,
                    "title": title,
                    "subtitle": subtitle,
                    "body": body,
                    "body_extra": body_extra,
                    "button_label": button_label,
                    "button_url": button_url,
                    "is_active": True,
                },
            )

    def _seed_hero_slides(self):
        if HeroSlide.objects.exists():
            return
        HeroSlide.objects.create(
            title=LOREM.capitalize(),
            lead=LOREM_LONG,
            sort_order=0,
            is_active=True,
        )

    def _seed_reviews(self):
        if Review.objects.exists():
            return
        Review.objects.bulk_create(
            [
                Review(quote=LOREM_LONG, author="Jan Kowalski", sort_order=0, is_active=True),
                Review(quote=LOREM, author="Anna Nowak", sort_order=1, is_active=True),
            ]
        )

    def _seed_product_groups(self):
        for index, group in enumerate(content_data.PRODUCT_GROUPS):
            ProductGroup.objects.get_or_create(
                slug=group["slug"],
                defaults={
                    "title": group["title"],
                    "sort_order": index,
                    "is_active": True,
                },
            )

    def _seed_test_product(self):
        if Product.objects.exists():
            return
        group = ProductGroup.objects.filter(slug="plyty-tarasowe").first()
        if group is None:
            return

        product, _ = Product.objects.get_or_create(
            group=group,
            slug=content_data.TEST_PRODUCT_SLUG,
            defaults={
                "title": "Produkt testowy #1",
                "subtitle": LOREM,
                "description": LOREM_LONG,
                "description_extra": LOREM,
                "is_active": True,
            },
        )

        if product.attribute_assignments.exists():
            return

        filter_slugs = {"format", "grubosc", "kolor", "powierzchnia"}
        for index, spec in enumerate(content_data.TEST_PRODUCT["specs"]):
            slug = slugify(spec["label"])
            attribute, _ = ProductAttribute.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": spec["label"],
                    "show_in_filters": slug in filter_slugs,
                    "sort_order": index,
                },
            )
            option, _ = ProductAttributeOption.objects.get_or_create(
                attribute=attribute,
                value=spec["value"],
                defaults={"sort_order": 0},
            )
            ProductAttributeAssignment.objects.get_or_create(
                product=product,
                option=option,
                defaults={"sort_order": index},
            )

        if not product.pins.exists():
            for index, pin in enumerate(content_data.TEST_PRODUCT["pins"]):
                ProductPin.objects.create(
                    product=product,
                    x=pin["x"],
                    y=pin["y"],
                    text=pin["text"],
                    sort_order=index,
                )

    def _seed_tips(self):
        if Tip.objects.exists():
            return
        Tip.objects.create(
            slug="testowa-porada",
            title="Testowa porada",
            excerpt=LOREM,
            body=LOREM_LONG,
            published_at=date.today(),
            is_published=True,
        )

    def _seed_news(self):
        if NewsPost.objects.exists():
            return
        NewsPost.objects.create(
            slug="testowa-aktualnosc",
            title="Testowa aktualność",
            excerpt=LOREM,
            body=LOREM_LONG,
            published_at=date.today(),
            is_published=True,
        )

    def _seed_catalog_form(self):
        FormWidget.objects.get_or_create(
            slug="zamow-katalog",
            defaults={
                "title": "Zamów katalog",
                "description": "<p>Wypełnij formularz, a wyślemy katalog.</p>",
                "recipient_email": "informacja@vestone.pl",
                "required_fields_text": "<p>Pola oznaczone gwiazdką są obowiązkowe.</p>",
                "consent_text": "Wyrażam zgodę na przetwarzanie danych osobowych w celu realizacji zamówienia katalogu.",
                "thanks_text": "<p>Dziękujemy. Skontaktujemy się w sprawie wysyłki katalogu.</p>",
                "is_active": True,
            },
        )
