from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0021_emailsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="surfacetype",
            name="icon",
            field=models.ImageField(
                blank=True,
                help_text="Mała ikona przy produktach na stronie koloru (np. TOP ARTE, AVANGARDE).",
                upload_to="cms/surfaces/icons/",
                verbose_name="Ikona rodzaju powierzchni",
            ),
        ),
    ]
