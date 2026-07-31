from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    FloatingPromotion,
    FormWidget,
    HeroSlide,
    JobOpening,
    LegalDocument,
    NewsPost,
    NewsGalleryImage,
    Product,
    ProductAttribute,
    ProductAttributeAssignment,
    ProductAttributeOption,
    ProductGalleryImage,
    ProductGroup,
    ProductPackshotImage,
    ProductPin,
    PromotionSlide,
    Review,
    SalesPoint,
    SiteSettings,
    SurfaceCategory,
    SurfaceItem,
    SurfaceType,
    Tip,
    TipGalleryImage,
)
from .widgets import CMSClearableFileInput, CMSFileInput, RichTextWidget


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Nieprawidłowy e-mail lub hasło. Spróbuj ponownie.",
    }

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            user_model = get_user_model()
            user = user_model.objects.filter(email__iexact=email).first()
            if user is None:
                raise self.get_invalid_login_error()

            self.user_cache = authenticate(
                self.request,
                username=user.get_username(),
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.HiddenInput):
                continue
            if isinstance(widget, forms.ClearableFileInput):
                field.widget = CMSClearableFileInput(attrs=widget.attrs)
            elif isinstance(widget, forms.FileInput):
                field.widget = CMSFileInput(attrs=widget.attrs)
            elif isinstance(widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "cms-checkbox")
            elif isinstance(widget, forms.Textarea):
                field.widget = RichTextWidget(attrs=widget.attrs)
            elif isinstance(widget, forms.RadioSelect):
                continue
            elif isinstance(widget, forms.Select):
                field.widget.attrs.setdefault("class", "cms-select")
            else:
                field.widget.attrs.setdefault("class", "cms-input")


class SiteSettingsForm(StyledModelForm):
    class Meta:
        model = SiteSettings
        fields = ("phone", "email", "infoline", "address", "footer_tagline")


class ContentBlockForm(StyledModelForm):
    class Meta:
        model = ContentBlock
        fields = (
            "key",
            "group",
            "label",
            "title",
            "subtitle",
            "body",
            "body_extra",
            "image",
            "button_label",
            "button_url",
            "is_active",
        )


