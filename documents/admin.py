# pylint: disable=missing-docstring
import os
import re
from tempfile import TemporaryDirectory, TemporaryFile
from zipfile import ZipFile

from django import forms
from django.contrib import admin
from django.core.files.storage import default_storage
from django.http import FileResponse

from ai.tasks import index_documents, index_documents_in_category

from .models import Category, Correction, Document


def sanitize_filename(filename):
    """
    Sanitize a filename by removing characters that could cause issues.
    """
    return re.sub(r"(?u)[^-\'’ \w.]", "", filename.strip())


def index_documents_action(modeladmin, request):
    """
    This function triggers the indexing of documents.
    """
    index_documents.delay()
    modeladmin.message_user(
        request, "Documents indexing has started, please wait for completion"
    )


index_documents_action.short_description = "Index selected documents"


def index_documents_in_category_action(modeladmin, request, queryset):
    """
    This function triggers the indexing of documents in a specific category.
    """
    for category in queryset:
        index_documents_in_category.delay(category.id)
    modeladmin.message_user(
        request, "Documents indexing has started, please wait for completion"
    )


index_documents_action.short_description = "Index documents for given category"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("file", "title", "category")
    list_filter = [
        "category",
    ]
    actions = [index_documents_action]


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1  # number of extra forms to display


class CorrectionInline(admin.TabularInline):  # New Inline class for Correction
    model = Correction
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [DocumentInline, CorrectionInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "prompt":
            formfield.widget = forms.Textarea(
                attrs={"style": "font-family:monospace;", "cols": "120"}
            )
        return formfield

    def download_files(self, _request, queryset):
        # Create a temporary directory to store the files
        with TemporaryDirectory() as tmp_dir:
            for category in queryset:
                documents = Document.objects.filter(category=category)
                for document in documents:
                    if document.title:
                        sanitized_title = sanitize_filename(document.title)
                        original_extension = os.path.splitext(document.file.name)[1]
                        new_file_name = f"{sanitized_title}{original_extension}"
                    else:
                        new_file_name = document.file.name.split("/")[
                            -1
                        ]  # Use the original file name

                    file_path = os.path.join(tmp_dir, new_file_name)
                    if default_storage.exists(document.file.name):
                        with default_storage.open(document.file.name, "rb") as file:
                            file_content = file.read()
                            with open(file_path, "wb") as local_file:
                                local_file.write(file_content)

            # Create a temporary file to store the zip
            zip_file = TemporaryFile()

            with ZipFile(zip_file, "w") as zipfile:
                # go through each file in the temporary directory and add to zip
                for root, _dirs, files in os.walk(tmp_dir):
                    for file in files:
                        zipfile.write(os.path.join(root, file), arcname=file)

            zip_file.seek(0)

            # Create a file response to download the zip
            response = FileResponse(
                zip_file, as_attachment=True, filename="documents.zip"
            )

            return response

    download_files.short_description = "Download documents for selected categories"
    actions = [
        index_documents_in_category_action,
        download_files,
    ]  # Add the new action to the existing ones


@admin.register(Correction)
class CorrectionAdmin(admin.ModelAdmin):
    list_display = ("category", "query", "answer", "corrected_at")
    list_filter = [
        "category",
    ]
