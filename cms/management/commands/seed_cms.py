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
        self._seed_catalog_products()
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

    def _seed_catalog_products(self):
        samples = (
            (
                "mala-architektura",
                "cento",
                "Cento",
                "Palisada dekoracyjna",
                (
                    "<p>Smukła, wysoka palisada uzupełnia ofertę produktów do aranżacji "
                    "przestrzeni wokół domu. Sprawdzi się przy wykończeniu tarasów, schodów "
                    "oraz w miejscach, gdzie trzeba zniwelować różnice wysokości terenu.</p>"
                    "<p>Minimalistyczna forma i praktyczne barwy komponują się z kostkami "
                    "i płytami dekoracyjnymi Vestone.</p>"
                ),
                "<p>Format 100 × 30 cm, grubość 8 cm. Powierzchnia One Color i Gładka.</p>",
                Product.CARD_STANDARD,
                0,
            ),
            (
                "mala-architektura",
                "mersano",
                "Mersano",
                "Obrzeże dekoracyjne",
                (
                    "<p>Proste obrzeże z pozorną fugą, które nadaje formie lekkości. "
                    "Służy do wykańczania ścieżek, podjazdów, parkingów i tarasów, "
                    "a także do wytyczania rabat i niskich kwietników.</p>"
                    "<p>Odstępnik z jednej strony ułatwia montaż i równe fugi "
                    "między elementami.</p>"
                ),
                "<p>Format 50 × 28 cm, grubość 8 cm. Powierzchnia One Color i Gładka.</p>",
                Product.CARD_STANDARD,
                1,
            ),
            (
                "mala-architektura",
                "mersano-grande",
                "Mersano Grande",
                "Obrzeże dekoracyjne",
                (
                    "<p>Większe obrzeże z pozorną fugą do wykańczania ścieżek, podjazdów, "
                    "parkingów i tarasów. Nadaje się też do rabat i niskich kwietników.</p>"
                    "<p>Odstępnik z jednej strony ułatwia montaż i trzyma równą fugę.</p>"
                ),
                "<p>Format 45 × 40 cm, grubość 8 cm. Powierzchnia One Color i Gładka.</p>",
                Product.CARD_STANDARD,
                2,
            ),
            (
                "mala-architektura",
                "obrzeze-palisadowe-gladkie",
                "Obrzeże palisadowe gładkie",
                "Wykończenie nawierzchni",
                (
                    "<p>Praktyczny element do wykańczania nawierzchni z płyt i kostek, "
                    "ścieżek, podjazdów, parkingów i tarasów. Można nim też wyznaczyć "
                    "granicę zieleni albo wykończyć schody.</p>"
                ),
                "<p>Format 50 × 28 cm, grubość 6 cm. Powierzchnia One Color i Gładka.</p>",
                Product.CARD_STANDARD,
                3,
            ),
            (
                "mala-architektura",
                "stopien-schodowy",
                "Stopień schodowy",
                "Wejścia i tarasy",
                (
                    "<p>Duży, praktyczny stopień do wygodnych wejść. Nadaje się też "
                    "do wytyczenia granic zieleni i przestrzeni wypoczynkowej.</p>"
                    "<p>Komponuje się z kostkami i płytami w barwach melanżowych "
                    "i jednolitych.</p>"
                ),
                "<p>Format 100 × 35 cm, grubość 15 cm. Powierzchnia Gładka, Coloratto i One Color.</p>",
                Product.CARD_STANDARD,
                4,
            ),
            (
                "piasek-fugowy",
                "piasek-fugowy",
                "Piasek fugowy",
                "Naturalne piaski do fug",
                (
                    "<p>Naturalne piaski fugowe to ostatni element wpływający na wygląd "
                    "nawierzchni. Kolorem można podkreślić wzór ułożenia albo zbliżyć "
                    "całość do jednej tonacji. Barwa może się zmieniać pod wpływem pogody.</p>"
                    "<p>Piaski są wodoprzepuszczalne, jednoskładnikowe i w 100% naturalne. "
                    "Nie barwią powierzchni i ograniczają przerost traw i chwastów.</p>"
                    "<p>Rekomendowane do kostek Cortina, Grado, Lappare, Larino, Monte Carlo, "
                    "Wenecja oraz płyt Alicante, Desio, Ferrara i Lamezia. Piasek nie jest "
                    "materiałem konstrukcyjnym i stosuje się go na podbudowie wodoprzepuszczalnej. "
                    "Minimalna szerokość fugi to 3 mm.</p>"
                ),
                (
                    "<p>Dostępne frakcje: 0,1–0,5 mm kremowy, 0–2 mm pustynny, "
                    "0–2 mm bazaltowy, 0–2 mm stalowy. Worek 25 kg, 48 worków na palecie.</p>"
                ),
                Product.CARD_DESCRIPTIVE,
                0,
            ),
            (
                "beton-towarowy",
                "beton-towarowy",
                "Beton towarowy",
                "Beton od Budokrusz S.A.",
                (
                    "<p>Vestone to marka produktów nawierzchniowych Budokrusz S.A., "
                    "producenta betonu towarowego. W ofercie są między innymi beton "
                    "na płyty fundamentowe, beton drogowy nawierzchniowy oraz betony "
                    "specjalne: kontraktor, architektoniczny, SCC, ASCC, jamisty "
                    "i ekspansywny.</p>"
                    "<p>Szczegóły i ofertę cenową można dostać po zapytaniu.</p>"
                ),
                "",
                Product.CARD_DESCRIPTIVE,
                0,
            ),
        )
        for group_slug, slug, title, subtitle, description, extra, card_type, sort_order in samples:
            group = ProductGroup.objects.filter(slug=group_slug).first()
            if group is None:
                continue
            Product.objects.get_or_create(
                group=group,
                slug=slug,
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "description": description,
                    "description_extra": extra,
                    "card_type": card_type,
                    "sort_order": sort_order,
                    "is_active": True,
                    "show_main_image": False,
                },
            )

    def _seed_tips(self):
        samples = (
            ("testowa-porada", "Testowa porada"),
            ("testowa-porada-2", "Układanie kostki na podjeździe"),
            ("testowa-porada-3", "Pielęgnacja płyt tarasowych"),
        )
        for slug, title in samples:
            if Tip.objects.filter(is_published=True).count() >= 3:
                return
            Tip.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "excerpt": LOREM,
                    "body": LOREM_LONG,
                    "published_at": date.today(),
                    "is_published": True,
                },
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
