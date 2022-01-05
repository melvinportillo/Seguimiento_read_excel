import os

from django.db import models

# Create your models here.
class Temp_Pregunta(models.Model):
    Usuario= models.CharField(max_length=15)
    Num= models.IntegerField()
    Tipo= models.CharField(max_length=10)
    Enunciado = models.CharField(max_length=100)
    Opciones = models.CharField(max_length=100)

class pregunta(models.Model):
    Usuario = models.CharField(max_length=15)
    Num_Encuesta = models.IntegerField()
    Num = models.IntegerField()
    Tipo = models.CharField(max_length=10)
    Enunciado = models.CharField(max_length=100)
    Opciones = models.CharField(max_length=100)

class Linea_Base(models.Model):
    Usuario = models.CharField(max_length=15)
    Xml = models.FileField(upload_to='LineaBase/Xmls')
    Nombre_proyecto = models.CharField(max_length=50)
    Nombre_encuesta = models.CharField(max_length=50)
    Folder_id = models.CharField(max_length=100)
    File_Id = models.CharField(max_length=100)
    File_url = models.CharField(max_length=100)

    def filename(self):
         return os.path.basename(self.Xml.name)

class Temp_Linea_Base(models.Model):
    Usuario = models.CharField(max_length=15, default="user0")
    Xml = models.FileField(upload_to='LineaBase/Xmls')
    Nombre_proyecto = models.CharField(max_length=50)
    Nombre_encuesta = models.CharField(max_length=50)
    Folder_id = models.CharField(max_length=100)
    File_Id = models.CharField(max_length=100)
    File_url = models.CharField(max_length=100)

    def filename(self):
         return os.path.basename(self.Xml.name)


class Datos_Encuestas(models.Model):
    Usuario = models.CharField(max_length=30)
    Encuesta = models.IntegerField()
    Num_Pregunta = models.IntegerField()
    Label = models.CharField(max_length=100)
    Clase = models.CharField(max_length=100)
    Frecuencia = models.IntegerField()

class Coordenadas(models.Model):
    Encuesta=  models.IntegerField()
    Encuestado= models.CharField(max_length=50)
    Sexo= models.CharField(max_length=10)
    DNI_Encuestado= models.CharField(max_length=15)
    Estado_civil = models.CharField(max_length=10)
    Num_telefono = models.CharField(max_length=15)
    Diosesis = models.CharField(max_length=30)
    Latitud= models.CharField(max_length=11)
    Longitud= models.CharField(max_length=11)
    Altitud= models.CharField(max_length=11)
    Geolocalizacion_acuracy = models.CharField(max_length=15)
    Link_foto= models.CharField(max_length=100)