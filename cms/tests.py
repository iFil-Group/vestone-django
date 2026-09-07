from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import HeroSlideForm, ProductForm, ProductPinFormSet, PromotionSlideForm
from .models import (
    FloatingPromotion,
    HeroSlide,
    Product,
    ProductGalleryImage,
    ProductGroup,
    ProductPin,
    PromotionSlide,
    Tip,
)
from .services import get_hero_slides, get_promotion_slides, promotion_text_lines, unseen_floating_promotions
from .widgets import RichTextWidget


class ProductGroupAssignmentTests(TestCase):
    def test_product_can_be_moved_to_another_group(self):
        first = ProductGroup.objects.create(title="Pierwsza", slug="pierwsza")
        second = ProductGroup.objects.create(title="Druga", slug="druga")
        product = Product.objects.create(group=first, title="Test", slug="test")
        form = ProductForm(
            data={
                "card_type": Product.CARD_STANDARD,
                "group": second.pk,
                "title": product.title,
                "slug": product.slug,
                "subtitle": "",
                "description": "",
                "description_extra": "",
                "show_main_image": "on",
                "show_packshot": "",
                "packshot_columns": "2",
                "show_related_products": "on",
                "sort_order": 0,
                "is_active": "on",
            },
            instance=product,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        product.refresh_from_db()
        self.assertEqual(product.group, second)

    def test_slug_change_keeps_previous_address(self):
        group = ProductGroup.objects.create(title="Grupa", slug="grupa-slug")
        product = Product.objects.create(group=group, title="Nazwa", slug="stary-adres")
        product.slug = "nowy-adres"
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.slug, "nowy-adres")
        self.assertIn("stary-adres", product.legacy_slugs)


class ProductGalleryPinFormSetTests(TestCase):
    def setUp(self):
        self.group = ProductGroup.objects.create(title="Grupa", slug="grupa")
        self.product = Product.objects.create(
            group=self.group,
            title="Produkt",
            slug="produkt",
            image="products/main.jpg",
        )
        self.gallery = ProductGalleryImage.objects.create(
            product=self.product,
            image="products/gallery.jpg",
            pins_enabled=False,
        )

    def test_new_gallery_pins_validate_and_enable_pins(self):
        data = {
            "pins-TOTAL_FORMS": "1",
            "pins-INITIAL_FORMS": "0",
            "pins-MIN_NUM_FORMS": "0",
            "pins-MAX_NUM_FORMS": "1000",
            "pins-0-gallery_image": str(self.gallery.pk),
            "pins-0-gallery_pending": "",
            "pins-0-x": "12.5",
            "pins-0-y": "33.3",
            "pins-0-text": "Nowy pin galerii",
            "pins-0-sort_order": "0",
        }
        formset = ProductPinFormSet(data, instance=self.product, prefix="pins")
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()

        pin = ProductPin.objects.get(product=self.product, text="Nowy pin galerii")
        self.assertEqual(pin.gallery_image_id, self.gallery.pk)
        self.gallery.refresh_from_db()
        self.assertTrue(self.gallery.pins_enabled)

    def test_main_image_pins_still_validate_without_gallery(self):
        data = {
            "pins-TOTAL_FORMS": "1",
            "pins-INITIAL_FORMS": "0",
            "pins-MIN_NUM_FORMS": "0",
            "pins-MAX_NUM_FORMS": "1000",
            "pins-0-gallery_image": "",
            "pins-0-gallery_pending": "",
            "pins-0-x": "50",
            "pins-0-y": "50",
            "pins-0-text": "Pin główny",
            "pins-0-sort_order": "0",
        }
        formset = ProductPinFormSet(data, instance=self.product, prefix="pins")
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        self.assertTrue(
            ProductPin.objects.filter(
                product=self.product, gallery_image__isnull=True, text="Pin główny"
            ).exists()
        )

    def test_pending_gallery_pins_resolve_after_gallery_save(self):
        from cms.forms import ProductGalleryFormSet

        gallery_data = {
            "gallery-TOTAL_FORMS": "1",
            "gallery-INITIAL_FORMS": "1",
            "gallery-MIN_NUM_FORMS": "0",
            "gallery-MAX_NUM_FORMS": "1000",
            "gallery-0-id": str(self.gallery.pk),
            "gallery-0-alt": "",
            "gallery-0-pins_enabled": "",
            "gallery-0-sort_order": "0",
        }
        gallery_formset = ProductGalleryFormSet(
            gallery_data, instance=self.product, prefix="gallery"
        )
        self.assertTrue(gallery_formset.is_valid(), gallery_formset.errors)

        pin_data = {
            "pins-TOTAL_FORMS": "1",
            "pins-INITIAL_FORMS": "0",
            "pins-MIN_NUM_FORMS": "0",
            "pins-MAX_NUM_FORMS": "1000",
            "pins-0-gallery_image": "",
            "pins-0-gallery_pending": "0",
            "pins-0-x": "40",
            "pins-0-y": "60",
            "pins-0-text": "Pin na nowym zdjęciu",
            "pins-0-sort_order": "0",
        }
        pin_formset = ProductPinFormSet(pin_data, instance=self.product, prefix="pins")
        self.assertTrue(pin_formset.is_valid(), pin_formset.errors)

        gallery_formset.save()
        pin_formset.apply_pending_gallery_images(gallery_formset)
        pin_formset.save()

        pin = ProductPin.objects.get(text="Pin na nowym zdjęciu")
        self.assertEqual(pin.gallery_image_id, self.gallery.pk)
        self.gallery.refresh_from_db()
        self.assertTrue(self.gallery.pins_enabled)


