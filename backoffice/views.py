import os
import zipfile

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from documents.models import Category, Correction, Document

from .forms import FileUploadForm


class CategoryListView(UserPassesTestMixin, ListView):
    model = Category
    template_name = "backoffice/category_list.html"

    def test_func(self):
        return self.request.user.is_staff


class DocumentListView(UserPassesTestMixin, ListView):
    model = Document
    template_name = "backoffice/document_list.html"

    def test_func(self):
        return self.request.user.is_staff


class CorrectionListView(UserPassesTestMixin, ListView):
    model = Correction
    template_name = "backoffice/correction_list.html"

    def test_func(self):
        return self.request.user.is_staff


class CategoryDetailView(UserPassesTestMixin, FormView, DetailView):
    model = Category
    template_name = "backoffice/category_detail.html"
    form_class = FileUploadForm

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return self.request.path  # Stay on the same page after form submission

    def form_valid(self, form):
        category = self.get_object()
        handle_uploaded_file(
            form.cleaned_data["file"], category
        )  # Assuming this function handles the file upload
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs["pk"])
        context["documents"] = Document.objects.filter(category=category)
        context["corrections"] = Correction.objects.filter(category=category)
        return context


def handle_uploaded_file(f, category):
    with zipfile.ZipFile(f, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            title, ext = os.path.splitext(file_name)  # split the filename and extension

            if not Document.objects.filter(
                title=title, category=category
            ).exists():  # if document doesn't exist, create it
                file_content = zip_ref.read(file_name)  # get the content of the file

                document = Document()
                document.category = category
                document.title = title

                # create a Django ContentFile to pass into FileField
                django_file = ContentFile(file_content)
                document.file.save(file_name, django_file, save=True)
