from django.db import models
from django.utils.text import slugify


class SiteSettings(models.Model):
    phone = models.CharField("Telefon", max_length=64, blank=True)
    email = models.EmailField("E-mail", blank=True)
    infoline = models.CharField("Infolinia", max_length=64, blank=True)
    address = models.TextField("Adres", blank=True)
    footer_tagline = models.CharField("Tagline stopki", max_length=255, blank=True)

    class Meta:
        verbose_name = "Ustawienia strony"
        verbose_name_plural = "Ustawienia strony"

    def __str__(self):
        return "Ustawienia strony"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContentBlock(models.Model):
    GROUP_HOME = "home"
    GROUP_ABOUT = "about"
    GROUP_GLOBAL = "global"
    GROUP_CHOICES = [
        (GROUP_HOME, "Strona główna"),
        (GROUP_ABOUT, "O nas"),
        (GROUP_GLOBAL, "Globalne"),
    ]

    key = models.SlugField("Klucz", max_length=80, unique=True)
    group = models.CharField("Grupa", max_length=20, choices=GROUP_CHOICES)
    label = models.CharField("Etykieta w CMS", max_length=200)
    title = models.CharField("Tytuł", max_length=255, blank=True)
    subtitle = models.CharField("Podtytuł", max_length=255, blank=True)
    body = models.TextField("Treść", blank=True)
    body_extra = models.TextField("Treść dodatkowa", blank=True)
    image = models.ImageField("Obraz", upload_to="cms/pages/", blank=True)
    button_label = models.CharField("Etykieta przycisku", max_length=120, blank=True)
    button_url = models.CharField("URL przycisku", max_length=255, blank=True)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["group", "label"]
        verbose_name = "Blok treści"
        verbose_name_plural = "Bloki treści"

    def __str__(self):
        return self.label


