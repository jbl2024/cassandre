# chat/forms.py
from django import forms
from .models import Category, Correction

class CorrectionForm(forms.ModelForm):
    class Meta:
        model = Correction
        fields = ['query', 'answer', 'category']

    def __init__(self, *args, **kwargs):
        super(CorrectionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
