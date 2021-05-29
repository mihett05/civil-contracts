from django.urls import path

from .views import index, select_periods


urlpatterns = [
    path("", index),
    path("select/", select_periods)
]
