from datetime import date, timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cms.models import (
    FormSubmission,
    FormWidget,
    LegalDocument,
    Product,
    ProductGalleryImage,
    ProductPackshotImage,
    ProductGroup,
    ProductPin,
    PromotionSlide,
    Tip,
    TipGalleryImage,
    DownloadCategory,
    DownloadItem,
    SurfaceItem,
    SurfaceType,
)
from cms.services import (
    get_download_items,
    get_product,
    get_promotion_slides,
    get_related_products,
    get_surface_filters,
    get_tip,
)


class PromotionSlideTests(TestCase):
    def test_only_current_slides_are_returned(self):
        now = timezone.now()
        PromotionSlide.objects.create(text="Aktywny", is_active=True)
        PromotionSlide.objects.create(
            text="Przyszły", is_active=True, active_from=now + timedelta(days=1)
        )
        PromotionSlide.objects.create(
            text="Zakończony", is_active=True, active_until=now - timedelta(days=1)
        )
        self.assertEqual([item["text"] for item in get_promotion_slides()], ["Aktywny"])


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SITE_ACCESS_ENABLED=False,
)
class FormWidgetTests(TestCase):
    def setUp(self):
        self.widget = FormWidget.objects.create(
            slug="probka",
            title="Zamów próbkę",
            recipient_email="test@example.com",
            consent_text="Wyrażam zgodę.",
        )
        self.url = reverse("form_widget", kwargs={"slug": self.widget.slug})
        self.data = {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "street": "Testowa",
            "house_number": "1",
            "postal_code": "00-001",
            "city": "Warszawa",
            "company": "",
        }

    def test_consent_is_required(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_valid_submission_is_saved_and_emailed(self):
        response = self.client.post(self.url, {**self.data, "consent": "on"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dziękujemy")
        self.assertEqual(FormSubmission.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])


class ProductExtensionsTests(TestCase):
    def setUp(self):
        self.group = ProductGroup.objects.create(title="Płyty", slug="plyty")
        self.product = Product.objects.create(
            group=self.group,
            title="Produkt A",
            slug="produkt-a",
            image="products/a.jpg",
            show_main_image=False,
            show_packshot=True,
            packshot_columns=3,
        )
        ProductPackshotImage.objects.create(
            product=self.product,
            image="products/packshot.jpg",
            caption="Wariant jasny",
            sort_order=0,
        )

    def test_gallery_image_has_own_pins(self):
        gallery = ProductGalleryImage.objects.create(
            product=self.product,
            image="products/gallery.jpg",
            alt="Detal",
            pins_enabled=True,
        )
        ProductPin.objects.create(
            product=self.product, gallery_image=gallery, x=25, y=75, text="Detal pinu"
        )
        data = get_product("plyty", "produkt-a")
        self.assertFalse(data["show_main_image"])
        self.assertTrue(data["show_packshot"])
        self.assertEqual(data["packshot_columns"], 3)
        self.assertEqual(data["packshots"][0]["caption"], "Wariant jasny")
        self.assertEqual(data["gallery"][0]["pins"][0]["text"], "Detal pinu")
        self.assertEqual(data["card_type"], "standard")

        gallery.pins_enabled = False
        gallery.save(update_fields=["pins_enabled"])
        data = get_product("plyty", "produkt-a")
        self.assertEqual(data["gallery"][0]["pins"], [])

    def test_selected_related_products_are_preferred(self):
        related = Product.objects.create(
            group=self.group, title="Produkt B", slug="produkt-b", image="products/b.jpg"
        )
        self.product.related_products.add(related)
        result = get_related_products(product=self.product)
        self.assertEqual([item["slug"] for item in result], ["produkt-b"])


class SurfaceFilterTests(TestCase):
    def test_surface_filters_cover_required_fields(self):
        surface_type = SurfaceType.objects.get(slug="top-arte")
        SurfaceItem.objects.create(
            title="Opal",
            slug="opal",
            surface_type=surface_type,
            product_kind=SurfaceItem.KIND_PAVING,
            thickness="8 cm",
            application="Podjazd",
            load_capacity="Samochody osobowe",
        )
        names = {item["name"] for item in get_surface_filters()}
        self.assertEqual(
            names,
            {"grubosc", "powierzchnia", "rodzaj-produktu", "zastosowanie", "nosnosc"},
        )


class ContentModuleTests(TestCase):
    def test_tip_gallery_is_exposed_to_article_view(self):
        tip = Tip.objects.create(
            title="Porada", slug="porada", published_at=date.today(), is_published=True
        )
        TipGalleryImage.objects.create(
            article=tip, image="articles/gallery.jpg", layout="half"
        )
        data = get_tip("porada")
        self.assertEqual(data["gallery"][0]["layout"], "half")

    def test_download_number_is_exposed(self):
        category = DownloadCategory.objects.create(label="Katalogi", slug="katalogi")
        DownloadItem.objects.create(
            category=category,
            title="Katalog",
            file_number="KAT-01",
            file="downloads/katalog.pdf",
        )
        item = next(item for item in get_download_items() if item["title"] == "Katalog")
        self.assertEqual(item["file_number"], "KAT-01")

    @override_settings(SITE_ACCESS_ENABLED=False)
    def test_legal_document_content_is_rendered(self):
        document = LegalDocument.objects.get(slug="polityka-prywatnosci")
        document.body = "<p>Treść dokumentu</p>"
        document.save()
        response = self.client.get("/dokumenty/polityka-prywatnosci/")
        self.assertContains(response, "Treść dokumentu")
