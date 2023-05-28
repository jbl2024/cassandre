# chat/forms.py
from django import forms
from .models import Category, Correction


class CorrectionForm(forms.ModelForm):
    mark_as_deleted = forms.BooleanField(required=False)

    class Meta:
        model = Correction
        fields = ["query", "answer", "category", "mark_as_deleted"]

    def __init__(self, *args, **kwargs):
        super(CorrectionForm, self).__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
