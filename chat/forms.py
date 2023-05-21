# chat/forms.py
from django import forms
from documents.models import Category


class SearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Posez votre question...",
                "autofocus": "autofocus",
                "class": "flex items-center h-10 w-full rounded-lg px-3 text-sm pr-12",
            }
        ),
        label="",
    )
    engine = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial="gpt-3.5-turbo"
    )  # Set the default value for the "engine" field
    history = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )  # Add a hidden input field for the history


class DebugForm(forms.ModelForm):
    ENGINE_CHOICES = [
        ("paradigm", "LightOn"),
        ("gpt-3.5-turbo", "ChatGPT 3.5"),
        # ...
    ]
    engine = forms.ChoiceField(choices=ENGINE_CHOICES)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"id": "category-select"}),
    )
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={"style": "font-family:monospace;", "cols": "120"})
    )

    query = forms.CharField(
        widget=forms.Textarea(attrs={"style": "font-family:monospace;", "cols": "120", "rows": "4"})
    )

    class Meta:
        model = Category
        fields = ["prompt", "k", "query"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["category"].initial = self.instance.id
            self.fields["prompt"].initial = self.instance.prompt
            self.fields["k"].initial = self.instance.k
        self.order_fields(["category", "prompt", "k", "engine", "query"])
