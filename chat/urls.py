from django.urls import path

from .views import SearchAPIView, AsyncSearchView, debug, debug_vector, search

urlpatterns = [
    path(
        "api/v1/search/<str:category_slug>/", SearchAPIView.as_view(), name="search_api"
    ),
    path('api/v1/async_search/', AsyncSearchView.as_view(), name='async_search_api'),
    path("search/<str:category_slug>/", search, name="search"),
    path("search/", search, name="search"),
    path("__internal_cas_debug__/", debug, name="debug"),
    path("__internal_cas_debug_vector__/", debug_vector, name="debug_vector"),
]
