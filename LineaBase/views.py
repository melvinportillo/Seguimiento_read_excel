from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import  Linea_Base_form
from pydrive.auth import  GoogleAuth
from pydrive.drive import GoogleDrive
from .models import Temp_Linea_Base, Linea_Base, Temp_Pregunta, Datos_Encuestas, Coordenadas
from .utils.xform_tools import formversion_pyxform
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart, BarChart, PieChart, ColumnChart
import pandas as pd
import requests
import io
import gdown
from googleapiclient.http import MediaIoBaseDownload

import folium
from folium import plugins
from folium.plugins import MarkerCluster
from folium.plugins import Search
import geocoder

import json

from django.shortcuts import render
from django.http import HttpResponse

            # Include the `fusioncharts.py` file which has required functions to embed the charts in html page
from .fusioncharts import FusionCharts


# Create your views here.

class Subir_Linea(TemplateView):


    def post(self,request, *args, **kwargs):
        form = Linea_Base_form(request.POST, request.FILES)
        if form.is_valid():
            Temp_Linea_Base.objects.all().delete()
            Linea_Base.objects.all().delete()

            form.save()
            return redirect("lineabase:drive")

    def get(self, request, *args, **kwargs):
        form = Linea_Base_form


        return  render(request, "Lineas_Base/Crear_Linea_Base.html",{'formulario':form})


class Drive_manage (TemplateView):

    def __init__(self):
        self.drive = "s"
    def autenticar(self):
            ga = GoogleAuth()
            ga.LocalWebserverAuth()
            #ga.LoadCredentialsFile("mycreds.txt")
            self.drive= ga

    def crear_carpeta(self):
            dr = GoogleDrive(self.drive)
            datos = Temp_Linea_Base.objects.get(Usuario= "user0")
            Proyecto = datos.Nombre_proyecto
            folder = dr.CreateFile({'title': Proyecto, "mimeType": "application/vnd.google-apps.folder"})
            folder.Upload()
            datos.Folder_id = folder['id']
            datos.Usuario = self.request.user.username
            datos.save()

    def crear_archivo_excel(self):
        dr = GoogleDrive(self.drive)
        datos = Temp_Linea_Base.objects.get(Usuario=self.request.user.username)
        nombre_e = datos.Nombre_encuesta
        folder = datos.Folder_id
        sheel = dr.CreateFile({
            'title': nombre_e,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id':folder}]

        })
        sheel.Upload()
        permiso = sheel.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'writer'
        })
        link = sheel['alternateLink']
        id = sheel['id']
        datos.File_Id=id
        datos.File_url=link
        datos.save()

    def preparar_archivo(self):
        datos = Temp_Linea_Base.objects.get(Usuario=self.request.user.username)
        Nombre_E = datos.Nombre_encuesta
        archivo_name= "LineaBase/Xmls/"+Nombre_E + ".xml"
        name_orginal = datos.filename()
        archivo_orginal = "LineaBase/Xmls/"+ name_orginal

        archivo = open(archivo_name, 'w')
        f = open(archivo_orginal,'r')
        lineas = f.readlines()
        for linea in lineas:
            l = str(linea)
            if "</instance>" in l:
                archivo.write(l)
                nueva_l = "<submission method=\"form-data-post\" action=\""+ datos.File_url+ "\"/\n>"
                archivo.write(nueva_l)
            else:
                archivo.write(l)
        archivo.close()


    def subir_archivo(self):
        datos = Temp_Linea_Base.objects.get(Usuario=self.request.user.username)
        Nombre_E = datos.Nombre_encuesta
        archivo_name = "LineaBase/Xmls/" + Nombre_E + ".xml"
        Fo_if = datos.Folder_id
        dr = GoogleDrive(self.drive)
        A = dr.CreateFile()
        A.SetContentFile(archivo_name)
        A['title']= Nombre_E + ".xml"
        A['parents'] = [{"kind": "drive#parentReference", "id": Fo_if}]
        A.Upload()
        datos.File_Id = A['id']



    def get(self, request, *args, **kwargs):
        self.autenticar()
        self.crear_carpeta()
        self.crear_archivo_excel()
        self.preparar_archivo()
        self.subir_archivo()


        return redirect("inicio")



