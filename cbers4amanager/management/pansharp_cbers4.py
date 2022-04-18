import os, sys, django, json
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import INOMClippered, Pansharpened

def main(pks):
    for i in pks:
        try:
            rec = INOMClippered.objects.get(pk=i)
        except Exception as e:
            print(e)
            continue
        if rec.finalizado: continue
        out = os.path.join(settings.MEDIA_ROOT,'recortes',rec.nome+final_do_nome)
        clipper = rec.inom.bounds
        # Tenho que converter a area de recorte par aomesmo src do recortado
        try:
            clipee = rec.rgb.rgb if "RGB" in final_do_nome else rec.pancromatica.arquivo.path
        except Exception as e:
            print(e)
            continue
        comando = 'gdal_translate -a_nodata 0.0 -projwin '#<ulx> <uly> <lrx> <lry>
        comando += '%s %s %s %s -projwin_srs EPSG:%s -of GTiff '%(xmin,ymax,xmax,ymin,clipper.srid)
        comando += '%s %s'%(clipee,out)
        print(comando)
        #os.system(comando)
        print("TERMINADO:",rec)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in Pansharpened.objects.all()]
    main(pks)

