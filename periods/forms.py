from django import forms

from .models import Period


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ["start", "end", "price", "service"]
        labels = {
            "start": "Дата начала",
            "end": "Дата окончания",
            "price": "Стоимость",
            "service": "Услуги"
        }

        widgets = {
            "service": forms.Select
        }
