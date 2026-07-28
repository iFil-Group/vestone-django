from django.db import migrations, models
import django.db.models.deletion


def forwards_migrate_packshot(apps, schema_editor):
    Product = apps.get_model("cms", "Product")
    ProductPackshotImage = apps.get_model("cms", "ProductPackshotImage")
    for product in Product.objects.exclude(packshot_image="").exclude(packshot_image=None):
        ProductPackshotImage.objects.create(
            product=product,
            image=product.packshot_image,
            caption="",
            sort_order=0,
        )


def backwards_migrate_packshot(apps, schema_editor):
    Product = apps.get_model("cms", "Product")
    ProductPackshotImage = apps.get_model("cms", "ProductPackshotImage")
    for product in Product.objects.all():
        first = (
            ProductPackshotImage.objects.filter(product=product)
            .exclude(image="")
            .order_by("sort_order", "id")
            .first()
        )
        if first:
            product.packshot_image = first.image
            product.save(update_fields=["packshot_image"])


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0010_product_card_type_gallery_pins"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductPackshotImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(blank=True, upload_to="cms/products/packshots/", verbose_name="Zdjęcie")),
                ("caption", models.CharField(blank=True, max_length=255, verbose_name="Podpis")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Kolejność")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="packshots",
                        to="cms.product",
                        verbose_name="Produkt",
                    ),
                ),
            ],
            options={
                "verbose_name": "Zdjęcie packshot",
                "verbose_name_plural": "Zdjęcia packshot",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddField(
            model_name="product",
            name="packshot_columns",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1 kolumna"), (2, "2 kolumny"), (3, "3 kolumny"), (4, "4 kolumny")],
                default=2,
                verbose_name="Liczba kolumn packshotów",
            ),
        ),
        migrations.RunPython(forwards_migrate_packshot, backwards_migrate_packshot),
        migrations.RemoveField(
            model_name="product",
            name="packshot_image",
        ),
    ]