class HeroSlideDisplayTests(TestCase):
    def test_form_title_uses_compact_rich_text(self):
        form = HeroSlideForm()
        widget = form.fields["title"].widget
        self.assertIsInstance(widget, RichTextWidget)
        self.assertTrue(widget.compact)

    def test_empty_title_and_lead_are_image_only(self):
        HeroSlide.objects.create(title="", lead="", is_active=True)
        slide = get_hero_slides()[0]
        self.assertEqual(slide["title"], "")
        self.assertEqual(slide["lead"], "")
        self.assertFalse(slide["has_copy"])

    def test_title_keeps_inline_markup(self):
        HeroSlide.objects.create(
            title="<p>Kostka <strong>brukowa</strong></p>",
            lead="",
            is_active=True,
        )
        slide = get_hero_slides()[0]
        self.assertEqual(slide["title"], "Kostka <strong>brukowa</strong>")
        self.assertTrue(slide["has_copy"])


class SeedCatalogProductsTests(TestCase):
    def test_seed_adds_vestone_core_products_to_empty_groups(self):
        call_command("seed_cms")
        self.assertTrue(
            Product.objects.filter(group__slug="mala-architektura", slug="cento").exists()
        )
        self.assertTrue(
            Product.objects.filter(group__slug="piasek-fugowy", slug="piasek-fugowy").exists()
        )
        self.assertTrue(
            Product.objects.filter(group__slug="beton-towarowy", slug="beton-towarowy").exists()
        )


class PromotionSlideFormTests(TestCase):
    def test_dates_stay_visible_when_editing(self):
        start = timezone.make_aware(datetime(2026, 9, 1, 10, 30))
        end = timezone.make_aware(datetime(2026, 9, 30, 18, 0))
        slide = PromotionSlide.objects.create(
            text="Linia A\nLinia B",
            link_label="Zamów",
            link_url="/zamow-katalog/",
            active_from=start,
            active_until=end,
        )
        form = PromotionSlideForm(instance=slide)
        self.assertEqual(form.fields["line_1"].initial, "Linia A")
        self.assertEqual(form.fields["line_2"].initial, "Linia B")
        html = form.as_p()
        self.assertIn('value="2026-09-01"', html)
        self.assertIn('value="2026-09-30"', html)

    def test_three_lines_are_saved_and_rotated(self):
        form = PromotionSlideForm(
            data={
                "line_1": "Pierwsza",
                "line_2": "Druga",
                "line_3": "Trzecia",
                "link_label": "Sprawdź",
                "link_url": "/zamow-katalog/",
                "active_from": "2026-09-01",
                "active_until": "2026-12-31",
                "sort_order": 0,
                "is_active": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        slide = form.save()
        self.assertEqual(slide.text, "Pierwsza\nDruga\nTrzecia")
        self.assertEqual(
            [item["text"] for item in get_promotion_slides()],
            ["Pierwsza", "Druga", "Trzecia"],
        )

    def test_html_text_splits_into_plain_lines(self):
        self.assertEqual(
            promotion_text_lines("<p>Raz</p><p>Dwa</p><p>Trzy</p><p>Cztery</p>"),
            ["Raz", "Dwa", "Trzy"],
        )


class FloatingPromotionClearTests(TestCase):
    def setUp(self):
        cache.clear()
        gif = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
            b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )
        self.promo = FloatingPromotion.objects.create(
            placement=FloatingPromotion.PLACEMENT_MODAL,
            image=SimpleUploadedFile("promo.gif", gif, content_type="image/gif"),
            link_url="/zamow-katalog/",
            is_active=True,
        )
        self.factory = RequestFactory()

    def test_reset_shows_promo_again(self):
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "203.0.113.10"
        first = unseen_floating_promotions(request)
        self.assertEqual(len(first), 1)
        second = unseen_floating_promotions(request)
        self.assertEqual(second, [])

        self.promo.seen_reset_at = timezone.now()
        self.promo.save(update_fields=["seen_reset_at"])
        again = unseen_floating_promotions(request)
        self.assertEqual(len(again), 1)
        self.assertNotEqual(again[0]["reset_token"], "0")

    def test_clear_button_updates_reset_time(self):
        user = get_user_model().objects.create_user("cms", "cms@example.com", "pass")
        self.client.force_login(user)
        response = self.client.post(
            reverse("cms_floating_promotion_clear", args=[self.promo.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.promo.refresh_from_db()
        self.assertIsNotNone(self.promo.seen_reset_at)

    def test_promotions_page_has_clear_action(self):
        user = get_user_model().objects.create_user("cms2", "cms2@example.com", "pass")
        self.client.force_login(user)
        response = self.client.get(reverse("cms_promotions"))
        self.assertContains(response, "Wyczyść")
        self.assertContains(response, reverse("cms_floating_promotion_clear", args=[self.promo.pk]))


class SeedTipsTests(TestCase):
    def test_seed_fills_up_to_three_tips(self):
        Tip.objects.create(
            slug="testowa-porada",
            title="Testowa porada",
            excerpt="x",
            body="x",
            published_at=date.today(),
            is_published=True,
        )
        call_command("seed_cms")
        self.assertGreaterEqual(Tip.objects.filter(is_published=True).count(), 3)
