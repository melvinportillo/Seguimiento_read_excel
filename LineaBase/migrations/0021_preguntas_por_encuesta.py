# Generated by Django 3.1.13 on 2022-04-01 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineaBase', '0020_auto_20220331_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preguntas_por_encuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Numero_preguntas', models.IntegerField()),
                ('Pregunta', models.CharField(max_length=300)),
                ('Num_encuesta', models.IntegerField()),
            ],
        ),
    ]
