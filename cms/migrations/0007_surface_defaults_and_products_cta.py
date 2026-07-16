from django.db import migrations


def create_defaults(apps, schema_editor):
    ContentBlock = apps.get_model("cms", "ContentBlock")
    SurfaceCategory = apps.get_model("cms", "SurfaceCategory")
    SurfaceType = apps.get_model("cms", "SurfaceType")
    SurfaceItem = apps.get_model("cms", "SurfaceItem")

    ContentBlock.objects.get_or_create(
        key="products-cta",
        defaults={
            "group": "home",
            "label": "Produkty — kafel kontaktowy",
            "title": "Nie wiesz co wybrać?",
            "body": "Skontaktuj się z nami, a pomożemy dobrać rozwiązanie.",
            "button_label": "Skontaktuj się",
            "button_url": "/#kontakt",
            "is_active": True,
        },
    )

    surfaces, _ = SurfaceCategory.objects.get_or_create(
        slug="nawierzchnie",
        defaults={"name": "Nawierzchnie", "sort_order": 0, "is_active": True},
    )
    for index, (name, slug) in enumerate(
        [
            ("Kostki brukowe", "kostki-brukowe"),
            ("Płyty dekoracyjne", "plyty-dekoracyjne"),
        ]
    ):
        SurfaceCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "parent": surfaces, "sort_order": index, "is_active": True},
        )
    for index, (name, slug) in enumerate(
        [
            ("Mała architektura", "mala-architektura"),
            ("Piaski fugowe", "piaski-fugowe"),
        ],
        start=1,
    ):
        SurfaceCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "sort_order": index, "is_active": True},
        )

    for index, (name, slug) in enumerate(
        [("TOP ARTE", "top-arte"), ("COLORATTO", "coloratto"), ("ONE COLOR", "one-color")]
    ):
        SurfaceType.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "sort_order": index, "is_active": True},
        )

    for item in SurfaceItem.objects.exclude(surface=""):
        surface_type = SurfaceType.objects.filter(name__iexact=item.surface).first()
        if surface_type:
            item.surface_type = surface_type
            item.save(update_fields=["surface_type"])


class Migration(migrations.Migration):
    dependencies = [("cms", "0006_surfacetype_product_packshot_image_and_more")]
    operations = [migrations.RunPython(create_defaults, migrations.RunPython.noop)]
