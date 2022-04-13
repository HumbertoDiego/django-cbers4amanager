# Generated by Django 4.0.3 on 2022-04-12 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbers4amanager', '0003_alter_download_url_alter_inom_inom'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='tipo',
            field=models.CharField(blank=True, choices=[('red', 'Vermelho'), ('green', 'Verde'), ('blue', 'Azul'), ('pan', 'Pancromática'), ('', 'Indefinido')], default='', max_length=5, null=True),
        ),
    ]