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

from cbers4amanager.models import INOMClippered

def getAreaUtil(fname):
    comando = 'gdalinfo %s -stats -json'%(fname)
    print(comando)
    json_str = os.popen(comando).read()
    dic = json.loads(json_str)
    statistics_valid_percent = round(min([float(i['metadata']['']['STATISTICS_VALID_PERCENT']) for i in dic['bands']]),2)
    try:
        maximos = [int(i['metadata']['']['STATISTICS_MAXIMUM']) for i in dic['bands']]
    except KeyError:
        maximos = []
    print(statistics_valid_percent)
    return statistics_valid_percent, maximos

def getNuvens(fname,m):
    file_name, file_extension = os.path.splitext(os.path.basename(fname))
    new_file_name = file_name+"_NUVENS"+file_extension
    out = os.path.join(settings.MEDIA_ROOT,'a','nuvens',new_file_name)
    mred,mgreen,mblue = m[0:3]
    # Caso erro ValueError: not enough values to unpack (expected 3, got 2) 
    f = 0.5
    fdelta= 0.0005
    comando = 'gdal_calc'
    comando += '.bat' if os.name=='nt' else '.py'
    comando += " -A {fname} --A_band=1 -B {fname} --B_band=2 -C {fname} --C_band=3 "
    #TODO: melhorar o algoritmo
    comando += '--calc="(A>{r})*(B>{g})*(C>{b})" --co NBITS=1 --type Byte '
    #comando += "--calc='A+B+C>{soma}' "         
    comando += " --outfile {out} --overwrite --quiet --NoDataValue 0"
    comando = comando.format(fname=fname,r=f*mred,g=f*mgreen,b=f*mblue,soma=f*sum(m),delta=fdelta*sum(m),out=out)
    print(comando)
    os.system(comando)
    return out

def main(pks,final_do_nome):
    for i in pks:
        try:
            rec = INOMClippered.objects.get(pk=i)
        except Exception as e:
            print(e)
            continue
        if rec.finalizado: continue
        if rec.finalizado==None: continue
        if "PAN" in final_do_nome and not rec.pancromatica: continue
        out = os.path.join(settings.MEDIA_ROOT,'a','recortes',rec.nome+final_do_nome)
        clipper = rec.inom.bounds
        try:
            clipee = rec.rgb.rgb if "RGB" in final_do_nome else rec.pancromatica.arquivo
        except Exception as e:
            print(e)
            continue
        xmin, ymin, xmax, ymax = clipper.extent
        comando = 'gdal_translate -a_nodata 0.0 -projwin '#<ulx> <uly> <lrx> <lry>
        comando += '%s %s %s %s -projwin_srs EPSG:%s -of GTiff '%(xmin,ymax,xmax,ymin,clipper.srid)
        comando += '%s %s'%(clipee,out)
        print(comando)
        # TODO: Dar um jeito de descobrir se deu erro no comando GDAL
        try:
            os.system(comando)
        except Exception as e:
            print("ERRO GDAL, PULANDO.",str(e))
            if not os.path.isfile(out):
                print("No such file or directory:",out)
            continue
        if "RGB" in final_do_nome:
            # TODO: Ver  se o recorte deu certo
            rec.recorte_rgb = out
        else: 
            rec.recorte_pancromatica = out
        rec.save()
        # Obter a área útil se for recorte RGB
        if "RGB" in final_do_nome:
            rec.area_util , maximos = getAreaUtil(out)
            rec.save()
            # Obter a área útil da classificação das nuvens do recorte RGB
            if maximos and len(maximos)==3:
                out = getNuvens(out,maximos)
                area_util , maximos = getAreaUtil(out)
            else:
                area_util = None
            rec.cobertura_nuvens = area_util
            rec.save()
        l = settings.CBERS4AMANAGER['LIMITS']
        if rec.rgb and rec.pancromatica and rec.recorte_rgb and rec.recorte_pancromatica:
            if rec.area_util>float(l['min_area_com_dados_percent']) and rec.cobertura_nuvens<float(l['max_area_nuvens_percent']) :
                rec.finalizado = True
                rec.save()
            else:
                rec.finalizado = None
                rec.save()
        print("TERMINADO:",rec)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        if '--pan' in pks:
            ids = [i.id for i in INOMClippered.objects.all()]
            main(ids,'_PAN.tif')
        if '--rgb' in pks:
            ids = [i.id for i in INOMClippered.objects.all()]
            main(ids,'_RGB.tif')
    else:
        if '--pan' in pks:
            pks.remove('--pan')
            main(pks,'_PAN.tif')
        elif '--rgb' in pks:
            pks.remove('--rgb')
            main(pks,'_RGB.tif')

