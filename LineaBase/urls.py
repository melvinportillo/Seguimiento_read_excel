from django.urls import path, re_path
from .views import Subir_Linea, Drive_manage, Crear_Encuesta, Nueva_Pregunta, Excel_to_bd
from .views import Graficos

app_name = 'lineabase'
urlpatterns = [
    path('subir/', Subir_Linea.as_view(), name="subir"),
    path('drive/',Drive_manage.as_view(), name='drive'),
    path('crear_1/',Crear_Encuesta.as_view(),name='crear'),
    path('nueva_pregutna/', Nueva_Pregunta.as_view(),name='nueva_pregunta'),
    path('graficos/', Graficos.as_view(),name='graficos'),
    path('excel_to_bd/',Excel_to_bd.as_view(),name = "excel"),

]
