import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0012_surfaces_product_groups"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductTechPack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Nazwa")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Kolejność")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tech_packs",
                        to="cms.product",
                        verbose_name="Produkt",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paczka danych technicznych",
                "verbose_name_plural": "Paczki danych technicznych",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ProductTechRow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=200, verbose_name="Etykieta")),
                ("value", models.CharField(max_length=255, verbose_name="Wartość")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Kolejność")),
                (
                    "pack",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rows",
                        to="cms.producttechpack",
                        verbose_name="Paczka",
                    ),
                ),
            ],
            options={
                "verbose_name": "Wiersz danych technicznych",
                "verbose_name_plural": "Wiersze danych technicznych",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
