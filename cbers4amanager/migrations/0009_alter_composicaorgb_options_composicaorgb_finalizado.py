# Generated by Django 4.0.2 on 2022-04-15 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0008_alter_composicaorgb_options_alter_download_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='composicaorgb',
            options={'verbose_name': 'Composição RGB'},
        ),
        migrations.AddField(
            model_name='composicaorgb',
            name='finalizado',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]