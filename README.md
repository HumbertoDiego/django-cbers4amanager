# django-cbers4amanager
App para download, composição RGB, recorte, calcular coeficiente de nuvens e fazer pansharpen de imagens CBERS4A.

## Requisitos
* Docker: 
  * Windows:
    * Fazer o download e instalar [Start Docker Desktop](https://docs.docker.com/desktop/install/windows-install/ "Start Docker Desktop"); e
    * Fazer o download e instalar o [Windows Subsystem for Linux Kernel](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi "Windows Subsystem for Linux Kernel") (wsl2kernel)

  * Ubuntu: 
    ```
    curl -fsSL https://get.docker.com -o get-docker.sh
    DRY_RUN=1 sh ./get-docker.sh
    ```
## Instalação

```
docker-compose up -d
docker-compose exec app python manage.py makemigrations
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
docker-compose restart
```
## Fluxo de tabalho
