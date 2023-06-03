from django.urls import path
from .views import CategoryDetailView, CategoryListView, DocumentListView, CorrectionListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('documents/', DocumentListView.as_view(), name='documents'),
    path('corrections/', CorrectionListView.as_view(), name='corrections'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),    
]