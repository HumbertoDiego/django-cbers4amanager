import os, sys, django, json
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Pansharpened

def main(pks):
    for i in pks:
        try:
            pan = Pansharpened.objects.get(pk=i)
        except Exception as e:
            print(e)
            continue
        if pan.finalizado: continue
        input_pan = pan.insumos.recorte_pancromatica
        input_rgb = pan.insumos.recorte_rgb
        out = os.path.join(settings.MEDIA_ROOT,'pansharp',pan.insumos.nome+"_PANSHARPENED.tif")
        comando = 'gdal_pansharpen.py "{input_pan}" "{input_rgb}" "{out}" '.format(input_pan=input_pan,input_rgb=input_rgb,out=out)
        comando += '-co COMPRESS=DEFLATE -co PHOTOMETRIC=RGB'
        print(comando)
        os.system(comando)
        pan.pansharp = out
        pan.finalizado = True
        pan.save()
        print("TERMINADO:",pan)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in Pansharpened.objects.all()]
    main(pks)