class Crear_Encuesta(TemplateView):

    def get(self, request, *args, **kwargs):
        pyxform_survey = formversion_pyxform({
            'survey': [
                {'type': 'text',
                 'name': 'Nombre',
                 'label': 'Nombre'},
                {'type': 'select one sexo',
                 'name': 'Sexo',
                 'label': 'Sexo'},
                {'type': 'int',
                 'name': 'Edad',
                 'label': 'Edad'},
                {'type': 'location',
                 'name': 'Posicion',
                 'label': 'Posicion'},


            ],
            'choices': [
                {'list_name': 'sexo', 'value': 'F', 'label': 'Femenino'},
                {'list_name': 'sexo', 'value': 'M', 'label': 'Masculino'},
            ],
            'settings': {'id_string': 'simple',
                         'title': 'Ejemplo_1',
                         'name': 'data'}
        })



        file = "LineaBase/Xmls/"+"prueba"+".xml"
        f = open(file,'w')
        f.write(pyxform_survey.to_xml())

        return  redirect("lineabase:subir")


class Nueva_Pregunta(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, "Lineas_Base/Nueva_Pregunta.html")

    def post(self,request,*args,**kwargs):
        Tipo_Pregunta = request.POST['Tipo_q']
        Enunciado = request.POST['Enunciado']
        Opciones = request.POST['Opciones']
        # Agregar validación

        c = Temp_Pregunta.objects.filter(Usuario=request.user.username).count()

        if Tipo_Pregunta == 'text':
            n = Temp_Pregunta(
                Usuario= request.user.username,
                Num= c +1,
                Tipo='text',
                Enunciado = Enunciado,
                Opciones =Opciones
            )
            n.save()



class Graficos(TemplateView):
    template_name = "Lineas_Base/graficos_form.html"

    def post(self,request,*args, **kwargs):
        Num_Encuest = request.POST['Encuesta']
        Num_Preguta = request.POST['Pregunta']
        # Agregar Validación
        lista_preg=Datos_Encuestas.objects.filter(Num_Pregunta=Num_Preguta)
        L=[]



            # Loading Data from a Static JSON String
            # It is a example to show a Pie 3D chart where data is passed as JSON string format.
            # The `chart` method is defined to load chart data from an JSON string.


        # Create an object for the pie3d chart using the FusionCharts class constructor
        #[lista_preg[0].Label, 'Cantidad']
        dic={"chart": {
             "caption": str(lista_preg[0].Label),
             "showValues":"1",
             "showPercentInTooltip" : "0",
             "numberPrefix" : "Cantidad: ",
             "enableMultiSlicing":"1",
             "theme": "fusion"
         }}
        dic1={}
        for i in lista_preg:
            dic1["label"]=str(i.Clase)
            dic1["value"]=str(i.Frecuencia)
            L.append(str(dic1))

        dic["data"]=L


                             # The data is passed as a string in the `dataSource` as parameter.
        pie3d = FusionCharts("pie3d", "ex2", "100%", "400", "chart-1", "json",str(dic))

        # returning complete JavaScript and HTML code, which is used to generate chart in the browsers.
       # return render(request, 'index.html', {'output': pie3d.render(), 'chartTitle': 'Pie 3D Chart'})
        context = {'Encuesta': Num_Encuest,
                   'Pregunta': Num_Preguta
                   }
        return render(request, "Lineas_Base/graficos.html", {'output': pie3d.render(), 'chartTitle': 'Resultados', 'Encuesta': Num_Encuest,
                   'Pregunta': Num_Preguta})

