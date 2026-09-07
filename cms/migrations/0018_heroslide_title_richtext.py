from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0017_product_colors_legacy_tech"),
    ]

    operations = [
        migrations.AlterField(
            model_name="heroslide",
            name="title",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Opcjonalny. Pogrubienie i kursywa w pasku narzędzi. "
                    "Zostaw pusty razem z leadem, jeśli slajd ma być samym zdjęciem."
                ),
                verbose_name="Tytuł",
            ),
        ),
    ]
