from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import ObjectDoesNotExist
from .forms import CorrectionForm
from .models import Category, Correction


def correct(request, category_id):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=category_id)
        # Update the request's POST data to include the category_id
        data = request.POST.copy()
        data.update({"category": category_id})

        form = CorrectionForm(data)
        if form.is_valid():
            correction = form.save(commit=False)
            if form.cleaned_data.get('mark_as_deleted'):
                # The 'mark as deleted' box was checked
                correction = Correction.objects.get(
                    category=category, query=form.cleaned_data["query"]
                )
                correction.delete()
            else:
                try:
                    # Try to get an existing correction
                    correction = Correction.objects.get(
                        category=category, query=form.cleaned_data["query"]
                    )
                    # Update existing correction
                    correction.query = form.cleaned_data["query"]
                    correction.answer = form.cleaned_data["answer"]
                    correction.save()
                except ObjectDoesNotExist:
                    # If it doesn't exist, create a new one
                    form.save()

            return JsonResponse(
                {"status": "success", "message": "Correction saved successfully."},
                status=201,
            )

    # You could return a different response if the method is not POST or the form is invalid
    return JsonResponse({"status": "error"})
