# Generated by Django 3.1.1 on 2021-05-27 17:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myfrstapp', '0011_auto_20210527_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proyectos',
            name='nombre_proyecto',
        ),
    ]
