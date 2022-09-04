"""
-62.2435582072567826,4.1762312603723757 : -61.9280513942536999,4.3214343936291044

1ª Opção
gdal_translate -projwin 583937.7520195323 477741.281275324 618973.348692482 461647.5944654071 -of GTiff INPUT.tif OUTPUT.tif

2ª Opção
gdalwarp -overwrite -of GTiff -cutline AOI.geojson -cl AOI -crop_to_cutline INPUT.tif OUTPUT.tif

3ª Opção
RASTER.objects.raw('SELECT ST_Clip(rast, inom,1) from inom_clippereds.rgb
WHERE rid = 171;'):
"""
import os, sys, django, json
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download


def main(pks,final_do_nome):
    for i in pks:
        try:
            d = Download.objects.get(pk=i)
        except Exception as e:
            print(e)
            continue    

if __name__ == '__main__':
    pks = sys.argv[1:]
    #if "--todos" in pks:
    #    pks = [i.id for i in Download.objects.all()]
    main(pks)

