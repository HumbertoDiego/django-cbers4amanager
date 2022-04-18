import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import ComposicaoRGB
from django.core.files.base import ContentFile
"""
CASO ERRO: ModuleNotFoundError: No module named '_gdal_array'
pip uninstall gdal
pip install numpy
pip install gdal
"""

def main(pks):
    for i in pks:
        try:
            comprgb = ComposicaoRGB.objects.get(pk=i)
        except Exception as e:
            print(str(e))
            continue
        #if comprgb.finalizado: continue
        rgbfname = '%s'%comprgb
        out = os.path.join(settings.MEDIA_ROOT,'rgbs',rgbfname)
        red = os.path.join(settings.MEDIA_ROOT,'bandas',comprgb.red.nome)
        green = os.path.join(settings.MEDIA_ROOT,'bandas',comprgb.green.nome)
        blue = os.path.join(settings.MEDIA_ROOT,'bandas',comprgb.blue.nome)
        comando = 'gdal_merge.py -separate -n 0.0 -a_nodata 0.0 -ot Int16 -co PHOTOMETRIC=RGB -co COMPRESS=DEFLATE -o '
        comando += '{out} {red} {green} {blue}'.format(out=out,red=red,green=green,blue=blue)
        print(comando)
        os.system(comando)
        comprgb.finalizado = True
        comprgb.rgb = out
        comprgb.save()
        print("TERMINADO:",rgbfname)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in ComposicaoRGB.objects.all()]
    main(pks)
