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
        pansharpened = pan.pansharp
        if pansharpened:
            comando = 'gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL {out}'.format(out=pansharpened)
            print(comando)
            os.system(comando)
            pan.finalizado = True
            pan.save()
            print("TERMINADO:",pan)
        else:
            print("NÃO POSSUI IMAGEM PANSHARPENED:",pan)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in Pansharpened.objects.filter(finalizado=False).all()]
    main(pks)

