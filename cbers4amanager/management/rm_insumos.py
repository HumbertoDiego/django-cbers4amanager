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

from cbers4amanager.models import Download, Pansharpened, ComposicaoRGB, INOMClippered


def main(pks):
    for i in pks:
        try:
            p = Pansharpened.objects.get(pk=i)
            download_ids_to_delete = [
                p.insumos.pancromatica.id,
                p.insumos.rgb.red.id,
                p.insumos.rgb.green.id,
                p.insumos.rgb.blue.id,
                ]
            comporgb_ids_to_delete = [
                p.insumos.rgb.id
                ]
            recorte_ids_to_delete = [
                p.insumos.id
            ]
            print("Removendo:", [
                p.insumos.recorte_rgb,
                p.insumos.recorte_pancromatica,
                p.insumos.rgb.rgb,
                p.insumos.pancromatica.arquivo,
                p.insumos.rgb.red.arquivo,
                p.insumos.rgb.green.arquivo,
                p.insumos.rgb.blue.arquivo,
            ])
            # DELETE
            Download.objects.filter(id__in=download_ids_to_delete).delete()
            ComposicaoRGB.objects.filter(id__in=comporgb_ids_to_delete).delete()
            INOMClippered.objects.filter(id__in=recorte_ids_to_delete).delete()
        except Exception as e:
            print(str(e))
            continue

if __name__ == '__main__':
    pks = [i.id for i in Pansharpened.objects.filter(finalizado=True).all()]
    main(pks)

