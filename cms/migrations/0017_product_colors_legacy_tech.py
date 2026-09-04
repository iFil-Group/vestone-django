from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0016_homepage_promo_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="legacy_slugs",
            field=models.TextField(
                blank=True,
                help_text="Stare adresy produktu, po jednym w linii.",
                verbose_name="Poprzednie adresy",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="show_related_products",
            field=models.BooleanField(
                default=True,
                verbose_name="Pokaż „Sprawdź inne produkty”",
            ),
        ),
        migrations.AlterField(
            model_name="producttechrow",
            name="value",
            field=models.TextField(blank=True, verbose_name="Wartość"),
        ),
        migrations.AddField(
            model_name="producttechrow",
            name="icon_preset",
            field=models.CharField(
                blank=True,
                choices=[("", "Brak"), ("load", "Nośność")],
                max_length=20,
                verbose_name="Ikona",
            ),
        ),
        migrations.CreateModel(
            name="ProductColorImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        upload_to="cms/products/colors/",
                        verbose_name="Zdjęcie nawierzchni",
                    ),
                ),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Nazwa koloru",
                    ),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(default=0, verbose_name="Kolejność"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="colors",
                        to="cms.product",
                        verbose_name="Produkt",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kolor produktu",
                "verbose_name_plural": "Kolory produktu",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
