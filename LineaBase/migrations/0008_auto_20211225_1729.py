# Generated by Django 3.1.13 on 2021-12-25 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LineaBase', '0007_rename_frecuecia_datos_encuestas_frecuencia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datos_encuestas',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='linea_base',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='temp_linea_base',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='temp_pregunta',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
