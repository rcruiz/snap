from django.db import models

# Create your models here.
class proyectos(models.Model):
    usuario= models.CharField(max_length=50, null=False)
    url_proyecto = models.CharField(max_length=100, unique=True, null=False)
    nivel=models.CharField(max_length=50, null=False)
