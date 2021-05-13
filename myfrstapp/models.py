from django.db import models

# Create your models here.
class proyectos(models.Model):
    usuario= models.CharField(max_length=50)
    url_proyecto = models.CharField(max_length=100)
