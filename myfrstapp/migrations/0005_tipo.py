# Generated by Django 3.1.1 on 2021-05-24 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myfrstapp', '0004_delete_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='tipo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=50, unique=True)),
                ('tipo', models.CharField(max_length=50)),
            ],
        ),
    ]