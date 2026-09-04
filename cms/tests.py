from django.test import TestCase

from .forms import ProductForm, ProductPinFormSet
from .models import Product, ProductGalleryImage, ProductGroup, ProductPin


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
