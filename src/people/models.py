from django.db import models


class Worker(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=256)
    birth = models.CharField(max_length=10)
    address = models.CharField(max_length=256)
    passport_serial = models.IntegerField()
    passport_date = models.CharField(max_length=10)
    passport_issuer = models.CharField(max_length=256)

    def __str__(self):
        return f"Worker({self.name})"
