from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0018_heroslide_title_richtext"),
    ]

    operations = [
        migrations.AddField(
            model_name="floatingpromotion",
            name="seen_reset_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Wyczyszczono widoczność",
            ),
        ),
    ]
