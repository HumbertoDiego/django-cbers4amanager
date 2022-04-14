# django-cbers4amanager
App para download, composição RGB, recorte, calcular coeficiente de nuvens e fazer pansharpen de imagens CBERS4A.

## Requisitos
* PostgreSQL: 
  * apt install postgresql postgis
  * su USERNAME_POST # Alterar o arquivo settings.py com este username
  * psql
  * postgres=# \password -- Alterar o arquivo settings.py com esta senha -> PASSWORD_POST
  * postgres=# CREATE DATABASE cbers4a;
  * postgres=# \c cbers4a
  * cbers4a=# CREATE EXTENSION postgis; 
  * cbers4a=# CREATE EXTENSION postgis_raster;
  * cbers4a=# CREATE EXTENSION postgis_sfcgal; 
* Django
  * sudo apt install python3-django

## Fluxo de tabalho
