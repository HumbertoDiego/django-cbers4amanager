# Generated by Django 4.0.3 on 2022-04-20 13:09

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0024_alter_composicaorgb_rgb_alter_download_arquivo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='composicaorgb',
            name='bounds',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
    ]
