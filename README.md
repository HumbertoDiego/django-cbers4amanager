# CBERS4AManager
App para download, composição RGB, recorte, calcular coeficiente de nuvens e fazer pansharpen de imagens CBERS4A.

## Requisitos
* Docker: 
  * Windows:
    * Fazer o download e instalar [Start Docker Desktop](https://docs.docker.com/desktop/install/windows-install/ "Start Docker Desktop"); e
    * Fazer o download e instalar o [Windows Subsystem for Linux Kernel](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi "Windows Subsystem for Linux Kernel") (wsl2kernel)

  * Debian/Ubuntu: 
    ```
    curl -fsSL https://get.docker.com -o get-docker.sh
    DRY_RUN=1 sh ./get-docker.sh
    apt install docker-compose
    ```
## Instalação

```
git init
git pull https://github.com/HumbertoDiego/django-cbers4amanager
docker-compose up -d
docker-compose exec app python manage.py makemigrations
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
docker-compose restart
```
## Fluxo de tabalho

1. Navegar para a página `http://<IP>:81/admin`, realizar o LOGIN com as credenciais de superusuário criadas.


## Administração manual

### Deletar conjunto de arquivos obsoletos usados como insumos (bandas, composição RGB/NDVI e recortes)

Após a confecção final da imagem fusionada com resolução espacial de 2m, ou ainda, após a conclusão de que a fusão seria inviável por excesso de nuvens, os insumos podem ser deletados para fins de poupar espaço em disco. Para fazer isso, é necessario verificar o banco em `postgres://<IP>:5432` e coletar o ID e as tabelas dos arquivos.

1. Abrir o [QGIS](https://www.qgis.org) --> Janela navegador --> PostgreSQL --> New Connection...
   1. Nome: `<qualquer>`
   1. Host: `ip a | grep inet # =<IP>, escolher o IP do adaptador ligado a rede (geralmente eth0)`
   1. Banco de Dados : `docker-compose exec app python -c "import os;print(os.environ['POST_DB'])"`
   1. Autenticação: 
      1. Usuário: `docker-compose exec app python -c "import os;print(os.environ['POST_USER'])"`
      1. Senha: `docker-compose exec app python -c "import os;print(os.environ['POST_PASSWORD'])"`
2. Verificação dos dados
