from django import forms

from .models import Worker


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            "name", "birth", "address",
            "passport_serial", "passport_date",
            "passport_issuer"
        ]
        
        labels = {
            "name": "Наименование",
            "birth": "Дата рождения",
            "address": "Адрес проживания",
            "passport_serial": "Серия, номер паспорта",
            "passport_date": "Дата выдачи паспорта",
            "passport_issuer": "Паспорт выдан"
        }

