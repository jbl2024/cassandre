# chat/forms.py
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Posez votre question...', 'class': 'flex items-center h-10 w-full rounded px-3 text-sm pr-12'}), label='')
