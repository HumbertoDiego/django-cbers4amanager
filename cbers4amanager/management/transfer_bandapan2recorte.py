#!/usr/bin/env python3
from email import header
import os, sys, django, time
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import GEOSGeometry

from cbers4amanager.models import INOMClippered, ComposicaoRGB, INOM, Download
		
def getIntersection(pan):
        #print(comprgb)
        rst = GDALRaster(pan.arquivo, write=False)
        xmin, ymin, xmax, ymax = rst.extent
        pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        poly = GEOSGeometry(pol,srid=rst.srid)
        queryset = INOM.objects.filter(bounds__intersects=poly)
        return queryset

def get_composicao(classe, requisicao):
    msg=""
    pans_cujo_ao_menos_rgb_ja_registrado_para_recorte = INOMClippered.objects.values('pancromatica').all()
    n_registrar_esses_ids = list(set([i['pancromatica'] for i in pans_cujo_ao_menos_rgb_ja_registrado_para_recorte if i['pancromatica'] ]))
    queryset = Download.objects.filter(finalizado=True,tipo='pan').exclude(id__in=n_registrar_esses_ids)
    # create Genere object from passed in data
    count = 0
    for pan in queryset.all():
        try:
            inoms = getIntersection(pan)
        except Exception as e:
            print(str(e))
            continue
        print(inoms)
        if not inoms: 
            msg += ": Sem interseção com áreas de interesse."
            continue
        for inom in inoms.all():
            # já tem que ter no min uma RGB cadastrada pra encontrar:
            i = INOMClippered.objects.get(nome=pan.nome_base+"_"+inom.inom)
            if i:
                try:
                    i.pancromatica = pan
                    i.save()
                    count+=1
                except Exception as e:
                    print(str(e))
                    pass
    print("Adicionados %s registros%s"%(count,msg))

if __name__ == '__main__':
	get_composicao(None,None)
	

