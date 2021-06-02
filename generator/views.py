import json
import os
import io
import random
import string
import zipfile
import shutil
from urllib.parse import quote
from datetime import date

from docxtpl import DocxTemplate
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage

from people.models import Worker
from periods.models import Period, services

from .forms import WorkerSelectForm
from .contracts import group_periods_by_services, unite_contracts
from .excel import load_people
from .num_to_text import num2text


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
            worker_text = f"{worker.name}, именуем(ая)ый в дальнейшем «Исполнитель», {worker.birth}г. рождения, " \
                          f"проживающ(ая)ый по адресу: {worker.address}, паспорт: {str(worker.passport_serial)[:2]} "\
                    f"{str(worker.passport_serial)[2:4]} №{str(worker.passport_serial)[4:]}, {worker.passport_date},"\
                          f"{worker.passport_issuer}"
            price_text = num2text(int(contract["price"]), (("рубль", "рубля", "рублей"), "m")).capitalize().split()
            price_num = "{:,}".format(int(contract["price"])).replace(",", " ")
            start = date(*reversed(list(map(int, contract["range"].split("по")[0][1:].strip()[:-2].split(".")))))
            date_text = f"«{start.strftime('%d')}» m {start.year}г.".replace("m", {
                1: "января",
                2: "февраля",
                3: "марта",
                4: "апреля",
                5: "мая",
                6: "июня",
                7: "июля",
                8: "августа",
                9: "сентября",
                10: "октября",
                11: "ноября",
                12: "декабря",
            }[start.month])

            doc = DocxTemplate("templates/template.docx")
            doc.render({
                "worker": worker_text,
                "service_name": contract["service"],
                "service_list": services[contract["service"]]["list"],
                "service_paragraph_2": services[contract["service"]]["2"],
                "range": contract["range"],
                "price": f"{price_num} ({' '.join(price_text[:-1])}) {price_text[-1]}",
                "date": date_text
            })
            file = f"{dir_name}/{contract['range']}_{contract['service']}_{worker.name}.docx"
            files.append(file)
            doc.save(file)

        stream = io.BytesIO()
        zf = zipfile.ZipFile(stream, "w")
        for file in files:
            zf.write(file, file[len(dir_name):])
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
