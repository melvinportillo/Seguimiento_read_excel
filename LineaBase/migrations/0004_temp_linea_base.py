# Generated by Django 3.2.6 on 2021-08-28 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineaBase', '0003_auto_20210828_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temp_Linea_Base',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Usuario', models.CharField(max_length=15)),
                ('Xml', models.FileField(upload_to='LineaBase/Xmls')),
                ('Nombre_proyecto', models.CharField(max_length=50)),
                ('Nombre_encuesta', models.CharField(max_length=50)),
                ('Folder_id', models.CharField(max_length=100)),
                ('File_Id', models.CharField(max_length=100)),
                ('File_url', models.CharField(max_length=100)),
            ],
        ),
    ]