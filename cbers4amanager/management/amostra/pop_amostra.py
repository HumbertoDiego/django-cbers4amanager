#!/usr/bin/env python3
import os, sys, django
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Projeto, INOM, Download
from django.contrib.gis.geos import GEOSGeometry

def import_txt(classe, requisicao):
    # create Genere object from passed in data
    inpe_catalog_path = os.path.join(os.getcwd(),'cbers4amanager','static','cbers4amanager','amostra','inpe_catalog.txt')
    with open(inpe_catalog_path) as f:
        text = f.read().decode("utf-8") 
    linhas = [u.strip() for u in text.split("\n") if u]
    count = 0
    for linha in linhas:
        if ".xml" in linha: continue
        nome = linha.split("/")[-1].split("?")[0]
        nome_base = nome.split("_BAND")[0]
        tipo = "red" if "BAND3" in nome else "green" if "BAND2" in nome else "blue" if "BAND1" in nome else "pan" if "BAND0" in nome else "nir" if "BAND4" in nome else ""
        d = Download(url=linha,nome=nome,nome_base=nome_base,tipo=tipo)
        try:
            d.save()
        except IntegrityError as e:
            print(str(e))
            continue
        count+=1
    print( "Adicionados %s registros"%(str(count)))

def main():
    # Projeto
    p = Projeto(
        nome='SC-19-V-C na escala 1:50K',
        bounds=GEOSGeometry('Polygon ((-71.9999999249999405 -9.00000009399997225, -70.50000001199998678 -9.00000009399997225, -70.50000001199998678 -10.0000002029999564, -71.9999999249999405 -10.0000002029999564, -71.9999999249999405 -9.00000009399997225))',srid=4326)
        )
    p.save()
    # INOM
    inomspath = os.path.join(os.getcwd(),'cbers4amanager','static','cbers4amanager','amostra','SC-19-V-C_em_50K.csv')
    with open(inomspath, newline='') as csvfile:
        features = csv.reader(csvfile, delimiter=';', quotechar='"')
        header = next(features)
        for feature in features:
            #"wkt","inom","mi"
            wkt,inom,mi = feature[0:3]
            pol = GEOSGeometry(wkt,srid=4326)
            i = INOM(inom=inom, mi=mi, bounds=pol, projeto=p.id)
            try:
                i.save()
            except IntegrityError as e:
                print(str(e))
                continue
    # Download
    import_txt(None, None)
    return p.id

if __name__ == '__main__':
    main()
