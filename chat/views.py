# chat/views.py
from django.shortcuts import render
from .forms import SearchForm
from documents.models import Document
from documents.search import search_documents

def search(request):
    results = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = search_documents(query) # Use the search_documents function
    else:
        form = SearchForm()

    return render(request, 'chat/search.html', {'form': form, 'results': results})
