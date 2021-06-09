from django.urls import path

from .views import index, select_periods,  select_people, load_people_view


urlpatterns = [
    path("", index),
    path("select/", select_periods),
    path("select_people/", select_people),
    path("load_people/", load_people_view),
]
