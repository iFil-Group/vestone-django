from django.test import TestCase

from .forms import ProductForm
from .models import Product, ProductGroup


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
                "sort_order": 0,
                "is_active": "on",
            },
            instance=product,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        product.refresh_from_db()
        self.assertEqual(product.group, second)
