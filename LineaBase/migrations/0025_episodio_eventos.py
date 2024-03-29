# Generated by Django 4.2 on 2023-04-26 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineaBase', '0024_alter_coordenadas_altitud'),
    ]

    operations = [
        migrations.CreateModel(
            name='Episodio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Actor_s', models.CharField(max_length=50)),
                ('Actor_r', models.CharField(max_length=50)),
                ('Ubicacion', models.CharField(max_length=25)),
                ('Lugar', models.CharField(max_length=30)),
                ('Descripion_episodio', models.CharField(max_length=500)),
                ('Zona', models.CharField(max_length=10)),
                ('Medida_pre', models.CharField(max_length=40)),
                ('Alcance', models.CharField(max_length=30)),
                ('Nivel', models.CharField(max_length=20)),
                ('Grado', models.CharField(max_length=30)),
                ('Respuesta', models.CharField(max_length=30)),
                ('Key_ep', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Eventos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fecha', models.CharField(max_length=12)),
                ('Departamento', models.CharField(max_length=20)),
                ('Resumen', models.CharField(max_length=500)),
                ('Sector', models.CharField(max_length=20)),
                ('Fuente_info', models.CharField(max_length=200)),
                ('Foto', models.CharField(max_length=100)),
                ('Link', models.CharField(max_length=100)),
                ('Desenlace', models.CharField(max_length=300)),
                ('Key_id', models.CharField(max_length=30)),
            ],
        ),
    ]
