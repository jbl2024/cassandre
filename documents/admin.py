from django.contrib import admin
from documents.tasks import index_documents
from documents.models import Document

def index_documents_action(modeladmin, request, queryset):
    index_documents.delay()
    modeladmin.message_user(request, 'Documents indexing has started, please wait for completion')
index_documents_action.short_description = 'Index selected documents'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    actions = [index_documents_action]