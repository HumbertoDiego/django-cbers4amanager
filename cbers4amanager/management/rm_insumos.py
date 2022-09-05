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
import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download, Pansharpened, ComposicaoRGB, INOMClippered

def delete_orfaos():
    dowpath = Download._meta.get_field('arquivo').path
    rgbpath = ComposicaoRGB._meta.get_field('rgb').path
    recpath = INOMClippered._meta.get_field('recorte_rgb').path
    panpath = Pansharpened._meta.get_field('pansharp').path
    for n in os.listdir( dowpath ):
        f = os.path.join(recpath,n)
        if os.path.isfile(f) and n!='.gitkeep':
            try:
                Download.objects.get(nome=n)
            except:
                try:
                    print(n)
                    os.remove(f)
                except OSError as error:
                    print(error,n)
                    continue
    for n in os.listdir( rgbpath ):
        f = os.path.join(rgbpath,n)
        if os.path.isfile(f) and n!='.gitkeep':
            try:
                ComposicaoRGB.objects.get(rgb=f)
            except:
                try:
                    print(n)
                    os.remove(f)
                except OSError as error:
                    print(error,n)
                    continue
    for n in os.listdir( recpath ):
        f = os.path.join(recpath,n)
        if os.path.isfile(f) and n!='.gitkeep':
            if "RGB" in n:
                try:
                    INOMClippered.objects.get(recorte_rgb=f)
                except:
                    try:
                        print(n)
                        os.remove(f)
                    except OSError as error:
                        print(error,n)
                        continue
            else:
                try:
                    INOMClippered.objects.get(recorte_pancromatica=f)
                except:
                    try:
                        print(n)
                        os.remove(f)
                    except OSError as error:
                        print(error,n)
                        continue
    for n in os.listdir( panpath ):
        f = os.path.join(panpath,n)
        if os.path.isfile(f) and n!='.gitkeep':
            try:
                Pansharpened.objects.get(pansharp=f)
            except:
                try:
                    print(n)
                    os.remove(f)
                except OSError as error:
                    print(error,n)
                    continue
def delete_parents(pks):
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

def main(pks):
    delete_parents(pks)
    delete_orfaos()

if __name__ == '__main__':
    pks = [i.id for i in Pansharpened.objects.filter(finalizado=True).all()]
    main(pks)

