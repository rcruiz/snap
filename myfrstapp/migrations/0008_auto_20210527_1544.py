# Generated by Django 3.1.1 on 2021-05-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myfrstapp', '0007_auto_20210527_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyectos',
            name='nombre_proyecto',
            field=models.CharField(max_length=100),
        ),
    ]
