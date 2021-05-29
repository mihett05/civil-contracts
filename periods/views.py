from django.shortcuts import render, HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Worker, Period, Service
from .forms import PeriodForm, ServiceForm


def periods(request):
    workers = sorted(Worker.objects.all(), key=lambda x: x.name)
    return render(request, "periods/periods.html", {
        "workers": workers,
        "selected": int(request.GET.get("selected", workers[0].pk if len(workers) > 0 else 0)),
    })


def add_period(request, worker_id):
    workers = Worker.objects.all()
    worker = Worker.objects.filter(pk=worker_id).first()

    if not worker:
        return Http404()

    if request.method == "POST":
        form = PeriodForm(request.POST)
        form.fill_choices()
        if form.is_valid():
            period = Period(
                worker=worker,
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                price=form.cleaned_data["price"]
            )
            period.save()
            form.apply_services(period)

            return HttpResponseRedirect(f"/periods/?selected={worker.pk}")
        else:
            return render(request, "periods/period_add.html", {
                "workers": workers,
                "selected": worker_id,
                "form": form,
            })
    else:
        form = PeriodForm()
        form.fill_choices()

    return render(request, "periods/period_add.html", {
        "workers": workers,
        "selected": worker_id,
        "form": form
    })


def get_periods(request, worker_id):
    worker = Worker.objects.get(pk=worker_id)
    worker_periods = Period.objects.filter(worker=worker).all()

    return JsonResponse({"periods": [{
        "id": period.pk,
        "start": period.start,
        "end": period.end,
        "price": period.price,
        "services": [service.pk for service in period.services.all()],
    } for period in sorted(worker_periods, key=lambda x: x.start)]})


@require_POST
def edit_period(request, period_id):
    period = Period.objects.filter(pk=period_id).first()
    if not period:
        return Http404()

    form = PeriodForm(request.POST, instance=period)
    if form.is_valid():
        form.save()
        form.apply_services(period)
    return HttpResponseRedirect(f"/periods/?selected={period.worker.pk}")


def del_period(request, period_id):
    period = Period.objects.filter(pk=period_id).first()
    if not period:
        return Http404()

    period.delete()
    return HttpResponseRedirect(f"/periods/?selected={period.worker.pk}")


def get_services(request):
    services = Service.objects.all()
    return render(request, "periods/services.html", {
        "services": services
    })


def get_services_list(request):
    services = Service.objects.all()
    return JsonResponse({service.pk: service.name for service in services})


def add_service(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/periods/services/")
    else:
        form = ServiceForm()

    return render(request, "periods/service_add.html", {
        "form": form
    })


def edit_service(request, service_id):
    service = Service.objects.filter(pk=service_id).first()

    if not service:
        return Http404()

    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/periods/services/")
    else:
        form = ServiceForm(instance=service)

    return render(request, "periods/service_edit.html", {
        "form": form
    })


def del_service(request, service_id):
    service = Service.objects.filter(pk=service_id).first()

    if not service:
        return Http404()

    service.delete()
    return HttpResponseRedirect("/periods/services/")
