# Generated by Django 3.1.1 on 2021-05-24 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myfrstapp', '0005_tipo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tipo',
            old_name='tipo',
            new_name='tipo_usuario',
        ),
    ]
