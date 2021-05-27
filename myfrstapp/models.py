from django.db import models

# Create your models here.
class proyectos(models.Model):
    usuario= models.CharField(max_length=50, null=False)
    url_proyecto = models.CharField(max_length=100, null=False)
    name_proyecto = models.CharField(max_length=100, null=False)
    nombre_zip=models.CharField(max_length=100, null=True)
    nivel=models.CharField(max_length=50, null=False)
    condicionales = models.IntegerField(null=False, default=0)
    sincronizacion = models.IntegerField(null=False, default=0)
    control_flujo = models.IntegerField(null=False, default=0)
    abstraccion = models.IntegerField(null=False, default=0)
    paralelismo = models.IntegerField(null=False, default=0)
    categorias = models.IntegerField(null=False, default=0)
    interactividad = models.IntegerField(null=False, default=0)


class tipo(models.Model):
    usuario= models.CharField(max_length=50, null=False, unique=True)
    tipo_usuario=models.CharField(max_length=50, null=False)
