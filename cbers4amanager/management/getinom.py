import os, sys, django,csv,json
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from django.contrib.gis.geos import GEOSGeometry
from cbers4amanager.models import INOM
from django.db import IntegrityError


def main(pks):
    ascpath = os.path.join(os.getcwd(),'cbers4amanager','management','asc_25k.csv')
    with open(ascpath, newline='') as csvfile:
        features = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(features)
        for feature in features:
            #"inom","mi","geom","id","check_version","qt_produtos","check_version_op","qt_produtos_op"
            inom,mi,hex = feature[0:3]
            pol = GEOSGeometry(hex)
            f = json.loads(pol.geojson)
            if pol.geom_type=="MultiPolygon":
                f['type'] = 'Polygon'
                f['coordinates'] = f['coordinates'][0]
                pol = GEOSGeometry(str(f))
            i = INOM(inom=inom,mi=mi, bounds=pol)
            try:
                i.save()
            except IntegrityError as e:
                print(str(e))
                continue
    

if __name__ == '__main__':
    pks = sys.argv[1:]
    main(pks)

