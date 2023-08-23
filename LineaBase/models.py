import os

from django.db import models

# Create your models here.
#from LineaBase.forms import Preguntas


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
    Label = models.CharField(max_length=500)
    Clase = models.CharField(max_length=500)
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
    Altitud= models.CharField(max_length=25)
    Geolocalizacion_acuracy = models.CharField(max_length=15)
    Link_foto= models.CharField(max_length=100)

class Tabla_encuestas(models.Model):
    Encuesta = models.CharField(max_length=100)
    Sheet_Id = models.CharField(max_length=60)
    Hoja = models.CharField(max_length=50)
    Numero = models.IntegerField()

    def __str__(self):
        return self.Encuesta


class Encuestas(models.Model):
    Num_encuesta = models.IntegerField()
    Numero_preg = models.IntegerField()
    Pregunta = models.CharField(max_length=300)
    Tipo_preg = models.IntegerField()
    Columna = models.CharField(max_length=100)
    Label = models.CharField(max_length=500)
    Label_en_sheet = models.CharField(max_length=50)
    Filas_preg_tipo_matriz = models.CharField(max_length=200)
    Otros = models.CharField(max_length=500)

class Preguntas_por_encuesta(models.Model):
    Numero_preguntas = models.IntegerField()
    Pregunta = models.CharField(max_length=300)
    Num_encuesta = models.IntegerField()
    def __str__(self):
        return self.Pregunta
class Eventos(models.Model):
    Fecha = models.CharField(max_length=12)
    Departamento = models.CharField(max_length=20)
    Resumen = models.CharField(max_length=500)
    Sector = models.CharField(max_length=20)
    Fuente_info = models.CharField(max_length=200)
    Foto = models.CharField(max_length=100)
    Link = models.CharField(max_length=100)
    Desenlace = models.CharField(max_length=300)
    Key_id = models.CharField(max_length=30)

class Episodio(models.Model):
    Actor_s = models.CharField(max_length=50)
    Actor_r = models.CharField(max_length=50)
    Ubicacion = models.CharField(max_length=25)
    Lugar = models.CharField(max_length=30)
    Descripion_episodio = models.CharField(max_length=500)
    Zona = models.CharField(max_length=10)
    Medida_pre = models.CharField(max_length=40)
    Alcance = models.CharField(max_length=30)
    Nivel = models.CharField(max_length=20)
    Grado = models.CharField(max_length=30)
    Respuesta = models.CharField(max_length=30)
    Key_ep = models.CharField(max_length=30)






