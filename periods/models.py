from django.db import models

from people.models import Worker


class Service(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.TextField()


class Period(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    price = models.FloatField()
    services = models.ManyToManyField(Service)

    def __str__(self):
        return f"{str(self.start)} - {str(self.end)}"
