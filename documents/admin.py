from django.contrib import admin
from .models import Document
from django.core.management import call_command

def index_documents_action(modeladmin, request, queryset):
    call_command('index_documents')
    modeladmin.message_user(request, 'Documents have been indexed successfully')
index_documents_action.short_description = 'Index selected documents'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    actions = [index_documents_action]
