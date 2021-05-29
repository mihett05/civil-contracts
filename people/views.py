from django.shortcuts import render, HttpResponseRedirect, Http404

from .models import Worker
from .forms import WorkerForm


def people_list(request):
    return render(request, "people/people_list.html", {
        "list": sorted(Worker.objects.all(), key=lambda x: x.name),
        "labels": [
            "ФИО", "Дата рождения", "Адрес проживания",
            "Серия, Номер", "Дата выдачи", "Паспорт выдан"
        ]
    })


def add_worker(request):
    if request.method == "POST":
        form = WorkerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/people/")
    else:
        form = WorkerForm()
    return render(request, "people/people_add.html", {
        "form": form
    })


def edit_worker(request, worker_id):
    worker = Worker.objects.filter(pk=worker_id).first()

    if not worker:
        return Http404()

    if request.method == "POST":
        form = WorkerForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/people/")
    else:
        form = WorkerForm(instance=worker)

    return render(request, "people/people_edit.html", {
        "form": form
    })


def delete_worker(request, worker_id):
    worker = Worker.objects.filter(pk=worker_id).first()

    if not worker:
        return Http404()

    worker.delete()

    return HttpResponseRedirect("/people/")