class HeroSlideForm(StyledModelForm):
    class Meta:
        model = HeroSlide
        fields = (
            "title", "lead", "media_type", "image", "mobile_image", "video",
            "video_url", "button_label", "button_url", "sort_order", "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["mobile_image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["video"].widget.attrs.setdefault("accept", "video/*")

    def clean(self):
        cleaned = super().clean()
        media_type = cleaned.get("media_type")
        if media_type == HeroSlide.MEDIA_IMAGE and not (cleaned.get("image") or self.instance.image):
            self.add_error("image", "Dodaj zdjęcie desktop.")
        if media_type == HeroSlide.MEDIA_VIDEO and not (
            cleaned.get("video") or cleaned.get("video_url") or self.instance.video
        ):
            self.add_error("video", "Dodaj plik filmu lub link do filmu.")
        return cleaned


class PromotionSlideForm(StyledModelForm):
    class Meta:
        model = PromotionSlide
        fields = (
            "text", "link_label", "link_url", "active_from", "active_until",
            "sort_order", "is_active",
        )
        widgets = {
            "active_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "active_until": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("active_from") and cleaned.get("active_until"):
            if cleaned["active_from"] >= cleaned["active_until"]:
                self.add_error("active_until", "Data końcowa musi być późniejsza od początkowej.")
        return cleaned


class FormWidgetForm(StyledModelForm):
    class Meta:
        model = FormWidget
        fields = (
            "title", "slug", "description", "image", "recipient_email",
            "required_fields_text", "consent_text", "thanks_image", "thanks_text",
            "is_active",
        )


class SalesPointForm(StyledModelForm):
    class Meta:
        model = SalesPoint
        fields = (
            "name", "address", "phone", "email", "website_url", "offer_type",
            "sort_order", "is_active",
        )


class FloatingPromotionForm(StyledModelForm):
    class Meta:
        model = FloatingPromotion
        fields = ("placement", "image", "link_url", "is_active")


class ReviewForm(StyledModelForm):
    class Meta:
        model = Review
        fields = ("quote", "author", "sort_order", "is_active")


class ProductGroupForm(StyledModelForm):
    class Meta:
        model = ProductGroup
        fields = ("title", "slug", "image", "sort_order", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].label = "Zdjęcie kategorii"
        self.fields["image"].help_text = "Kafelek na stronie /produkty/ oraz w sekcji produktów na stronie głównej."
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")


class ProductsCtaForm(StyledModelForm):
    class Meta:
        model = ContentBlock
        fields = ("title", "body", "button_label", "button_url")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Nagłówek"
        self.fields["body"].label = "Treść"
        self.fields["button_label"].label = "Tekst przycisku / linku"
        self.fields["button_url"].label = "Adres linku"
        self.fields["button_url"].help_text = "Np. /#kontakt albo /gdzie-kupic/"
        self.fields["button_url"].widget.attrs.setdefault("placeholder", "/#kontakt")


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = (
            "card_type",
            "group",
            "title",
            "slug",
            "subtitle",
            "description",
            "description_extra",
            "image",
            "show_main_image",
            "show_packshot",
            "packshot_columns",
            "related_products",
            "sort_order",
            "is_active",
        )
        widgets = {
            "card_type": forms.RadioSelect,
            "packshot_columns": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = ProductGroup.objects.all().order_by("sort_order", "title")
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["related_products"].queryset = Product.objects.exclude(
            pk=self.instance.pk
        ).select_related("group").order_by("title")
        self.fields["related_products"].widget = forms.MultipleHiddenInput()
        self.fields["card_type"].widget.attrs["class"] = "cms-card-type"
        self.fields["packshot_columns"].widget.attrs["class"] = "cms-card-type"



class ProductAttributeAssignmentForm(StyledModelForm):
    attribute = forms.ModelChoiceField(
        queryset=ProductAttribute.objects.order_by("sort_order", "name"),
        required=False,
        label="Atrybut",
        empty_label="— wybierz atrybut —",
    )
    new_attribute_name = forms.CharField(
        required=False,
        label="Nowy atrybut",
        widget=forms.TextInput(attrs={"placeholder": "np. Format"}),
    )
    show_in_filters = forms.BooleanField(
        required=False,
        label="W filtrach na stronie",
    )
    new_option_value = forms.CharField(
        required=False,
        label="Nowa wartość",
        widget=forms.TextInput(attrs={"placeholder": "np. 60 × 60 cm"}),
    )

    class Meta:
        model = ProductAttributeAssignment
        fields = ("option", "sort_order")
        labels = {"option": "Wartość"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["option"].required = False
        self.fields["option"].queryset = ProductAttributeOption.objects.select_related(
            "attribute"
        ).order_by("attribute__sort_order", "attribute__name", "sort_order", "value")
        self.fields["option"].empty_label = "— wybierz wartość —"

        if self.instance.pk and self.instance.option_id:
            attribute = self.instance.option.attribute
            self.fields["attribute"].initial = attribute.pk
            self.fields["show_in_filters"].initial = attribute.show_in_filters
            self.fields["option"].queryset = ProductAttributeOption.objects.filter(
                attribute=attribute
            ).order_by("sort_order", "value")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned

        attribute = cleaned.get("attribute")
        new_attribute_name = (cleaned.get("new_attribute_name") or "").strip()
        option = cleaned.get("option")
        new_option_value = (cleaned.get("new_option_value") or "").strip()

        if (
            not self.instance.pk
            and not attribute
            and not new_attribute_name
            and not option
            and not new_option_value
        ):
            return cleaned

        if not attribute and not new_attribute_name:
            raise forms.ValidationError("Wybierz atrybut lub podaj nazwę nowego atrybutu.")
        if attribute and new_attribute_name:
            raise forms.ValidationError("Wybierz istniejący atrybut albo podaj nazwę nowego — nie oba naraz.")
        if not option and not new_option_value:
            raise forms.ValidationError("Wybierz wartość lub podaj nową wartość atrybutu.")
        if option and new_option_value:
            raise forms.ValidationError("Wybierz istniejącą wartość albo podaj nową — nie oba naraz.")

        if option and attribute and option.attribute_id != attribute.pk:
            raise forms.ValidationError("Wybrana wartość nie należy do wskazanego atrybutu.")

        if new_option_value:
            cleaned["option"] = None

        if new_attribute_name:
            cleaned["attribute"] = None

        return cleaned

    def save(self, commit=True):
        if self.cleaned_data.get("DELETE"):
            if self.instance.pk:
                self.instance.delete()
            return self.instance

        attribute = self.cleaned_data.get("attribute")
        new_attribute_name = (self.cleaned_data.get("new_attribute_name") or "").strip()
        show_in_filters = self.cleaned_data.get("show_in_filters") or False
        option = self.cleaned_data.get("option")
        new_option_value = (self.cleaned_data.get("new_option_value") or "").strip()

        if new_attribute_name:
            from django.utils.text import slugify

            slug = slugify(new_attribute_name)
            attribute, _ = ProductAttribute.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": new_attribute_name,
                    "show_in_filters": show_in_filters,
                },
            )
            if attribute.name != new_attribute_name:
                attribute.name = new_attribute_name
            attribute.show_in_filters = show_in_filters
            attribute.save()
        elif attribute:
            attribute.show_in_filters = show_in_filters
            attribute.save(update_fields=["show_in_filters"])

        if new_option_value:
            option, _ = ProductAttributeOption.objects.get_or_create(
                attribute=attribute,
                value=new_option_value,
                defaults={"sort_order": 0},
            )
        elif option and option.attribute_id != attribute.pk:
            option = ProductAttributeOption.objects.get(pk=option.pk)

        assignment = super().save(commit=False)
        assignment.option = option
        if commit:
            assignment.save()
        return assignment


class BaseProductAttributeAssignmentFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        has_assignment = False
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            attribute = form.cleaned_data.get("attribute")
            new_attribute_name = (form.cleaned_data.get("new_attribute_name") or "").strip()
            option = form.cleaned_data.get("option")
            new_option_value = (form.cleaned_data.get("new_option_value") or "").strip()
            if attribute or new_attribute_name or option or new_option_value or form.instance.pk:
                has_assignment = True
        if not has_assignment and not self.instance:
            return

    def save(self, commit=True):
        assignments = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                if form.instance.pk:
                    form.instance.delete()
                continue
            attribute = form.cleaned_data.get("attribute")
            new_attribute_name = (form.cleaned_data.get("new_attribute_name") or "").strip()
            option = form.cleaned_data.get("option")
            new_option_value = (form.cleaned_data.get("new_option_value") or "").strip()
            if (
                not form.instance.pk
                and not attribute
                and not new_attribute_name
                and not option
                and not new_option_value
            ):
                continue
            if (
                form.instance.pk
                and not form.has_changed()
                and not new_option_value
                and not new_attribute_name
            ):
                assignments.append(form.instance)
                continue
            assignments.append(form.save(commit=commit))
        return assignments


ProductAttributeAssignmentFormSet = inlineformset_factory(
    Product,
    ProductAttributeAssignment,
    form=ProductAttributeAssignmentForm,
    formset=BaseProductAttributeAssignmentFormSet,
    fields=("option", "sort_order"),
    extra=0,
    can_delete=True,
)

class ProductPinInlineForm(StyledModelForm):
    class Meta:
        model = ProductPin
        fields = ("gallery_image", "x", "y", "text", "sort_order")
        widgets = {
            "gallery_image": forms.HiddenInput(),
            "x": forms.HiddenInput(),
            "y": forms.HiddenInput(),
            "sort_order": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget = forms.Textarea(attrs={"class": "cms-textarea", "rows": 3})
        product_id = getattr(self.instance, "product_id", None)
        self.fields["gallery_image"].queryset = ProductGalleryImage.objects.filter(
            product_id=product_id
        )

    def clean(self):
        cleaned = super().clean()
        gallery_image = cleaned.get("gallery_image")
        product_id = getattr(self.instance, "product_id", None)
        if gallery_image and gallery_image.product_id != product_id:
            self.add_error("gallery_image", "Wybrane zdjęcie nie należy do tego produktu.")
        return cleaned


class BaseProductPinFormSet(forms.BaseInlineFormSet):
    def save(self, commit=True):
        saved = []
        for form in self.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                if form.instance.pk:
                    form.instance.delete()
                continue
            text = (form.cleaned_data.get("text") or "").strip()
            if not text:
                continue
            gallery_image = form.cleaned_data.get("gallery_image")
            if gallery_image and not ProductGalleryImage.objects.filter(pk=gallery_image.pk).exists():
                continue
            saved.append(form.save(commit=commit))
        return saved


ProductPinFormSet = inlineformset_factory(
    Product,
    ProductPin,
    form=ProductPinInlineForm,
    formset=BaseProductPinFormSet,
    fields=("gallery_image", "x", "y", "text", "sort_order"),
    extra=0,
    can_delete=True,
)


class ProductGalleryInlineForm(StyledModelForm):
    class Meta:
        model = ProductGalleryImage
        fields = ("image", "alt", "pins_enabled", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["sort_order"].widget = forms.HiddenInput()
        self.fields["alt"].widget.attrs.setdefault("placeholder", "Tekst alternatywny (opcjonalnie)")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        image = cleaned.get("image")
        clearing = image is False
        has_existing = bool(self.instance.pk and self.instance.image)
        if clearing or (not image and not has_existing):
            cleaned["DELETE"] = True
            return cleaned
        # If this gallery image has pins in POST/DB, keep storefront pins active.
        if self.instance.pk and self.instance.pins.exists():
            cleaned["pins_enabled"] = True
        return cleaned


ProductGalleryFormSet = inlineformset_factory(
    Product,
    ProductGalleryImage,
    form=ProductGalleryInlineForm,
    fields=("image", "alt", "pins_enabled", "sort_order"),
    extra=0,
    can_delete=True,
)


class ProductPackshotInlineForm(StyledModelForm):
    class Meta:
        model = ProductPackshotImage
        fields = ("image", "caption", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["sort_order"].widget = forms.HiddenInput()
        self.fields["caption"].widget.attrs.setdefault(
            "placeholder", "Opcjonalny podpis pod zdjęciem"
        )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        image = cleaned.get("image")
        clearing = image is False
        has_existing = bool(self.instance.pk and self.instance.image)
        if clearing or (not image and not has_existing):
            # Drop blank rows — empty formset slots must never become ghost images.
            cleaned["DELETE"] = True
        return cleaned


ProductPackshotFormSet = inlineformset_factory(
    Product,
    ProductPackshotImage,
    form=ProductPackshotInlineForm,
    fields=("image", "caption", "sort_order"),
    extra=0,
    can_delete=True,
)


class SurfaceItemForm(StyledModelForm):
    class Meta:
        model = SurfaceItem
        fields = (
            "title",
            "slug",
            "surface_type",
            "image",
            "sort_order",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["surface_type"].label = "Grupa produktowa"
        self.fields["surface_type"].queryset = SurfaceType.objects.order_by("sort_order", "name")
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")


class SurfaceCategoryForm(StyledModelForm):
    class Meta:
        model = SurfaceCategory
        fields = ("name", "slug", "parent", "description", "sort_order", "is_active")


class SurfaceTypeForm(StyledModelForm):
    class Meta:
        model = SurfaceType
        fields = ("name", "slug", "image", "sort_order", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].label = "Zdjęcie grupy"
        self.fields["image"].help_text = "Wyświetlane wyśrodkowane nad siatką barw na stronie barw i powierzchni."
        self.fields["image"].widget.attrs.setdefault("accept", "image/*")


class TipForm(StyledModelForm):
    class Meta:
        model = Tip
        fields = (
            "title",
            "slug",
            "excerpt",
            "body",
            "image",
            "published_at",
            "is_published",
        )
        widgets = {"published_at": forms.DateInput(attrs={"type": "date", "class": "cms-input"})}


class TipGalleryImageForm(StyledModelForm):
    class Meta:
        model = TipGalleryImage
        fields = ("image", "alt", "layout", "sort_order")


TipGalleryFormSet = inlineformset_factory(
    Tip, TipGalleryImage, form=TipGalleryImageForm,
    fields=("image", "alt", "layout", "sort_order"), extra=1, can_delete=True,
)


class NewsPostForm(StyledModelForm):
    class Meta:
        model = NewsPost
        fields = (
            "title",
            "slug",
            "excerpt",
            "body",
            "image",
            "published_at",
            "is_published",
        )
        widgets = {"published_at": forms.DateInput(attrs={"type": "date", "class": "cms-input"})}


class NewsGalleryImageForm(StyledModelForm):
    class Meta:
        model = NewsGalleryImage
        fields = ("image", "alt", "layout", "sort_order")


NewsGalleryFormSet = inlineformset_factory(
    NewsPost, NewsGalleryImage, form=NewsGalleryImageForm,
    fields=("image", "alt", "layout", "sort_order"), extra=1, can_delete=True,
)


class DownloadCategoryForm(StyledModelForm):
    class Meta:
        model = DownloadCategory
        fields = ("label", "slug", "sort_order")


class DownloadItemForm(StyledModelForm):
    class Meta:
        model = DownloadItem
        fields = ("category", "title", "file_number", "file", "kind", "sort_order", "is_published")


class JobOpeningForm(StyledModelForm):
    class Meta:
        model = JobOpening
        fields = (
            "title",
            "slug",
            "location",
            "employment_type",
            "excerpt",
            "body",
            "image",
            "is_active",
        )


class LegalDocumentForm(StyledModelForm):
    class Meta:
        model = LegalDocument
        fields = ("title", "slug", "body", "is_active")
