#!/usr/bin/env python3
from email import header
import os, sys, django, time
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download, ComposicaoRGB
from django.db.models import CharField
from django.db.models.aggregates import Aggregate

class PostgreSQLGroupConcat(Aggregate):
    template = "array_to_string(array_agg(%(expressions)s), ',') "
    #template = '%(function)s(%(distinct)s %(expression)s)'
    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=CharField(), **extra)
		
def get_downloads(classe, requisicao):
    queryset = Download.objects.filter(finalizado=True)
    newqueryset = queryset.filter(nome__icontains="BAND3") | queryset.filter(nome__icontains="BAND2") | queryset.filter(nome__icontains="BAND1") 
    finalqueryset = newqueryset.values("nome_base").annotate(downloads=PostgreSQLGroupConcat('nome'))
    #print(queryset.query)
    agrupamento = []
    for object in finalqueryset.all():
        if not ComposicaoRGB.objects.filter(nome_base=object['nome_base']) and all(i in object['downloads'] for i in ["BAND3","BAND2","BAND1"]):
            bandas = {}
            for nome in object['downloads'].split(","):
                if "BAND3" in nome:
                    bandas['red']=('style=color:red',nome)
            for nome in object['downloads'].split(","):
                if "BAND2" in nome:
                    bandas['green']=('style=color:green',nome)
            for nome in object['downloads'].split(","):
                if "BAND1" in nome:
                    bandas['blue']=('style=color:blue',nome)
            agrupamento.append(bandas)
    # create Genere object from passed in data
    for bandas in agrupamento:
        red = Download.objects.get(nome=bandas['red'][1])
        green = Download.objects.get(nome=bandas['green'][1])
        blue = Download.objects.get(nome=bandas['blue'][1])
        rgb = ComposicaoRGB(red=red, green=green, blue=blue)
        rgb.nome_base = red.nome_base or green.nome_base or blue.nome_base
        print(rgb)
        rgb.save()
    print("Adicionados %s registros"%(len(agrupamento)))

if __name__ == '__main__':
	get_downloads(None,None)
	

