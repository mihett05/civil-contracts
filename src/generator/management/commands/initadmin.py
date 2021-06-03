import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(
                email=os.environ.get("ADMIN_EMAIL"),
                username=os.environ.get("ADMIN_LOGIN"),
                password=os.environ.get("ADMIN_PASSWORD")
            )
            admin.is_active = True
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