class Geocoordenadas(TemplateView):
    def get(self,request,*args, **kwargs):

        '''if lat == None or lng == None:
            address.delete()
            return HttpResponse('You address input is invalid')'''

        # Create Map Object
        m = folium.Map(location=[15.199999, -86.241905], zoom_start=8,  control_scale=True)
        #crear marcas
        marker_cluster = MarkerCluster().add_to(m)
        #añadir estilos de mapas
        folium.TileLayer('Stamen Terrain').add_to(m)
        folium.TileLayer('Stamen Toner').add_to(m)
        folium.TileLayer('Stamen Water Color').add_to(m)
        folium.TileLayer('cartodb positron').add_to(m)
        folium.TileLayer('cartodb dark_matter').add_to(m)
        folium.LayerControl().add_to(m)
        #filtrar encuestados por nombre de encuesta
        Encuestados_por_encuesta=Coordenadas.objects.filter(Encuesta=3).count()

        for i in range(Encuestados_por_encuesta):
            lat = Coordenadas.objects.get(id=(i+1)).Latitud
            lng = Coordenadas.objects.get(id=(i + 1)).Longitud
            Nombre = Coordenadas.objects.get(id=(i + 1)).Encuestado
            DNI = Coordenadas.objects.get(id=(i + 1)).DNI_Encuestado
            Sexo = Coordenadas.objects.get(id=(i + 1)).Sexo
            Estado_civil = Coordenadas.objects.get(id=(i + 1)).Estado_civil
            Numero_de_telefono = Coordenadas.objects.get(id=(i + 1)).Num_telefono
            Diosesis = Coordenadas.objects.get(id=(i + 1)).Diosesis
            url = Coordenadas.objects.get(id=(i + 1)).Link_foto
            foto_id = url.split('id=')
            if len(foto_id) < 2:
                foto_id = ['d', 'd']
            #formato de tabla
            html_format="""<head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                        table {
                          border-collapse: collapse;
                          border-spacing: 0;
                          width: 100%;
                          border: 1px solid #ddd;
                        }
                        
                        th, td {
                          text-align: left;
                          padding: 16px;
                        }
                        
                        tr:nth-child(even) {
                          background-color: #f2f2f2;
                        }
                        </style>
                        </head>"""
            #datos de tabla
            html = html_format + f"""
                    <h2> {Nombre}</h2>
                    <body>
                    <table>
                    <tr>
                    <th colspan="2">Datos Generales</th>
                    </tr>
                    <tr>
                        <td>Nombre</td>
                        <td>{Nombre}</td>
                    </tr>
                    <tr>
                        <td>DNI</td>
                        <td>{DNI}</td>
                    </tr>
                    <tr>
                        <td>Sexo</td>
                        <td>{Sexo}</td>
                    </tr>
                    <tr>
                        <td>Estado cívil</td>
                        <td>{Estado_civil}</td>
                    </tr>
                    <tr>
                        <td>Teléfono</td>
                        <td>{Numero_de_telefono}</td>
                    </tr>
                    <tr>
                        <td>Diócesis</td>
                        <td>{Diosesis}</td>
                    </tr>
                    <tr>
                        <td>Coordenadas</td>
                        <td>{lat}, {lng}</td>
                    </tr>
                    </table>

                    </body>
                    <p align="left">Foto: </p>
                    <img src="https://drive.google.com/uc?id={foto_id[1]}" width="320">
                    """
            iframe = folium.IFrame(html=html, width=350, height=400)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Marker([lat, lng], tooltip=Nombre,
                          popup=popup, name=DNI).add_to(marker_cluster)
        #search
        servicesearch = Search(
            layer=marker_cluster,
            search_label="name",
            placeholder='Buscar por DNI',
            collapsed=False,
        ).add_to(m)
        # Get HTML Representation of Map Object
        m = m._repr_html_()
        context = {
            'm': m,
        }

        return render(request,"Coordenadas.html",context)

