# chat/forms.py
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your question...'}), label='')