class HeroSlide(models.Model):
    MEDIA_IMAGE = "image"
    MEDIA_VIDEO = "video"
    MEDIA_CHOICES = [(MEDIA_IMAGE, "Zdjęcie"), (MEDIA_VIDEO, "Film")]

    title = models.CharField("Tytuł", max_length=255)
    lead = models.TextField("Lead", blank=True)
    media_type = models.CharField("Typ medium", max_length=10, choices=MEDIA_CHOICES, default=MEDIA_IMAGE)
    image = models.ImageField("Obraz desktop", upload_to="cms/hero/", blank=True)
    mobile_image = models.ImageField("Obraz mobile", upload_to="cms/hero/mobile/", blank=True)
    video = models.FileField("Film", upload_to="cms/hero/video/", blank=True)
    video_url = models.URLField("Link do filmu", blank=True)
    button_label = models.CharField("Etykieta przycisku", max_length=120, blank=True)
    button_url = models.CharField("Link przycisku", max_length=500, blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"

    def __str__(self):
        return self.title


class PromotionSlide(models.Model):
    text = models.TextField("Treść")
    link_label = models.CharField("Etykieta linku", max_length=120, blank=True)
    link_url = models.CharField("Link", max_length=500, blank=True)
    active_from = models.DateTimeField("Aktywny od", blank=True, null=True)
    active_until = models.DateTimeField("Aktywny do", blank=True, null=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Slajd paska promocyjnego"
        verbose_name_plural = "Slajdy paska promocyjnego"

    def __str__(self):
        return self.link_label or f"Komunikat #{self.pk}"


class FormWidget(models.Model):
    slug = models.SlugField("Nazwa widgetu", max_length=120, unique=True)
    title = models.CharField("Tytuł", max_length=255)
    description = models.TextField("Opis", blank=True)
    image = models.ImageField("Zdjęcie", upload_to="cms/forms/", blank=True)
    recipient_email = models.EmailField("Adres e-mail odbiorcy")
    required_fields_text = models.TextField("Opis pól obowiązkowych", blank=True)
    consent_text = models.TextField("Zgoda na przetwarzanie danych")
    thanks_image = models.ImageField("Grafika podziękowania", upload_to="cms/forms/thanks/", blank=True)
    thanks_text = models.TextField("Tekst podziękowania", blank=True)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Widget formularza"
        verbose_name_plural = "Widgety formularzy"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class FormSubmission(models.Model):
    widget = models.ForeignKey(FormWidget, on_delete=models.CASCADE, related_name="submissions")
    first_name = models.CharField("Imię", max_length=120)
    last_name = models.CharField("Nazwisko", max_length=120)
    street = models.CharField("Ulica", max_length=200)
    house_number = models.CharField("Nr domu/mieszkania", max_length=40)
    postal_code = models.CharField("Kod pocztowy", max_length=20)
    city = models.CharField("Miejscowość", max_length=150)
    company = models.CharField("Firma", max_length=200, blank=True)
    consent = models.BooleanField("Zgoda", default=False)
    created_at = models.DateTimeField("Data zgłoszenia", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Zgłoszenie formularza"
        verbose_name_plural = "Zgłoszenia formularzy"

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.widget}"


class SalesPoint(models.Model):
    OFFER_FULL = "full"
    OFFER_MUSSO = "musso"
    OFFER_CHOICES = [
        (OFFER_FULL, "Pełna oferta"),
        (OFFER_MUSSO, "Płyty dekoracyjne MUSSO"),
    ]

    name = models.CharField("Nazwa", max_length=200)
    address = models.CharField("Adres", max_length=300)
    phone = models.CharField("Telefon", max_length=80, blank=True)
    email = models.EmailField("E-mail", blank=True)
    website_url = models.URLField("Link do strony", blank=True)
    offer_type = models.CharField("Oferta", max_length=10, choices=OFFER_CHOICES, default=OFFER_FULL)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Punkt sprzedaży"
        verbose_name_plural = "Punkty sprzedaży"

    def __str__(self):
        return self.name


class FloatingPromotion(models.Model):
    PLACEMENT_MODAL = "modal"
    PLACEMENT_SIDE = "side"
    PLACEMENT_CHOICES = [
        (PLACEMENT_MODAL, "Okno dialogowe"),
        (PLACEMENT_SIDE, "Widget boczny"),
    ]

    placement = models.CharField("Położenie", max_length=10, choices=PLACEMENT_CHOICES)
    image = models.ImageField("Zdjęcie", upload_to="cms/promotions/")
    link_url = models.CharField("Link", max_length=500)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["placement", "id"]
        verbose_name = "Widget promocyjny"
        verbose_name_plural = "Widgety promocyjne"

    def __str__(self):
        return self.get_placement_display()


class Review(models.Model):
    quote = models.TextField("Cytat")
    author = models.CharField("Autor", max_length=200)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Opinia"
        verbose_name_plural = "Opinie"

    def __str__(self):
        return self.author


class ProductGroup(models.Model):
    slug = models.SlugField("Slug", max_length=80, unique=True)
    title = models.CharField("Nazwa", max_length=200)
    image = models.ImageField("Obraz", upload_to="cms/products/groups/", blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Grupa produktów"
        verbose_name_plural = "Grupy produktów"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Product(models.Model):
    CARD_STANDARD = "standard"
    CARD_DESCRIPTIVE = "descriptive"
    CARD_TYPE_CHOICES = [
        (CARD_STANDARD, "Standardowa karta"),
        (CARD_DESCRIPTIVE, "Karta opisowa"),
    ]

    group = models.ForeignKey(
        ProductGroup,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Grupa",
    )
    slug = models.SlugField("Slug", max_length=120)
    title = models.CharField("Nazwa", max_length=200)
    subtitle = models.CharField("Podtytuł", max_length=255, blank=True)
    card_type = models.CharField(
        "Typ karty",
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        default=CARD_STANDARD,
    )
    description = models.TextField("Opis", blank=True)
    description_extra = models.TextField("Opis dodatkowy", blank=True)
    image = models.ImageField("Obraz główny", upload_to="cms/products/", blank=True)
    show_main_image = models.BooleanField("Pokaż zdjęcie główne z pinami", default=True)
    show_packshot = models.BooleanField("Pokaż sekcję Packshot", default=False)
    PACKSHOT_COLUMNS_CHOICES = [
        (1, "1 kolumna"),
        (2, "2 kolumny"),
        (3, "3 kolumny"),
        (4, "4 kolumny"),
    ]
    packshot_columns = models.PositiveSmallIntegerField(
        "Liczba kolumn packshotów",
        choices=PACKSHOT_COLUMNS_CHOICES,
        default=2,
    )
    related_products = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="related_to_products",
        verbose_name="Polecane produkty",
    )
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "title"]
        unique_together = [("group", "slug")]
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductSpec(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specs",
        verbose_name="Produkt",
    )
    label = models.CharField("Etykieta", max_length=120)
    value = models.CharField("Wartość", max_length=200)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Parametr produktu"
        verbose_name_plural = "Parametry produktu"

    def __str__(self):
        return f"{self.label}: {self.value}"


class ProductAttribute(models.Model):
    name = models.CharField("Nazwa", max_length=120)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    show_in_filters = models.BooleanField("W filtrach na stronie", default=False)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Atrybut produktu"
        verbose_name_plural = "Atrybuty produktów"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttributeOption(models.Model):
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="Atrybut",
    )
    value = models.CharField("Wartość", max_length=200)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "value"]
        unique_together = [("attribute", "value")]
        verbose_name = "Wartość atrybutu"
        verbose_name_plural = "Wartości atrybutów"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttributeAssignment(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attribute_assignments",
        verbose_name="Produkt",
    )
    option = models.ForeignKey(
        ProductAttributeOption,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Wartość",
    )
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Atrybut produktu"
        verbose_name_plural = "Atrybuty produktu"

    def __str__(self):
        return str(self.option)

