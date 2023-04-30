# chat/forms.py
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Posez votre question...', 'class': 'flex items-center h-10 w-full rounded px-3 text-sm pr-12'}), label='')
    engine = forms.CharField(widget=forms.HiddenInput(), required=False, initial="gpt-3.5-turbo")  # Set the default value for the "engine" field
    history = forms.CharField(widget=forms.HiddenInput(), required=False)  # Add a hidden input field for the history
    