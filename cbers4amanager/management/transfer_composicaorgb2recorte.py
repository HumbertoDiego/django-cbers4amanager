#!/usr/bin/env python3
from email import header
import os, sys, django, time
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import GEOSGeometry

from cbers4amanager.models import INOMClippered, ComposicaoRGB, INOM
		
def getIntersection(comprgb):
        #print(comprgb)
        rst = GDALRaster(comprgb.rgb, write=False)
        xmin, ymin, xmax, ymax = rst.extent
        pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        poly = GEOSGeometry(pol,srid=rst.srid)
        queryset = INOM.objects.filter(bounds__intersects=poly)
        return queryset

def get_composicao(classe, requisicao):
    rgbs_ja_registrados_para_recorte = INOMClippered.objects.values('rgb').all()
    n_registrar_esses_ids = list(set([i['rgb'] for i in rgbs_ja_registrados_para_recorte]))
    queryset = ComposicaoRGB.objects.filter(finalizado=True).exclude(id__in=n_registrar_esses_ids)
    # create Genere object from passed in data
    count = 0
    for comprgb in queryset.all():
        try:
            inoms = getIntersection(comprgb)
        except:
            continue
        print(inoms)
        for inom in inoms.all():
            if not INOMClippered.objects.filter(nome=comprgb.nome_base+"_"+inom.inom):
                i = INOMClippered(nome=comprgb.nome_base+"_"+inom.inom,inom=inom,rgb=comprgb)
                try:
                    i.pancromatica = Download.objects.filter(finalizado=True).get(nome_base__iexact=comprgb.nome_base,tipo='pan')
                except:
                    pass
                i.save()
                count+=1
    print("Adicionados %s registros"%(count))
    
    

if __name__ == '__main__':
	get_composicao(None,None)
	

