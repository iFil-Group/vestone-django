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
    ProductAttribute,
    ProductAttributeAssignment,
    ProductAttributeOption,
    ProductGalleryImage,
    ProductGroup,
    ProductPin,
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
            if not form.has_changed() and form.instance.pk:
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
