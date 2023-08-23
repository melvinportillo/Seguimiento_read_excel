from django import forms
from django.forms import ModelChoiceField

from .models import Temp_Linea_Base, Tabla_encuestas, Preguntas_por_encuesta

Preguntas=[('text', 'Texto'),
           ('num','Númerico'),
           ('Multi','Selección Multiple'),
            ('Uni', "Selección Única"), ('foto','Foto'), ('Loca', 'Ubicación')
           ]

class Linea_Base_form(forms.ModelForm):

    class Meta:
        model = Temp_Linea_Base
        fields = ("Xml","Nombre_proyecto","Nombre_encuesta")

'''class EncuestasForm(forms.ModelForm):
    Encuesta = ModelChoiceField(queryset=Tabla_encuestas.objects.all(),label='Encuesta',to_field_name="Numero")

    class Meta:
        model = Tabla_encuestas
        fields = ["Encuesta"]
'''








