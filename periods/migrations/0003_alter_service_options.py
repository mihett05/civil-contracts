# Generated by Django 3.2.3 on 2021-05-19 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0002_auto_20210519_1605'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['name']},
        ),
    ]
