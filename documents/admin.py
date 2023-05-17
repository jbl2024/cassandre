from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.http import urlencode

from .models import Category, Document
from .tasks import index_documents, index_documents_in_category


def index_documents_action(modeladmin, request, queryset):
    index_documents.delay()
    modeladmin.message_user(request, 'Documents indexing has started, please wait for completion')
index_documents_action.short_description = 'Index selected documents'

def index_documents_in_category_action(modeladmin, request, queryset):
    for category in queryset:
        index_documents_in_category.delay(category.id) 
    modeladmin.message_user(request, 'Documents indexing has started, please wait for completion')
index_documents_action.short_description = 'Index documents for given category'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file', 'title', 'category')
    list_filter = ['category', ]

    actions = [index_documents_action]

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1  # number of extra forms to display


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'prompt':
            formfield.widget = forms.Textarea(attrs={'style': 'font-family:monospace;', 'cols': '120'})
        return formfield
    actions = [index_documents_in_category_action]
