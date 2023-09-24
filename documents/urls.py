from django.urls import path

from .views import correct

urlpatterns = [
    path("correct/<int:category_id>/", correct, name="correct"),
]
