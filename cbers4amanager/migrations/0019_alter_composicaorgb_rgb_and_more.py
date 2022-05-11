# Generated by Django 4.0.3 on 2022-04-18 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0018_pansharpened_finalizado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='composicaorgb',
            name='rgb',
            field=models.FilePathField(blank=True, help_text='Este arquivo será criado após escolher a opção "Começar composição das linhas selecionadas".', match='(.*)RGB.tif', null=True, path='/home/capdiego/Documents/cbers4a/uploads/rgbs'),
        ),
        migrations.AlterField(
            model_name='inomclippered',
            name='recorte_pancromatica',
            field=models.FilePathField(blank=True, help_text='Este arquivo será criado após escolher a opção "Começar recorte PAN das linhas selecionadas".', match='(.*)PAN.tif', max_length=300, null=True, path='/home/capdiego/Documents/cbers4a/uploads/recortes'),
        ),
        migrations.AlterField(
            model_name='inomclippered',
            name='recorte_rgb',
            field=models.FilePathField(blank=True, help_text='Este arquivo será criado após escolher a opção "Começar recorte RGB das linhas selecionadas". ', match='(.*)RGB.tif', max_length=300, null=True, path='/home/capdiego/Documents/cbers4a/uploads/recortes'),
        ),
        migrations.AlterField(
            model_name='pansharpened',
            name='pansharp',
            field=models.FilePathField(blank=True, null=True, path='/home/capdiego/Documents/cbers4a/uploads/pansharp'),
        ),
    ]