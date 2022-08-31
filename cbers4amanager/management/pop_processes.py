#!/usr/bin/env python3
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
    sql = "TRUNCATE pr_processes CASCADE;TRUNCATE pr_tasks CASCADE;"
    with connection.cursor() as cursor:
        cursor.execute(sql)
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
    p2=Process(
        name='Toda hora (1º min)',
        description='Toda hora (1º min)',
        run_if_err=True,
        minute='1',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=0
    )
    p2.save()
    p3=Process(
        name='Toda hora (5º min)',
        description='Toda hora (5º min)',
        run_if_err=True,
        minute='5',
        hour='*',
        day_of_month='*',
        month='*',
        day_of_week='*',
        chart_height=0
    )
    p3.save()
    t1 = Task(
        name='Download',
        description='Execução de todos os downloads em ordem, um a um,',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos',
        process_id=p1.id
    )
    path = Path('cbers4amanager/management/download_cbers4a.py')
    with path.open(mode='rb') as f:
        t1.code = File(f, name=path.name)
        t1.save()
    t2 = Task(
        name='Transfer D',
        description='Tranferênica dos downloads com todas as bandas finalizadas para a tabela Composição RGB',
        is_active=True,
        level=0,
        offset='0%',
        interpreter='python',
        arguments='--todos',
        process_id=p2.id
    )
    path = Path('cbers4amanager/management/transfer_download2composicaorgb.py')
    with path.open(mode='rb') as f:
        t2.code = File(f, name=path.name)
        t2.save()

if __name__ == '__main__':
    main()
