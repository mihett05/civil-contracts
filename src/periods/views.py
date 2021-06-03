from django.shortcuts import render, HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Worker, Period, services
from .forms import PeriodForm


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
        if form.is_valid():
            period = Period(
                worker=worker,
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                price=form.cleaned_data["price"],
                service=form.cleaned_data["service"]
            )
            period.save()

            return HttpResponseRedirect(f"/periods/?selected={worker.pk}")
        else:
            return render(request, "periods/period_add.html", {
                "workers": workers,
                "selected": worker_id,
                "form": form,
            })
    else:
        form = PeriodForm()

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
        "service": period.service,
    } for period in sorted(worker_periods, key=lambda x: x.start)]})


@require_POST
def edit_period(request, period_id):
    period = Period.objects.filter(pk=period_id).first()
    if not period:
        return Http404()

    form = PeriodForm(request.POST, instance=period)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(f"/periods/?selected={period.worker.pk}")


def del_period(request, period_id):
    period = Period.objects.filter(pk=period_id).first()
    if not period:
        return Http404()

    period.delete()
    return HttpResponseRedirect(f"/periods/?selected={period.worker.pk}")


def get_services_list(request):
    return JsonResponse({"services": list(services.keys())})
