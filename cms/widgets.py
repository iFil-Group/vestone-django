from django import forms


class CMSFileInput(forms.FileInput):
    template_name = "cms/widgets/file_input.html"


class CMSClearableFileInput(forms.ClearableFileInput):
    template_name = "cms/widgets/clearable_file_input.html"


class RichTextWidget(forms.Textarea):
    template_name = "cms/widgets/rich_textarea.html"

    def __init__(self, attrs=None):
        attrs = {"class": "cms-textarea cms-richtext-source", **(attrs or {})}
        super().__init__(attrs)
