from django.db import migrations


def create_documents(apps, schema_editor):
    LegalDocument = apps.get_model("cms", "LegalDocument")
    for slug, title in [
        ("polityka-prywatnosci", "Polityka prywatności"),
        ("regulamin-serwisu", "Regulamin serwisu"),
        ("obowiazek-informacyjny", "Obowiązek informacyjny"),
    ]:
        LegalDocument.objects.get_or_create(
            slug=slug,
            defaults={"title": title, "is_active": True},
        )


class Migration(migrations.Migration):
    dependencies = [("cms", "0008_legaldocument_downloaditem_file_number_and_more")]
    operations = [migrations.RunPython(create_documents, migrations.RunPython.noop)]
