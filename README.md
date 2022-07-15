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
* Bibliotecas Geoespaciais para o funcionamento do GeoDjango

| Program |	Description |	Required | Supported Versions |
|---|-----|----|-------|
| GEOS |	Geometry Engine Open Source |	Yes |	3.10, 3.9, 3.8, 3.7, 3.6 |
| PROJ |	Cartographic Projections library |	Yes (PostgreSQL and SQLite only) |	8.x, 7.x, 6.x, 5.x, 4.x |
| GDAL |	Geospatial Data Abstraction Library |	Yes |	3.3, 3.2, 3.1, 3.0, 2.4, 2.3, 2.2, 2.1 |
| GeoIP |	IP-based geolocation library |	No |	2 |
| PostGIS |	Spatial extensions for PostgreSQL |	Yes (PostgreSQL only) |	3.1, 3.0, 2.5, 2.4 |
| SpatiaLite |	Spatial extensions for SQLite |	Yes (SQLite only) |	5.0, 4.3 |

## Fluxo de tabalho