class Excel_to_bd(TemplateView):
    def get(self, request, *args, **kwargs):
        # Script for authorization of pydrive.
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        # Download the specific sheet in Google Spreadsheet as a CSV data.
        spreadsheetId = '1NOuAwCEBfAKK8-tWMHMmMxx8wiOmUnLaubvoOnkwfHI'  # Please set the Spreadsheet ID.
        sheetId = '0'  # Please set the sheet ID. (GID)
        url = 'https://docs.google.com/spreadsheets/d/' + spreadsheetId + '/gviz/tq?tqx=out:csv&gid=' + sheetId
        headers = {'Authorization': 'Bearer ' + gauth.credentials.access_token}
        res = requests.get(url, headers=headers)
        with open('File.csv', 'wb') as f:
            f.write(res.content)

        df = pd.read_csv('File.csv',encoding='latin-1')
        dc = {}
        lista_ignorar = ['data-start', 'data-end', 'data-meta-instanceID', 'data-Nombre_de_la_persona_encuestada',
                         'data-Sexo_de_la_persona_encuestada',
                         'data-Estado_civil_de_la_persona_encuestada', 'data-N_mero_de_DNI_de_la_persona_encuestada',
                         'data-N_mero_de_tel_fono_d_a_persona_encuestada', 'data-Fotograf_a_de_la_persona_encuestada',
                         'data-Geo_localizaci_n', 'data-Geo_localizaci_n-altitude', 'data-Geo_localizaci_n-accuracy',
                         'data-Di_cesis']
        for n in df:
            if not (n in lista_ignorar):
                dc[n] = pd.value_counts(df[n])

        num_preg=1
        for i in dc:
            l = dc[i].index.tolist()
            l1 = dc[i].tolist()
            alternativa = str(i).replace('data-', '')
            if alternativa[0:2]=='I_' or alternativa[0:3]=='II_' or alternativa[0:4]=='III_' or alternativa[0:3]=='IV_':
                continue
            x = 0
            dc_frecuencias = {}
            for j in range(len(l)):
                l3=Datos_Encuestas.objects.filter(Usuario=request.user.username, Encuesta=4).count()
                if l3==0:
                    altclase1=(str(l[j]).replace('_', ' '))
                    altclase=altclase1#.encode('latin1').decode('utf8')
                    if altclase==' ':
                        altclase='Null'
                    if j==0:
                        for g in range(len(l)):
                            if ', ' in str(l[g]):
                                x=num_preg
                                break

                    if x==num_preg:
                        lista_frecuencias_sm=[]
                        lista_seleccion_multiple=altclase.split(', ')
                        for s in lista_seleccion_multiple:
                            if s in dc_frecuencias:
                                frec=dc_frecuencias[s]+l1[j]
                            else:
                                frec=l1[j]
                            dc_frecuencias[s]=frec
                        if (j+1)==len(l):
                            for k in dc_frecuencias:
                                a = Datos_Encuestas(
                                    Usuario=request.user.username,
                                    Encuesta=3,
                                    Num_Pregunta=num_preg,
                                    Label=alternativa.replace('_', ' '),
                                    Clase=k,#.encode('latin1').decode('utf8'),
                                    Frecuencia=dc_frecuencias[k]
                                )
                                a.save()

                    else:
                        a = Datos_Encuestas(
                            Usuario=request.user.username,
                            Encuesta=3,
                            Num_Pregunta=num_preg,
                            Label=alternativa.replace('_', ' '),
                            Clase=altclase,
                            Frecuencia=int(l1[j])
                        )
                        a.save()
                else:
                    altclase1 = (str(l[j]).replace('_', ' '))
                    altclase = altclase1#.encode('latin1').decode('utf8')
                    if altclase == ' ':
                        altclase = 'Null'
                    l2=Datos_Encuestas.objects.filter(Usuario=request.user.username, Encuesta=3, Clase= altclase,
                                                      Num_Pregunta=num_preg)
                    count=l2.count()
                    if count==0:
                        a = Datos_Encuestas(
                            Usuario=request.user.username,
                            Encuesta=3,
                            Num_Pregunta=num_preg,
                            Label=alternativa,
                            Clase=altclase,
                            Frecuencia=int(l1[j])
                        )
                        a.save()
                    else:
                        t=l2.last()
                        t.Frecuencia=int(l1[j])
                        t.save()

            num_preg+=1
        l4 = Coordenadas.objects.filter(Encuesta=3).count()
        if l4 == 0:
            for j in range (len(df['data-start'])):
                coor=df['data-Geo_localizaci_n'][j].split(',')
                a = Coordenadas(
                    Encuesta=3,
                    Encuestado = df['data-Nombre_de_la_persona_encuestada'][j],
                    Sexo = df['data-Sexo_de_la_persona_encuestada'][j],
                    DNI_Encuestado = df['data-N_mero_de_DNI_de_la_persona_encuestada'][j],
                    Estado_civil = df['data-Estado_civil_de_la_persona_encuestada'][j],
                    Num_telefono = df['data-N_mero_de_tel_fono_d_a_persona_encuestada'][j],
                    Diosesis = df['data-Di_cesis'][j],
                    Latitud = coor[0],
                    Longitud = coor[1],
                    Altitud = df['data-Geo_localizaci_n-altitude'][j],
                    Geolocalizacion_acuracy = df['data-Geo_localizaci_n-accuracy'][j],
                    Link_foto = df['data-Fotograf_a_de_la_persona_encuestada'][j]
                )
                a.save()

        return redirect('lineabase:graficos')
