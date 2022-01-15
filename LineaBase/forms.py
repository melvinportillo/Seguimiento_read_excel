from django import  forms
from .models import Temp_Linea_Base

Preguntas=[('text', 'Texto'),
           ('num','Númerico'),
           ('Multi','Selección Multiple'),
            ('Uni', "Selección Única"), ('foto','Foto'), ('Loca', 'Ubicación')
           ]

class Linea_Base_form(forms.ModelForm):

    class Meta:
        model = Temp_Linea_Base
        fields = ("Xml","Nombre_proyecto","Nombre_encuesta")






