import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import ComposicaoRGB
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import GDALRaster
"""
CASO ERRO: ModuleNotFoundError: No module named '_gdal_array'
pip uninstall gdal
pip install numpy
pip install gdal
"""

def set_bounds(comprgb):
    rst = GDALRaster(comprgb.rgb, write=False)
    xmin, ymin, xmax, ymax = rst.extent
    pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
    print(pol)
    poly = GEOSGeometry(pol,srid=rst.srid)
    comprgb.bounds = poly
    comprgb.save()


def main(pks):
    for i in pks:
        try:
            comprgb = ComposicaoRGB.objects.get(pk=i)
        except Exception as e:
            print(str(e))
            continue
        if comprgb.finalizado: continue
        rgbfname = '%s'%comprgb
        out = os.path.join(settings.MEDIA_ROOT,'a','rgbs',rgbfname)
        red = os.path.join(settings.MEDIA_ROOT,'a','bandas',comprgb.red.nome)
        green = os.path.join(settings.MEDIA_ROOT,'a','bandas',comprgb.green.nome)
        blue = os.path.join(settings.MEDIA_ROOT,'a','bandas',comprgb.blue.nome)
        comando = 'gdal_merge'
        comando += '.bat' if os.name=='nt' else '.py'
        comando += ' -separate -n 0.0 -a_nodata 0.0 -ot Int16 -co PHOTOMETRIC=RGB -co COMPRESS=DEFLATE -o '
        comando += '{out} {red} {green} {blue}'.format(out=out,red=red,green=green,blue=blue)
        print(comando)
        os.system(comando)
        comprgb.finalizado = True
        comprgb.rgb = out
        comprgb.save()
        set_bounds(comprgb)
        print("TERMINADO:",rgbfname)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in ComposicaoRGB.objects.all()]
    main(pks)

