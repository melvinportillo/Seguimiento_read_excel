from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import Linea_Base_form
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from .models import Eventos, Episodio, Temp_Linea_Base, Linea_Base, Temp_Pregunta, Datos_Encuestas, Coordenadas, Encuestas, Tabla_encuestas, Preguntas_por_encuesta
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
            if ("</instance>" in l) or ( "<data id=" in l):
                if "</instance>" in l:
                    archivo.write(l)
                    nueva_l = "<submission method=\"form-data-post\" action=\""+ datos.File_url+ "\"/\n>"
                    archivo.write(nueva_l)
                else:
                    archivo.write(l.replace("snapshot_xml", Nombre_E + "_xml"))
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
        Num_encuesta_pre = request.POST['Pregunta']
        dat=Num_encuesta_pre.split(',')
        # Agregar Validación

        lista_preg=Datos_Encuestas.objects.filter(Num_Pregunta=dat[0], Encuesta=dat[1])
        L=[]
            # Loading Data from a Static JSON String
            # It is a example to show a Pie 3D chart where data is passed as JSON string format.
            # The `chart` method is defined to load chart data from an JSON string.


        # Create an object for the pie3d chart using the FusionCharts class constructor
        #[lista_preg[0].Label, 'Cantidad']
        dic={"chart": {

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
        n = "\n"
        option1 = f'<option value="">{Preguntas_por_encuesta.objects.get(Numero_preguntas=dat[0], Num_encuesta=dat[1])}</option>' + n
        for i in Preguntas_por_encuesta.objects.filter(Num_encuesta=dat[1]):
            if i != Preguntas_por_encuesta.objects.get(Numero_preguntas=dat[0], Num_encuesta=dat[1]):
                value = str(i.Numero_preguntas) + ',' + str(dat[1])
                txt = i.Pregunta
                option1 = option1 + f'<option value="{value}">{txt}</option>' + n

        return render(request, "Lineas_Base/graficos.html", {'output': pie3d.render(), 'Encuesta': Tabla_encuestas.objects.get(Numero=dat[1]),
                   'Pregunta': Preguntas_por_encuesta.objects.get(Numero_preguntas=dat[0]), 'Form': option1})

class Geocoordenadas(TemplateView):
    def get(self,request,*args, **kwargs):

        '''excel_sheet = pd.ExcelFile('static/Archivo/datos.xlsx')
        hoja1 = excel_sheet.parse('Hoja 1')

        for j in range(len(hoja1)):
            ev = Eventos(
                Fecha = hoja1['aB7UW7jj8Tk9gZycMGrgXz-Fecha_del_Evento'][j],
                Departamento = hoja1['aB7UW7jj8Tk9gZycMGrgXz-Departamento_del_Monitor'][j],
                Resumen = hoja1['aB7UW7jj8Tk9gZycMGrgXz-Resumen_del_Conflicto'][j],
                Sector = hoja1['aB7UW7jj8Tk9gZycMGrgXz-_A_qu_sector_corresponde_la_d'][j],
                Fuente_info = hoja1['aB7UW7jj8Tk9gZycMGrgXz-_C_mo_se_obtuvo_la_informaci_n'][j],
                Foto = hoja1['aB7UW7jj8Tk9gZycMGrgXz-Fotograf_a'][j],
                Link = hoja1['aB7UW7jj8Tk9gZycMGrgXz-Enlace_de_la_Fuente'][j],
                Desenlace = hoja1['aB7UW7jj8Tk9gZycMGrgXz-_Cu_l_fue_el_desenlace_del_conflicto'][j],
                Key_id = hoja1['KEY'][j],
            )
            ev.save()

        hoja2 = excel_sheet.parse('aB7UW7jj8Tk9gZycMGrgXz-group_ab')
        for j in range(len(hoja1)):
            ep = Episodio(
                Actor_s = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Qui_n_es_el_actor_solicitante'][j],
                Actor_r = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Qui_n_es_el_actor_requerido_o'][j],
                Ubicacion = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-Ubicaci_n'][j],
                Lugar = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_En_qu_lugar_se_dio_el_conflicto'][j],
                Descripion_episodio = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Descripci_n_del_Episodio'][j],
                Zona = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_A_qu_zona_pertenece_el_conflicto'][j],
                Medida_pre = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Qu_tipo_de_medida_de_presi_n'][j],
                Alcance = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Cu_l_fue_el_alcance_del_hecho_conflicto'][j],
                Nivel = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Cu_l_fue_el_nivel_d_idad_en_el_conflicto'][j],
                Grado = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Cu_l_fue_el_grado_d_n_en_este_conflicto'][j],
                Respuesta = hoja2['aB7UW7jj8Tk9gZycMGrgXz-group_ab37j61-_Cu_l_es_la_respuest_nte_a_este_conflicto'][j],
                Key_ep = hoja2['PARENT_KEY'][j],
            )
            ep.save()'''

        # Create Map Object
        m = folium.Map(location=[14.8, -86.241905], zoom_start=8,  control_scale=True)
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
        evento=Eventos.objects.all()

        for i in evento:

            api = Episodio.objects.filter(Key_ep=i.Key_id)
            #formato de tabl

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

            html1 = f"""
                            <h2> Evento </h2>
                            <body>
                            <table>
                            <tr>
                            <th colspan="2">Datos generales</th>
                            </tr>
                            <tr>
                                <td>Fecha</td>
                                <td>{i.Fecha}</td>
                            </tr>
                            <tr>
                                <td>Departamento</td>
                                <td>{i.Departamento}</td>
                            </tr>
                            <tr>
                                <td>Resumen</td>
                                <td>{i.Resumen}</td>
                            </tr>
                            <tr>
                                <td>Sector</td>
                                <td>{i.Sector}</td>
                            </tr>
                            
                            </table>
                            <br>

                           
                            """
            v = 1
            g = ''
            for j in api:
                c = j.Ubicacion

                html2 = f"""
                                <table>
                                <tr>
                                <th colspan="2">Episodio {v}</th>
                                </tr>
                                <tr>
                                    <td>Actor solicitante</td>
                                    <td>{j.Actor_s}</td>
                                </tr>
                                <tr>
                                    <td>Actor Requerido</td>
                                    <td>{j.Actor_r}</td>
                                </tr>
                                <tr>
                                    <td>Lugar de conflicto</td>
                                    <td>{j.Lugar}</td>
                                </tr>
                                <tr>
                                    <td>Descripción de Episodio</td>
                                    <td>{j.Descripion_episodio}</td>
                                </tr>
                                <tr>
                                    <td>Zona</td>
                                    <td>{j.Zona}</td>
                                </tr>
                                <tr>
                                    <td>Tipo de medida de presión</td>
                                    <td>{j.Medida_pre}</td>
                                </tr>
                                <tr>
                                    <td>Alcance</td>
                                    <td>{j.Alcance}</td>
                                </tr>
                                <tr>
                                    <td>Nivel de conflicto</td>
                                    <td>{j.Nivel}</td>
                                </tr>
                                <tr>
                                    <td>Grado</td>
                                    <td>{j.Grado}</td>
                                </tr>
                                <tr>
                                    <td>Respuesta</td>
                                    <td>{j.Respuesta}</td>
                                </tr>                                
                                </table>
                                <br>
                """
                v = v+1
                g=g+html2
            if i.Foto == ' ':
                se = f''' <table>
                                <tr>
                                <th colspan="2">¿Cómo se obtuvo la información del conflicto?</th>
                                </tr>
                                <tr>
                                    <td>Fuente secundaria (Monitorio de medio de comunicación)</td>
                                    <td>{i.Link}</td>
                                </tr>
                                </table>
                                <br>'''
            else:
                r = i.Foto
                print (r)
                n = r.split('id=')
                se = f'''
                            <p align="left">Fuente primaria (Observación en campo)</p>
                            <img src="https://drive.google.com/uc?id={n[1]}" width="420"></body>
                '''
            html = html_format + html1 + g +se
            coor = c.split(',')
            lat = coor[0]
            lng = coor[1]
            iframe = folium.IFrame(html=html, width=450, height=400)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Marker([lat,lng], tooltip='Evento 1',
                          popup=popup, name='Evento').add_to(marker_cluster)
        #search
        servicesearch = Search(
            layer=marker_cluster,
            search_label="name",
            placeholder='Buscar por Evento',
            collapsed=False,
        ).add_to(m)
        # Get HTML Representation of Map Object
        m = m._repr_html_()
        context = {
            'm': m,
        }

        return render(request,"Forms/Coordenadas.html",context)

class Giras(TemplateView):
    def get(self,request,*args,**kwargs):
        excel_sheet = pd.ExcelFile('static/Archivo/Datos.xlsx')
        hoja = excel_sheet.parse('Hoja 1')
        t=""
        mi_diccionario = {}
        for i in range(len(hoja)):
            c1 = hoja["Ubicación final"][i]
            c0 = hoja["Ubicación inicial"][i]
            coor0 = c0.split(',')
            coor1 = c1.split(',')
            m = folium.Map(location=[coor0[0], coor0[1]], zoom_start=8, control_scale=True)
            marker_cluster = MarkerCluster().add_to(m)
            # añadir estilos de mapas
            folium.TileLayer('Stamen Terrain').add_to(m)
            folium.TileLayer('Stamen Toner').add_to(m)
            folium.TileLayer('Stamen Water Color').add_to(m)
            folium.TileLayer('cartodb positron').add_to(m)
            folium.TileLayer('cartodb dark_matter').add_to(m)
            folium.LayerControl().add_to(m)
            f1 = hoja["Foto Kilometraje inicial "][i]
            f2 = hoja["Foto de kilometraje final "][i]
            if not (f1 == ' '):
                foto1 = f1.split("id=")[1]
            if not (f2 == ' '):
                foto2 = f2.split("id=")[1]

            if c1 == ' ':
                txtr = "Sin recorrido"
            else:
                txtr = "Recorrido"
            s = str(c0)+','+str(c1)
            celdas = f'''<tr>
                <td>{hoja["Llave de la gira"][i]}</td>
                <td>{hoja["Unidad"][i]}</td>
                <td>{hoja["Especifíque"][i]}</td>
                <td>{hoja["Objetivo"][i]}</td>
                <td>{hoja["Vehículo asignado"][i]}</td>
                <td>{hoja["Placa del vehículo"][i]}</td>
                <td><span onclick="showPopup1(event, this, '{s}')">{txtr}</span></td>
                <td><span onclick="showPopup(event, '{foto1}')" >{hoja["Kilometráje inicial"][i]}</span></td>
                <td><span onclick="showPopup(event, '{foto2}')">{hoja["Kilometraje final"][i]}</span></td>
                <td>{hoja["Observaciones"][i]}</td>
              </tr>'''
            t=t+celdas

        return render(request, "Forms/Giras.html", {'t':t, 'diccionario': mi_diccionario})
class Diagnostico(TemplateView):
    def get(self, request, *args, **kwargs):
        excel_sheet = pd.ExcelFile('static/Archivo/Datos.xlsx')
        hoja = excel_sheet.parse('Hoja1')
        j=''
        for i in range(len(hoja)):
            k = f'''<option class= "op" value="{hoja["Tema de la capacitación"][i]}&=&{hoja["Llave de la capacitación "][i]}&=&{hoja["Unidad "][i]}&=&{hoja["Técnico "][i]}&=&{hoja["Proyecto"][i]}&=&{hoja["Ubicación"][i]}&=&{hoja["Fecha"][i]}&=&{hoja["Prueba d1"][i]}&=&{hoja["Prueba d2"][i]}&=&{hoja["Prueba d3"][i]}&=&{hoja["Prueba d4"][i]}&=&{hoja["Prueba F1"][i]}&=&{hoja["Prueba F2"][i]}&=&{hoja["Prueba F3"][i]}&=&{hoja["Prueba F4"][i]}&=&{hoja["Asistencia "][i]}&=&{hoja["Foto del evento"][i]}&=&{hoja["Observaciones "][i]}">{hoja["Tema de la capacitación"][i]}</option>
            '''
            j=j+k
        return render(request, "Forms/Diagnostico.html", {'tr':j})
class Preguntas(TemplateView):
    template_name = "Lineas_Base/graficos_form.html"
    def post(self,request,*args, **kwargs):
        Num_Encuesta = request.POST['Encuesta']
        option1 = ''
        for i in Preguntas_por_encuesta.objects.filter(Num_encuesta=Num_Encuesta):
            value = str(i.Numero_preguntas)+','+str(Num_Encuesta)
            txt = i.Pregunta
            n = "\n"
            option1 = option1 + f'<option value="{value}">{txt}</option>' + n

        option=f'<option value="">{Tabla_encuestas.objects.get(Numero=Num_Encuesta)}</option>'
        for ii in Tabla_encuestas.objects.all():
            if Tabla_encuestas.objects.get(Numero=ii.Numero)!=Tabla_encuestas.objects.get(Numero=Num_Encuesta):
                value = ii.Numero
                txt = ii.Encuesta
                n="\n"
                option = option + f'<option value="{value}">{txt}</option>'+n
        return render(request, "Lineas_Base/graficos_form.html",{'option1':option1,'option':option})

class Excel_to_bd(TemplateView):
    def get(self, request, *args, **kwargs):
        #Script for authorization of pydrive.
        '''gauth = GoogleAuth()
        gauth.LocalWebserverAuth()'''

        # Download the specific sheet in Google Spreadsheet as a CSV data.
        excel_sheet = pd.ExcelFile('static/Archivo/Preguntas_encuestas.xlsx')
        hoja=excel_sheet.parse('Hojas')

        for i in range(int(hoja['Total'][0])):
            if Tabla_encuestas.objects.filter(Encuesta=hoja['Encuesta'][i]).count()==0:
                ob=Tabla_encuestas(
                    Encuesta=hoja['Encuesta'][i],
                    Sheet_Id=hoja['Sheet_Id'][i],
                    Hoja = hoja['Hoja'][i],
                    Numero = int(hoja['Numero'][i])
                )
                ob.save()
                #hojas de encuesta
                hoja_encuesta = excel_sheet.parse(hoja['Hoja'][0])
                for j in range(len(hoja_encuesta)):
                    enc = Encuestas(
                        Num_encuesta = int(hoja['Numero'][i]),
                        Numero_preg = hoja_encuesta['Numero'][j],
                        Pregunta = hoja_encuesta['Pregunta'][j],
                        Tipo_preg = hoja_encuesta['Tipo_de_pregunta'][j],
                        Columna = hoja_encuesta['Columnas'][j],
                        Label = hoja_encuesta['Label'][j],
                        Label_en_sheet = hoja_encuesta['Label_en_sheet'][j],
                        Filas_preg_tipo_matriz = hoja_encuesta['Fila_es_tipo_matriz'][j],
                        Otros = hoja_encuesta['Otro'][j]
                    )
                    enc.save()
                    if Preguntas_por_encuesta.objects.filter(Numero_preguntas=hoja_encuesta['Numero'][j]).count()==0:
                        preg = Preguntas_por_encuesta(
                            Numero_preguntas=hoja_encuesta['Numero'][j],
                            Pregunta = hoja_encuesta['Pregunta'][j],
                            Num_encuesta = int(hoja['Numero'][i]),
                        )
                        preg.save()

        #spreadsheetId = '1NOuAwCEBfAKK8-tWMHMmMxx8wiOmUnLaubvoOnkwfHI'  # Please set the Spreadsheet ID.
        #spreadsheetId = '1gYy1qmrRlwEYUunI4ikT7Zku-RXt8qfdlAxW-3ZY478'
        #spreadsheetId=hoja['Sheet_Id'][0]

        '''sheetId = '0'  # Please set the sheet ID. (GID)
        url = 'https://docs.google.com/spreadsheets/d/' + spreadsheetId + '/gviz/tq?tqx=out:csv&gid=' + sheetId
        headers = {'Authorization': 'Bearer ' + gauth.credentials.access_token}
        res = requests.get(url, headers=headers)
        with open('File.csv', 'wb') as f:
            f.write(res.content)
        #convertir csv en dataframe
        df = pd.read_csv('File.csv',encoding='latin-1')'''
        df = pd.ExcelFile('static/Archivo/datos.xlsx')
        dc = {}
        for n in df:
            dc[n] = pd.value_counts(df[n])
        #procesar encuestas tipo seleccion unica
        for i in Encuestas.objects.filter(Tipo_preg = '1'):
            if i.Label_en_sheet=='1':
                continue
            s = Datos_Encuestas(
                Usuario=request.user.username,
                Encuesta=i.Num_encuesta,
                Num_Pregunta=i.Numero_preg,
                Label=i.Pregunta,
                Clase=i.Label,
                Frecuencia=dc[i.Columna][i.Label_en_sheet]
            )
            s.save()


        # procesar encuestas tipo seleccion multiple
        '''band = int(Encuestas.objects.filter(Tipo_preg='2').first().Numero_preg)+2
        for i in Encuestas.objects.filter(Tipo_preg='2'):
            if i.Numero_preg != band:
                dic={}
                for j in Encuestas.objects.filter(Numero_preg=i.Numero_preg):
                    dic[j.Label_en_sheet]=j.Label
                list_labels={}
                for k in dc[i.Columna].index:
                    r = k.split(', ')
                    for l in r:
                        if l in list_labels:
                            tem=int(dc[i.Columna][k])+list_labels[l]
                            list_labels[l]=tem
                        else:
                            list_labels[l] = int(dc[i.Columna][k])
                for m in list_labels:
                    if m == ' ':
                        continue
                    s = Datos_Encuestas(
                        Usuario=request.user.username,
                        Encuesta=i.Num_encuesta,
                        Num_Pregunta=i.Numero_preg,
                        Label=i.Pregunta,
                        Clase=dic[m],
                        Frecuencia=list_labels[m]
                    )
                    s.save()
                band = i.Numero_preg
           # for i in dc[i]:


        print (dc['aoZe8AcWNPjQizMNXi5nYo-_Las_familias_ahora_con_mejores_ingresos']['generados_por_proyectos_financiados'])
        for i in dc:
            print(dc[i])
        for i in dc:
            print (i)
            l = dc[i].index.tolist()
            l1 = dc[i].tolist()

            dc_frecuencias = {}
            for j in range(len(l)):
                l3=Datos_Encuestas.objects.filter(Usuario=request.user.username, Encuesta=4).count()
                if l3==0:
                    altclase1=(str(l[j]).replace('_', ' '))
                    if len(altclase1)<2:
                        altclase1='Null'
                    altclase=altclase1.encode('latin1').decode('utf8')

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
                                    Clase=k,#.encode('latin1').decode('utf8')
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
                    if len(altclase1) < 2:
                        altclase1 = 'Null'
                    altclase = altclase1.encode('latin1').decode('utf8')

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

        l4 = Coordenadas.objects.filter(Encuesta=3).count()
        if l4 == 0:
            for j in range (len(df['data-start'])):
                if len(df['data-Nombre_de_la_persona_encuestada'][j])<=1:
                    continue
                coor=df['data-Geo_localizaci_n'][j].split(',')
                a = Coordenadas(
                    Encuesta=3,
                    Encuestado = df['data-Nombre_de_la_persona_encuestada'][j].encode('latin1').decode('utf8'),
                    Sexo = df['data-Sexo_de_la_persona_encuestada'][j],
                    DNI_Encuestado = df['data-N_mero_de_DNI_de_la_persona_encuestada'][j].encode('latin1').decode('utf8'),
                    Estado_civil = df['data-Estado_civil_de_la_persona_encuestada'][j].encode('latin1').decode('utf8'),
                    Num_telefono = df['data-N_mero_de_tel_fono_d_a_persona_encuestada'][j].encode('latin1').decode('utf8'),
                    Diosesis = df['data-Di_cesis'][j],
                    Latitud = coor[0],
                    Longitud = coor[1],
                    Altitud = df['data-Geo_localizaci_n-altitude'][j],
                    Geolocalizacion_acuracy = df['data-Geo_localizaci_n-accuracy'][j],
                    Link_foto = df['data-Fotograf_a_de_la_persona_encuestada'][j]
                )
                a.save()'''
        option="<option value="">Seleccionar</option>"
        n = "\n"
        for ii in Tabla_encuestas.objects.all():
            value = ii.Numero
            txt = ii.Encuesta

            option = option + f'<option value="{value}" >{txt}</option>'+n
        option1=''

        return render(request, "Lineas_Base/graficos_form.html", {'option': option, 'option1': option1})
