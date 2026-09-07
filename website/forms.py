from django import forms

from pathlib import Path

from cms.models import FormSubmission, JobApplication


class WidgetSubmissionForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label="Zgoda",
        error_messages={"required": "Zaznacz zgodę, aby zamówić katalog."},
    )

    class Meta:
        model = FormSubmission
        fields = (
            "first_name", "last_name", "street", "house_number",
            "postal_code", "city", "company", "consent",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "street": forms.TextInput(attrs={"autocomplete": "address-line1"}),
            "house_number": forms.TextInput(attrs={"autocomplete": "address-line2"}),
            "postal_code": forms.TextInput(attrs={"autocomplete": "postal-code"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "company": forms.TextInput(attrs={"autocomplete": "organization"}),
        }
        error_messages = {
            "first_name": {"required": "Podaj imię."},
            "last_name": {"required": "Podaj nazwisko."},
            "street": {"required": "Podaj ulicę."},
            "house_number": {"required": "Podaj numer domu lub mieszkania."},
            "postal_code": {"required": "Podaj kod pocztowy."},
            "city": {"required": "Podaj miejscowość."},
        }

    def __init__(self, *args, widget, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.widget = widget
        for name, field in self.fields.items():
            if name != "consent":
                field.widget.attrs["class"] = "widget-form__input"
            if field.required:
                field.widget.attrs["aria-required"] = "true"


class JobApplicationForm(forms.ModelForm):
    consent = forms.BooleanField(required=True)

    class Meta:
        model = JobApplication
        fields = ("job", "name", "email", "phone", "cv", "consent")
        widgets = {"job": forms.HiddenInput()}

    def clean_cv(self):
        file = self.cleaned_data["cv"]
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Plik CV może mieć maksymalnie 10 MB.")
        if Path(file.name).suffix.lower() not in {".pdf", ".doc", ".docx"}:
            raise forms.ValidationError("Dozwolone formaty CV: PDF, DOC, DOCX.")
        return file
