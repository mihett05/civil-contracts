from django.urls import path

from .views import periods, get_periods, edit_period, del_period, add_period,\
    get_services_list, add_service, edit_service, del_service, get_services

urlpatterns = [
    path("", periods),
    path("<int:worker_id>/", get_periods),
    path("edit/<int:period_id>/", edit_period),
    path("delete/<int:period_id>/", del_period),
    path("add/<int:worker_id>/", add_period),
    path("services/", get_services),
    path("services/list/", get_services_list),
    path("services/add/", add_service),
    path("services/edit/<int:service_id>", edit_service),
    path("services/delete/<int:service_id>", del_service)
]
