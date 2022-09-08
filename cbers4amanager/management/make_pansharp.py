import os, sys, django, json
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Pansharpened
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import fromfile

from osgeo import ogr
from osgeo import osr

def set_bounds(pan):
    # 1 etapa raster binário
    file_name, file_extension = os.path.splitext(os.path.basename(pan.pansharp))
    new_file_name = file_name+"_DATA"+file_extension
    out = os.path.join(settings.MEDIA_ROOT,'a','nuvens',new_file_name)
    comando = 'gdal_calc'
    comando += '.bat' if os.name=='nt' else '.py'
    comando += " -A {fname} --A_band=1 "
    comando += '--calc="(A>0)" --co NBITS=1 --type Byte '
    comando += " --outfile {out} --overwrite --quiet --NoDataValue 0"
    comando = comando.format(fname=pan.pansharp,out=out)
    print(comando)
    os.system(comando)

    # 2 etapa poligonizar o raster binário
    new_file_name2 = file_name+"_DATA.gpkg"
    out2 = os.path.join(settings.MEDIA_ROOT,'a','nuvens',new_file_name2)
    comando = 'gdal_polygonize'
    comando += '.bat' if os.name=='nt' else '.py'
    comando += ' {fname} -b 1 -f "GPKG" {out} OUTPUT DN'
    comando = comando.format(fname=out,out=out2)
    print(comando)
    os.system(comando)

    # 3 Open file
    shp = ogr.Open(out2,0)
    lyr = shp.GetLayerByName( "OUTPUT" )

    # 4 Transformation params
    crs = lyr.GetSpatialRef()
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    transform = osr.CoordinateTransformation(crs, target)
    #epsg = crs.GetAttrValue("AUTHORITY", 1)

    # 5. Get best ring
    for feat in lyr:
        geom = feat.GetGeometryRef()
        max_area_ring = None
        max_area = 0
        for i in range(geom.GetGeometryCount()):
            ring = geom.GetGeometryRef(i)
            if max_area<ring.GetArea():
                max_area = ring.GetArea()
                max_area_ring = ring
    
    # 6. Tranform - JUMPER of a BUG
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(max_area_ring)#geom.Buffer(2.0))
    poly.Transform(transform)

    # 7. Save
    p = GEOSGeometry(poly.ExportToWkt(),srid="4326")
    pan.bounds = p
    pan.save()
    os.remove(out)
    os.remove(out2)
    print("Geometria adicionada:",pan)

def main(pks):
    for i in pks:
        try:
            pan = Pansharpened.objects.get(pk=i)
        except Exception as e:
            print(e)
            continue
        if pan.finalizado: continue
        if pan.pansharp:
            if os.path.isfile(pan.pansharp):
                continue
        input_pan = pan.insumos.recorte_pancromatica
        if not os.path.isfile(input_pan):
            print("No such file or directory:",input_pan)
            pan.insumos.recorte_pancromatica = None
            pan.insumos.finalizado = False
            pan.insumos.save()
            continue
        input_rgb = pan.insumos.recorte_rgb
        if not os.path.isfile(input_rgb):
            print("No such file or directory:",input_rgb)
            pan.insumos.recorte_rgb = None
            pan.insumos.finalizado = False
            pan.insumos.save()
            continue
        out = os.path.join(settings.MEDIA_ROOT,'a','pansharp',pan.insumos.nome+"_PANSHARPENED.tif")
        comando = 'gdal_pansharpen'
        comando += '.bat' if os.name=='nt' else '.py'
        comando += ' "{input_pan}" "{input_rgb}" "{out}" '.format(input_pan=input_pan,input_rgb=input_rgb,out=out)
        comando += '-co COMPRESS=DEFLATE -co PHOTOMETRIC=RGB'
        print(comando)
        os.system(comando)
        if not os.path.isfile(out):
            print("No such file or directory:",out)
            continue
        pan.pansharp = out
        pan.save()
        print("TERMINADO:",pan)
        set_bounds(pan)

if __name__ == '__main__':
    pks = sys.argv[1:]
    if "--todos" in pks:
        pks = [i.id for i in Pansharpened.objects.all()]
    main(pks)

