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
    title = models.CharField("Tytuł", max_length=255)
    lead = models.TextField("Lead", blank=True)
    image = models.ImageField("Obraz", upload_to="cms/hero/", blank=True)
    sort_order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Slajd hero"
        verbose_name_plural = "Slajdy hero"

    def __str__(self):
        return self.title


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
    group = models.ForeignKey(
        ProductGroup,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Grupa",
    )
    slug = models.SlugField("Slug", max_length=120)
    title = models.CharField("Nazwa", max_length=200)
    subtitle = models.CharField("Podtytuł", max_length=255, blank=True)
    description = models.TextField("Opis", blank=True)
    description_extra = models.TextField("Opis dodatkowy", blank=True)
    image = models.ImageField("Obraz główny", upload_to="cms/products/", blank=True)
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


class ProductPin(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="pins",
        verbose_name="Produkt",
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
    sort_order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Zdjęcie galerii"
        verbose_name_plural = "Zdjęcia galerii"

    def __str__(self):
        return self.alt or f"Galeria #{self.pk}"


class SurfaceItem(models.Model):
    title = models.CharField("Nazwa", max_length=200)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    image = models.ImageField("Obraz", upload_to="cms/surfaces/", blank=True)
    color = models.CharField("Kolor", max_length=120, blank=True)
    surface = models.CharField("Powierzchnia", max_length=120, blank=True)
    format_size = models.CharField("Format", max_length=120, blank=True)
    thickness = models.CharField("Grubość", max_length=120, blank=True)
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


class NewsPost(Article):
    class Meta(Article.Meta):
        verbose_name = "Aktualność"
        verbose_name_plural = "Aktualności"


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
