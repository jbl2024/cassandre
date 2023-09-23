# chat/forms.py
from django import forms
from .models import Category, Correction


class CorrectionForm(forms.ModelForm):
    """
    This is the CorrectionForm model form. It represents a form that can be used to create or update Correction instances.
    It has a BooleanField 'mark_as_deleted' which is not required by default.
    """
    mark_as_deleted = forms.BooleanField(required=False)

    class Meta:
        """
        Meta class for the CorrectionForm. It provides options to the model form including the model instance to be used
        and the fields that should be included in the form.
        """
        model = Correction
        fields = ["query", "answer", "category", "mark_as_deleted"]

    def __init__(self, *args, **kwargs):
        super(CorrectionForm, self).__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
