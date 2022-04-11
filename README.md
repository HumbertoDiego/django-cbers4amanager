# django-cbers4amanager
App para download, composição RGB, recorte, calcular coeficiente de nuvens e fazer pansharpen de imagens CBERS4A.

## Requisitos
* PostgreSQL: 
  * apt install postgresql postgis
  * su postgresl
  * psql
  * postgres=# \password -- Alterar o arquivo setting.py com esta senha
  * postgres=# CREATE DATABASE cbers4a;
  * postgres=# \c cbers4a
  * cbers4a=# CREATE EXTENSION postgis; 
  * cbers4a=# CREATE EXTENSION postgis_raster;
  * cbers4a=# CREATE EXTENSION postgis_sfcgal; 
* Django
  * sudo apt install python3-django
  * Editar settings.py
  > INSTALLED_APPS = [
  > 'cbers4amanager.apps.Cbers4AmanagerConfig',
  > 'django.contrib.gis',
  >  ...
  > ]


  > DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cbers4a',
        'USER': 'postgres',
        'PASSWORD': '4cgeosdt',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
  

