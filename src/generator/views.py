import json
import os
import io
import random
import string
import zipfile
import shutil
from urllib.parse import quote, parse_qs

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage

from people.models import Worker
from periods.models import Period

from .forms import WorkerSelectForm
from .contracts import group_periods_by_services, unite_contracts, make_word
from .excel import load_people



def index(request):
    choices = [(worker.pk, worker.name) for worker in sorted(Worker.objects.all(), key=lambda x: x.name)]
    form = WorkerSelectForm()
    form.fields["worker"].choices = choices
    return render(request, "generator/index.html", {
        "form": form
    })


@require_POST
def load_people_view(request):
    if "file" in request.FILES and request.FILES["file"]:
        file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save("".join(random.sample(string.ascii_lowercase, 16)) + "." + file.name.split(".")[-1], file)
        load_people(os.path.join("media", filename))
        fs.delete(filename)
    return HttpResponseRedirect("/")


def select_periods(request):
    if request.method == "POST":
        contracts = list(map(json.loads, request.POST.getlist("contracts")))
        worker = Worker.objects.filter(pk=int(request.GET["worker"])).first()

        dir_name = f"media/{worker.name}_" + "".join(random.sample(string.ascii_lowercase, 8))
        os.mkdir(dir_name)
        files = []

        for contract in contracts:
            files.append(make_word(contract, worker, dir_name))

        stream = io.BytesIO()
        zf = zipfile.ZipFile(stream, "w")
        for file in files:
            zf.write(file, file[len(dir_name):])  # убираю путь папки из названия
        shutil.rmtree(dir_name)

        resp = HttpResponse(stream.getvalue(), "application/x-zip-compressed")
        resp["Content-Disposition"] = f"attachment; filename={quote(worker.name)}.zip"

        return resp
    else:
        choices = [(worker.pk, worker.name) for worker in sorted(Worker.objects.all(), key=lambda x: x.name)]
        select_form = WorkerSelectForm(request.GET)
        select_form.fields["worker"].choices = choices

        if not select_form.is_valid():
            return HttpResponseRedirect("/")

        worker = Worker.objects.filter(pk=int(select_form.cleaned_data["worker"])).first()
        worker_periods = Period.objects.filter(worker=worker).all()
        contracts = unite_contracts(group_periods_by_services(worker_periods))

        for contract in contracts:
            contract["value"] = json.dumps(contract)

        return render(request, "generator/select.html", {
            "contracts": contracts,
            "worker": worker
        })


def select_people(request):
    workers = Worker.objects.all()

    if request.method == "POST":
        data = list(map(lambda x: x.decode("utf-8"), parse_qs(request.body, encoding="utf-8").keys()))
        data.remove("csrfmiddlewaretoken")
        data = list(map(int, data))
        contracts_workers = list(filter(lambda x: x.pk in data, workers))

        dirs = dict()

        for worker in contracts_workers:
            periods = Period.objects.filter(worker=worker).all()
            contracts = unite_contracts(group_periods_by_services(periods))
            dir_name = f"media/{worker.name}_" + "".join(random.sample(string.ascii_lowercase, 8))
            os.mkdir(dir_name)
            dirs[dir_name] = []
            for contract in contracts:
                dirs[dir_name].append(make_word(contract, worker, dir_name))

        stream = io.BytesIO()

        zf = zipfile.ZipFile(stream, "w")
        for directory in dirs:
            for file in dirs[directory]:
                zf.write(file, file[len(directory):])  # убираю путь папки из названия
            shutil.rmtree(directory)

        resp = HttpResponse(stream.getvalue(), "application/x-zip-compressed")
        resp["Content-Disposition"] = f"attachment; filename={quote('Договоры')}.zip"

        return resp

    else:
        return render(request, "generator/select_people.html", {
            "workers": workers
        })
