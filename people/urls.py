from django.urls import path

from .views import people_list, add_worker, edit_worker, delete_worker

urlpatterns = [
    path("", people_list),
    path("add/", add_worker),
    path("edit/<int:worker_id>", edit_worker),
    path("delete/<int:worker_id>", delete_worker)
]
