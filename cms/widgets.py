from django import forms


class CMSFileInput(forms.FileInput):
    template_name = "cms/widgets/file_input.html"


class CMSClearableFileInput(forms.ClearableFileInput):
    template_name = "cms/widgets/clearable_file_input.html"
