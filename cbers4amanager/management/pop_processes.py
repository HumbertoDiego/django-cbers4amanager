#!/usr/bin/env python
import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from process.models import Task, Process
from django.core.files import File
from django.db import connection
from pathlib import Path

def main():
    # Clean databse
    sql = "TRUNCATE pr_processes CASCADE;TRUNCATE pr_tasks CASCADE;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
    # Clean folder
    path = 'uploads/dj_process_tasks'
    for f in os.listdir(path):
        filename, file_extension = os.path.splitext(f)
        if file_extension in ['.py','.sh']:
            print(os.path.join(path,f))
            os.remove(os.path.join(path,f))
    # Inserts
    p1 = Process(
            name='Todo minuto',
            description='Todo minuto',
            run_if_err=True,
            minute='*',
            hour='*',
            day_of_month='*',
            month='*',
            day_of_week='*',
            chart_height=0
        )
    p1.save()
    t = Task(
        name='Download',
        description='Execução de todos os downloads cadastrados na tabela downloads com status não finalizado',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos',
        process_id=p1.id
    )
    path = Path('cbers4amanager/management/make_download.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    ##################### 
    p2=Process(
        name='Toda hora (1º min)',
        description='Toda hora (1º min)',
        run_if_err=True,
        minute='1',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=1
    )
    p2.save()
    t = Task(
        name='Transfer D',
        description='Tranferênica dos downloads com todas as bandas finalizadas para a tabela Composição RGB',
        is_active=True,
        level=1,
        offset='5%',
        interpreter='python',
        arguments='',
        process_id=p2.id
    )
    path = Path('cbers4amanager/management/transfer_download2composicaorgb.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p3=Process(
        name='Toda hora (10º min)',
        description='Toda hora (10º min)',
        run_if_err=True,
        minute='10',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=0
    )
    p3.save()
    t = Task(
        name='Comp RGB',
        description='Execução da composição de bandas dos objetos cadastradas na tabela Composição RGB',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos',
        process_id=p3.id
    )
    path = Path('cbers4amanager/management/make_composicaorgb.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p4=Process(
        name='Toda hora (30º min)',
        description='Toda hora (30º min)',
        run_if_err=True,
        minute='30',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=0
    )
    p4.save()
    t = Task(
        name='Transfer RGB',
        description='Tranferênica das composições RGB finalizadas para a tabela Recortes RGB/PAN',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='',
        process_id=p4.id
    )
    path = Path('cbers4amanager/management/transfer_composicaorgb2recorte.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    t = Task(
        name='Transfer PAN',
        description='Tranferênica das bandas PAN finalizadas para a tabela Recortes RGB/PAN',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='',
        process_id=p4.id
    )
    path = Path('cbers4amanager/management/transfer_bandapan2recorte.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p5=Process(
        name='Toda hora (40º min)',
        description='Toda hora (40º min)',
        run_if_err=True,
        minute='40',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=0
    )
    p5.save()
    t = Task(
        name='Recorte RGB',
        description='Execução dos recortes das composições RGB cadastrados e não finalizados na tabela Recortes RGB/PAN e cálculo sumário da área útil e com nuvens',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos --rgb',
        process_id=p5.id
    )
    path = Path('cbers4amanager/management/make_recorte.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p6=Process(
        name='Toda hora (50º min)',
        description='Toda hora (50º min)',
        run_if_err=True,
        minute='50',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=1
    )
    p6.save()
    t = Task(
        name='Recorte PAN',
        description='Execução dos recortes das bandas PAN cadastrados e não finalizados na tabela Recortes RGB/PAN',
        is_active=True,
        level=1,
        offset='0%',
        interpreter='python',
        arguments='--todos --pan',
        process_id=p6.id
    )
    path = Path('cbers4amanager/management/make_recorte.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p7=Process(
        name='Toda hora (55º min)',
        description='Toda hora (55º min)',
        run_if_err=True,
        minute='55',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=2
    )
    p7.save()
    t = Task(
        name='Transfer R',
        description='Tranferênica dos recortes prontos para a tabela das imagens Fusinonadas',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='',
        process_id=p7.id
    )
    path = Path('cbers4amanager/management/transfer_recorte2pansharp.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p8=Process(
        name='Toda hora (57º min)',
        description='Toda hora (57º min)',
        run_if_err=True,
        minute='57',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='0',
        chart_height=0
    )
    p8.save()
    t = Task(
        name='Fusão RGB/PAN',
        description='Executar a fusão IHS (Panshapening) das imagens cadastradas na tabela Fusão RGB/PAN',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos',
        process_id=p8.id
    )
    path = Path('cbers4amanager/management/make_pansharp.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    #####################
    p9=Process(
        name='Semanalmente (dom)',
        description='Semanalmente (dom 00:02)',
        run_if_err=True,
        minute='2',
        hour='0',
        day_of_month='*',
        month='*',
        day_of_week='0',
        chart_height=0
    )
    p9.save()
    t = Task(
        name='Remover Insumos',
        description='Exclusão dos insumos (Downloads, Composições RGB e Recortes) que originaram as fusões finalizadas. ',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='',
        process_id=p9.id
    )
    path = Path('cbers4amanager/management/rm_insumos.py')
    with path.open(mode='rb') as f:
        t.code = File(f, name=path.name)
        t.save()
    return p4.id

if __name__ == '__main__':
    main()
