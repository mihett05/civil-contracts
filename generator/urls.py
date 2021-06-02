from django.urls import path

from .views import index, select_periods, load_people_view


urlpatterns = [
    path("", index),
    path("select/", select_periods),
    path("load_people/", load_people_view)
]
