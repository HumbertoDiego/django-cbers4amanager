# Generated by Django 4.0.3 on 2022-04-18 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0019_alter_composicaorgb_rgb_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pansharpened',
            name='pansharp',
            field=models.FilePathField(blank=True, help_text='Este arquivo será criado após escolher a opção "Começar Fusão RGB/PAN das linhas selecionadas". ', match='(.*).tif', max_length=300, null=True, path='/home/capdiego/Documents/cbers4a/uploads/pansharp'),
        ),
    ]