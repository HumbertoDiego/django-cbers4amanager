# Generated by Django 4.0.2 on 2022-04-16 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0015_alter_inomclippered_nome_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inomclippered',
            name='area_util',
            field=models.CharField(blank=True, help_text='Este dados será computado após escolher a opção "Começar recorte RGB das linhas selecionadas". Equivale ao "STATISTICS_VALID_PERCENT" mínimo entre as bandas RGB, obtido pelo comando gdalinfo.', max_length=10, null=True, verbose_name='Área útil (%)'),
        ),
    ]