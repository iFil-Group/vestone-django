from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from .models import (
    ContentBlock,
    DownloadCategory,
    DownloadItem,
    HeroSlide,
    JobOpening,
    NewsPost,
    Product,
    ProductGalleryImage,
    ProductGroup,
    ProductPin,
    ProductSpec,
    Review,
    SiteSettings,
    SurfaceItem,
    Tip,
)
from .widgets import CMSClearableFileInput, CMSFileInput


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
                field.widget.attrs.setdefault("class", "cms-textarea")
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
        fields = ("title", "lead", "image", "sort_order", "is_active")


class ReviewForm(StyledModelForm):
    class Meta:
        model = Review
        fields = ("quote", "author", "sort_order", "is_active")


class ProductGroupForm(StyledModelForm):
    class Meta:
        model = ProductGroup
        fields = ("title", "slug", "image", "sort_order", "is_active")


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = (
            "group",
            "title",
            "slug",
            "subtitle",
            "description",
            "description_extra",
            "image",
            "sort_order",
            "is_active",
        )


ProductSpecFormSet = inlineformset_factory(
    Product,
    ProductSpec,
    form=StyledModelForm,
    fields=("label", "value", "sort_order"),
    extra=1,
    can_delete=True,
)

class ProductPinInlineForm(StyledModelForm):
    class Meta:
        model = ProductPin
        fields = ("x", "y", "text", "sort_order")
        widgets = {
            "x": forms.HiddenInput(),
            "y": forms.HiddenInput(),
            "sort_order": forms.HiddenInput(),
        }


ProductPinFormSet = inlineformset_factory(
    Product,
    ProductPin,
    form=ProductPinInlineForm,
    fields=("x", "y", "text", "sort_order"),
    extra=0,
    can_delete=True,
)

ProductGalleryFormSet = inlineformset_factory(
    Product,
    ProductGalleryImage,
    form=StyledModelForm,
    fields=("image", "alt", "sort_order"),
    extra=1,
    can_delete=True,
)


class SurfaceItemForm(StyledModelForm):
    class Meta:
        model = SurfaceItem
        fields = (
            "title",
            "slug",
            "image",
            "color",
            "surface",
            "format_size",
            "thickness",
            "sort_order",
            "is_active",
        )


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


class DownloadCategoryForm(StyledModelForm):
    class Meta:
        model = DownloadCategory
        fields = ("label", "slug", "sort_order")


class DownloadItemForm(StyledModelForm):
    class Meta:
        model = DownloadItem
        fields = ("category", "title", "file", "kind", "sort_order", "is_published")


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
            "is_active",
        )
