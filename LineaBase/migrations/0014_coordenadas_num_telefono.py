# Generated by Django 3.1.13 on 2021-12-31 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineaBase', '0013_coordenadas_dni_encuestado'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordenadas',
            name='Num_telefono',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
    ]
