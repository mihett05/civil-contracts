from django import forms


class WorkerSelectForm(forms.Form):
    worker = forms.ChoiceField()
