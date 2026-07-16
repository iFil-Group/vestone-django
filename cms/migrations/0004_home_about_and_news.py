from django.db import migrations


def migrate_home_content(apps, schema_editor):
    ContentBlock = apps.get_model("cms", "ContentBlock")
    home_about = ContentBlock.objects.filter(key="home-about").first()
    if home_about:
        full_body = home_about.body
        if home_about.body_extra:
            full_body = f"{full_body}\n\n{home_about.body_extra}".strip()
        ContentBlock.objects.update_or_create(
            key="page-about-company",
            defaults={
                "group": "about",
                "label": "O nas — pełna treść",
                "title": "O nas",
                "subtitle": "VESTONE - TWOJA PRZESTRZEŃ",
                "body": full_body,
                "is_active": True,
            },
        )
        home_about.button_label = "VESTONE - TWOJA PRZESTRZEŃ"
        home_about.button_url = "/o-nas/"
        home_about.body_extra = ""
        home_about.save(update_fields=["button_label", "button_url", "body_extra"])

    ContentBlock.objects.filter(key="home-reviews-lead").update(
        key="home-news-lead",
        label="Aktualności — lead",
        title="Aktualności",
        button_label="Zobacz wszystkie",
        button_url="/o-nas/aktualnosci/",
    )


class Migration(migrations.Migration):
    dependencies = [("cms", "0003_floatingpromotion_formwidget_promotionslide_and_more")]
    operations = [migrations.RunPython(migrate_home_content, migrations.RunPython.noop)]
