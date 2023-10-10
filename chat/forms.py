# chat/forms.py
from django import forms

from documents.models import Category


class SearchForm(forms.Form):
    """
    This form is used to handle the search functionality in the chat application.
    It contains two fields: 'query' and 'engine'.
    The 'query' field is used to take the user's input.
    The 'engine' field is used to select the AI model that will process the query.
    """

    query = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Posez votre question...",
                "autofocus": "autofocus",
                "class": (
                    "flex items-center h-10 w-full rounded-lg px-3 "
                    "text-sm pr-12 responsive-width"
                ),
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
    """
    This form is used for debugging purposes. It contains fields for selecting the AI model,
    the category, the prompt, and the query. The 'engine' field is used to select the AI model.
    The 'category' field is used to select the category.
    The 'prompt' field is used to input the prompt.
    The 'query' field is used to input the query.
    """

    ENGINE_CHOICES = [
        ("gpt-3.5-turbo", "ChatGPT 3.5"),
        ("gpt-3.5-turbo-instruct", "GPT 3.5 instruct"),
        ("gpt-4", "ChatGPT 4"),
        ("mistral_instruct", "Mistral Instruct"),
        ("falcon", "Falcon"),
        ("paradigm", "LightOn"),
        ("vertexai", "VertexAI"),
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
        required=False,
        widget=forms.Textarea(
            attrs={"style": "font-family:monospace;", "cols": "120", "rows": "4"}
        ),
    )

    class Meta:
        """
        Meta class for DebugForm. It specifies the model to be used and the fields
        to be included in the form.
        """

        model = Category
        fields = ["prompt", "k", "query"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["category"].initial = self.instance.id
            self.fields["prompt"].initial = self.instance.prompt
            self.fields["k"].initial = self.instance.k
        self.order_fields(["category", "prompt", "k", "engine", "raw_input", "query"])


class DebugVectorForm(forms.ModelForm):
    """
    This form is used for debugging vector operations.
    It contains fields for selecting the category,
    the 'k' value, and the query.
    The 'category' field is used to select the category.
    The 'k' field is used to input the 'k' value.
    The 'query' field is used to input the query.
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"id": "category-select"}),
    )
    query = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"style": "font-family:monospace;", "cols": "120", "rows": "4"}
        ),
    )

    class Meta:
        """
        This is the Meta class for DebugVectorForm. It specifies the model to be used and the
        fields to be included in the form.
        """

        model = Category
        fields = ["k", "query"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["category"].initial = self.instance.id
            self.fields["k"].initial = self.instance.k
        self.order_fields(["category", "k", "query"])
