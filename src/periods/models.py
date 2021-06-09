from django.db import models

from people.models import Worker

from .services import service_tech, service_expert, service_org, service_info, service_accountant


services = {
    "технические": service_tech,
    "экспертные": service_expert,
    "организационно-методические": service_org,
    "информационно-библиографические": service_info,
    "бухгалтерские": service_accountant,
}


class Period(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    price = models.FloatField()

    service_choices = [(service, service) for service in services.keys()]
    service = models.CharField(
        max_length=64,
        choices=service_choices,
        default="технические"
    )

    def __str__(self):
        return f"{str(self.start)} - {str(self.end)}"