class ProductPin(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="pins",
        verbose_name="Produkt",
    )
    gallery_image = models.ForeignKey(
        "ProductGalleryImage",
        on_delete=models.CASCADE,
        related_name="pins",
        verbose_name="Zdjęcie galerii",
        blank=True,
        null=True,
    )
    x = models.DecimalField("Pozycja X (%)", max_digits=5, decimal_places=2, default=50)
    y = models.DecimalField("Pozycja Y (%)", max_digits=5, decimal_places=2, default=50)
    text = models.TextField("Treść tooltipa")
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Pin na zdjęciu"
        verbose_name_plural = "Piny na zdjęciu"

    def __str__(self):
        return f"Pin {self.x}/{self.y}"


class ProductGalleryImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Produkt",
    )
    image = models.ImageField("Obraz", upload_to="cms/products/gallery/", blank=True)
    alt = models.CharField("Alt", max_length=255, blank=True)
    pins_enabled = models.BooleanField("Aktywuj piny", default=False)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Zdjęcie galerii"
        verbose_name_plural = "Zdjęcia galerii"

    def __str__(self):
        return self.alt or f"Galeria #{self.pk}"


class ProductPackshotImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="packshots",
        verbose_name="Produkt",
    )
    image = models.ImageField("Zdjęcie", upload_to="cms/products/packshots/", blank=True)
    caption = models.CharField("Podpis", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Zdjęcie packshot"
        verbose_name_plural = "Zdjęcia packshot"

    def __str__(self):
        return self.caption or f"Packshot #{self.pk}"


class SurfaceItem(models.Model):
    KIND_PAVING = "paving"
    KIND_SLAB = "slab"
    KIND_SMALL_ARCH = "small_arch"
    KIND_SAND = "sand"
    KIND_CHOICES = [
        (KIND_PAVING, "Kostka brukowa"),
        (KIND_SLAB, "Płyta dekoracyjna"),
        (KIND_SMALL_ARCH, "Mała architektura"),
        (KIND_SAND, "Piasek fugowy"),
    ]

    title = models.CharField("Nazwa", max_length=200)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    category = models.ForeignKey(
        "SurfaceCategory",
        on_delete=models.SET_NULL,
        related_name="items",
        verbose_name="Kategoria",
        blank=True,
        null=True,
    )
    surface_type = models.ForeignKey(
        "SurfaceType",
        on_delete=models.SET_NULL,
        related_name="items",
        verbose_name="Rodzaj powierzchni",
        blank=True,
        null=True,
    )
    image = models.ImageField("Obraz", upload_to="cms/surfaces/", blank=True)
    color = models.CharField("Kolor", max_length=120, blank=True)
    surface = models.CharField("Powierzchnia", max_length=120, blank=True)
    product_kind = models.CharField("Rodzaj produktu", max_length=20, choices=KIND_CHOICES, blank=True)
    format_size = models.CharField("Format", max_length=120, blank=True)
    thickness = models.CharField("Grubość", max_length=120, blank=True)
    application = models.CharField("Zastosowanie", max_length=200, blank=True)
    load_capacity = models.CharField("Nośność", max_length=120, blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Barwa / powierzchnia"
        verbose_name_plural = "Barwy i powierzchnie"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class SurfaceCategory(models.Model):
    name = models.CharField("Nazwa", max_length=160)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Sekcja nadrzędna",
        blank=True,
        null=True,
    )
    description = models.TextField("Opis", blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywna", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Kategoria barw i powierzchni"
        verbose_name_plural = "Kategorie barw i powierzchni"

    def __str__(self):
        return f"{self.parent.name} — {self.name}" if self.parent else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SurfaceType(models.Model):
    name = models.CharField("Nazwa", max_length=160)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    icon = models.ImageField("Ikona", upload_to="cms/surfaces/icons/", blank=True)
    description = models.TextField("Opis powierzchni", blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Rodzaj powierzchni"
        verbose_name_plural = "Rodzaje powierzchni"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    slug = models.SlugField("Slug", max_length=120, unique=True)
    title = models.CharField("Tytuł", max_length=255)
    excerpt = models.TextField("Zajawka", blank=True)
    body = models.TextField("Treść", blank=True)
    image = models.ImageField("Obraz", upload_to="cms/articles/", blank=True)
    published_at = models.DateField("Data publikacji")
    is_published = models.BooleanField("Opublikowany", default=True)

    class Meta:
        abstract = True
        ordering = ["-published_at", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Tip(Article):
    class Meta(Article.Meta):
        verbose_name = "Porada"
        verbose_name_plural = "Porady"


class ArticleGalleryImage(models.Model):
    LAYOUT_FULL = "full"
    LAYOUT_HALF = "half"
    LAYOUT_THIRD = "third"
    LAYOUT_CHOICES = [
        (LAYOUT_FULL, "Pełna szerokość"),
        (LAYOUT_HALF, "1/2 szerokości"),
        (LAYOUT_THIRD, "1/3 szerokości"),
    ]

    image = models.ImageField("Zdjęcie", upload_to="cms/articles/gallery/")
    alt = models.CharField("Opis zdjęcia", max_length=255, blank=True)
    layout = models.CharField("Układ", max_length=10, choices=LAYOUT_CHOICES, default=LAYOUT_FULL)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]


class TipGalleryImage(ArticleGalleryImage):
    article = models.ForeignKey(Tip, on_delete=models.CASCADE, related_name="gallery")


class NewsPost(Article):
    class Meta(Article.Meta):
        verbose_name = "Aktualność"
        verbose_name_plural = "Aktualności"


class NewsGalleryImage(ArticleGalleryImage):
    article = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name="gallery")


class DownloadCategory(models.Model):
    slug = models.SlugField("Slug", max_length=80, unique=True)
    label = models.CharField("Nazwa", max_length=200)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "label"]
        verbose_name = "Kategoria plików"
        verbose_name_plural = "Kategorie plików"

    def __str__(self):
        return self.label


class DownloadItem(models.Model):
    KIND_PDF = "pdf"
    KIND_ZIP = "zip"
    KIND_CHOICES = [
        (KIND_PDF, "PDF"),
        (KIND_ZIP, "ZIP"),
    ]

    category = models.ForeignKey(
        DownloadCategory,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Kategoria",
    )
    title = models.CharField("Tytuł", max_length=255)
    file_number = models.CharField("Numer pliku", max_length=100, blank=True)
    file = models.FileField("Plik", upload_to="cms/downloads/")
    kind = models.CharField("Typ", max_length=8, choices=KIND_CHOICES, default=KIND_PDF)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_published = models.BooleanField("Opublikowany", default=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Plik do pobrania"
        verbose_name_plural = "Pliki do pobrania"

    def __str__(self):
        return self.title


class JobOpening(models.Model):
    slug = models.SlugField("Slug", max_length=120, unique=True)
    title = models.CharField("Stanowisko", max_length=200)
    location = models.CharField("Lokalizacja", max_length=200, blank=True)
    employment_type = models.CharField("Typ zatrudnienia", max_length=120, blank=True)
    excerpt = models.TextField("Zajawka", blank=True)
    body = models.TextField("Opis", blank=True)
    image = models.ImageField("Zdjęcie", upload_to="cms/jobs/", blank=True)
    is_active = models.BooleanField("Aktywna", default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Oferta pracy"
        verbose_name_plural = "Oferty pracy"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class JobApplication(models.Model):
    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="applications")
    name = models.CharField("Imię i nazwisko", max_length=200)
    email = models.EmailField("E-mail")
    phone = models.CharField("Telefon", max_length=80)
    cv = models.FileField("CV", upload_to="cms/jobs/applications/")
    consent = models.BooleanField("Zgoda", default=False)
    created_at = models.DateTimeField("Data zgłoszenia", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Aplikacja"
        verbose_name_plural = "Aplikacje"


class LegalDocument(models.Model):
    slug = models.SlugField("Slug", max_length=120, unique=True)
    title = models.CharField("Tytuł", max_length=255)
    body = models.TextField("Treść", blank=True)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"

    def __str__(self):
        return self.title
