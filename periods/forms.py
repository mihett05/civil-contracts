from django import forms

from .models import Period, Service


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ["start", "end", "price", "services"]
        labels = {
            "start": "Дата начала",
            "end": "Дата окончания",
            "price": "Стоимость",
            "services": "Услуги"
        }
        widgets = {
            "services": forms.CheckboxSelectMultiple
        }

    def fill_choices(self):
        self.fields["services"].choices = [[service.pk, service.name] for service in Service.objects.all()]

    def apply_services(self, period):
        period.services.add(*self.cleaned_data["services"])


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name"]
        labels = {
            "name": "Название услуги"
        }
