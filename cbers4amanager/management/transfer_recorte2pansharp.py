#!/usr/bin/env python3
import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import INOMClippered, Pansharpened
		
def get_recortes(classe, requisicao):
    insumos_para_pansharp_ja_registrados = Pansharpened.objects.values('insumos').all()
    n_registrar_esses_ids = list(set([i['insumos'] for i in insumos_para_pansharp_ja_registrados]))
    queryset = INOMClippered.objects.filter(finalizado=True).exclude(id__in=n_registrar_esses_ids)
    # create Genere object from passed in data
    count = 0
    for inomclippered in queryset.all():
        p = Pansharpened(insumos=inomclippered)
        p.save()
        count +=1
    print("Adicionados %s registros"%(count))
    
if __name__ == '__main__':
	get_recortes(None,None)
	

