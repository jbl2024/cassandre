# chat/views.py
from django.http import JsonResponse
from django.shortcuts import render
from .forms import SearchForm
from documents.models import Document, Category
from documents.search import search_documents
from django.core import serializers

def document_to_dict(document):
    return {
        'page_content': document.page_content,
        'metadata': document.metadata,
    }

def search(request, category='documents'):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            engine = form.cleaned_data['engine'] or "gpt-3.5-turbo"  # Set the engine value to "gpt-3.5-turbo" if it is null
            history = form.cleaned_data['history'] or ""
            results = search_documents(query, history, engine, category)  # Use the search_documents function
            return JsonResponse({
                'result': results['result'],
                'source_documents': []
            })
    else:
        form = SearchForm()

    category = Category.objects.get(slug=category)
    return render(request, 'chat/search.html', {'form': form, 'category': category})
