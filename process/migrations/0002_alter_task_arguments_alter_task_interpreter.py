# Generated by Django 4.0.2 on 2022-04-14 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='arguments',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='arguments'),
        ),
        migrations.AlterField(
            model_name='task',
            name='interpreter',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='interpreter'),
        ),
    ]
