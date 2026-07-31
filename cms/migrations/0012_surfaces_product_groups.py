import django.db.models.deletion
from django.db import migrations, models


def forwards_migrate_surface_images(apps, schema_editor):
    SurfaceType = apps.get_model("cms", "SurfaceType")
    for group in SurfaceType.objects.all():
        icon_name = getattr(group, "icon", None)
        icon_name = getattr(icon_name, "name", icon_name) if icon_name else ""
        if icon_name and not group.image:
            group.image = icon_name
            group.save(update_fields=["image"])


def assign_orphan_items(apps, schema_editor):
    SurfaceItem = apps.get_model("cms", "SurfaceItem")
    SurfaceType = apps.get_model("cms", "SurfaceType")
    fallback = SurfaceType.objects.order_by("sort_order", "id").first()
    if not fallback:
        fallback = SurfaceType.objects.create(
            name="Bez grupy",
            slug="bez-grupy",
            sort_order=999,
            is_active=True,
        )
    SurfaceItem.objects.filter(surface_type__isnull=True).update(surface_type=fallback)


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0011_product_packshot_gallery"),
    ]

    operations = [
        migrations.AddField(
            model_name="surfacetype",
            name="image",
            field=models.ImageField(blank=True, upload_to="cms/surfaces/groups/", verbose_name="Zdjęcie"),
        ),
        migrations.RunPython(forwards_migrate_surface_images, migrations.RunPython.noop),
        migrations.RemoveField(model_name="surfacetype", name="description"),
        migrations.RemoveField(model_name="surfacetype", name="icon"),
        migrations.AlterModelOptions(
            name="surfacetype",
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Grupa produktowa (barwy)",
                "verbose_name_plural": "Grupy produktowe (barwy)",
            },
        ),
        migrations.AlterField(
            model_name="surfacetype",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Aktywna"),
        ),
        migrations.RunPython(assign_orphan_items, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="surfaceitem",
            name="surface_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="cms.surfacetype",
                verbose_name="Grupa produktowa",
            ),
        ),
        migrations.RemoveField(model_name="surfaceitem", name="application"),
        migrations.RemoveField(model_name="surfaceitem", name="category"),
        migrations.RemoveField(model_name="surfaceitem", name="color"),
        migrations.RemoveField(model_name="surfaceitem", name="format_size"),
        migrations.RemoveField(model_name="surfaceitem", name="load_capacity"),
        migrations.RemoveField(model_name="surfaceitem", name="product_kind"),
        migrations.RemoveField(model_name="surfaceitem", name="surface"),
        migrations.RemoveField(model_name="surfaceitem", name="thickness"),
        migrations.AlterField(
            model_name="surfaceitem",
            name="image",
            field=models.ImageField(blank=True, upload_to="cms/surfaces/", verbose_name="Zdjęcie"),
        ),
        migrations.AlterField(
            model_name="surfaceitem",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Aktywna"),
        ),
        migrations.AlterModelOptions(
            name="surfacecategory",
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Kategoria barw (archiwum)",
                "verbose_name_plural": "Kategorie barw (archiwum)",
            },
        ),
    ]
