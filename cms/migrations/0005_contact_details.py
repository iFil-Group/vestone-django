from django.db import migrations


CONTACT_BODY = (
    "<p><strong>DZIAŁ HANDLOWY i DZIAŁ KSIĘGOWY</strong><br>"
    '<a href="tel:+48227555440">48 755 54 40</a><br>'
    '<a href="mailto:informacja@vestone.pl">informacja@vestone.pl</a></p>'
)


def set_contact_details(apps, schema_editor):
    ContentBlock = apps.get_model("cms", "ContentBlock")
    ContentBlock.objects.update_or_create(
        key="home-contact",
        defaults={
            "group": "home",
            "label": "Kontakt — treść",
            "title": "Kontakt",
            "body": CONTACT_BODY,
            "body_extra": "",
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("cms", "0004_home_about_and_news")]
    operations = [migrations.RunPython(set_contact_details, migrations.RunPython.noop)]
