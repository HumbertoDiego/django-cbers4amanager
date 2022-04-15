from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import INOM, Download, ComposicaoRGB, INOMClippered, Pansharpened
from django.shortcuts import redirect, render
from django import forms
from django.urls import path
import json
from django.contrib.gis.geos import GEOSGeometry
from django.db import IntegrityError
from django.contrib import messages
from process.models import Process, Job, Task
import os
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import CharField
from django.contrib.gis.gdal import GDALRaster
################ INOM ##################
class JsonImportForm(forms.Form):
    file = forms.FileField()

class MyOSMGeoAdminv2(OSMGeoAdmin):
    actions = []
    change_list_template = "cbers4amanager/inom_changelist.html"
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-geojson/', self.import_geojson),
        ]
        return my_urls + urls
    def import_geojson(self, request):
        if request.method == "POST":
            # create Genere object from passed in data
            geojson = request.FILES["file"]
            datastring = geojson.read().decode("utf-8") 
            data = json.loads(datastring)
            features = data['features']
            crs = data['crs']['properties']['name']
            count = 0
            for feature in features:
                inom = feature['properties'].get('inom','')
                if not inom:
                    print("Feição sem a coluna inom! pulando.")
                    continue
                pol = GEOSGeometry(str(feature['geometry']))
                if pol.geom_type=="MultiPolygon":
                    feature['geometry']['type'] = 'Polygon'
                    feature['geometry']['coordinates'] = feature['geometry']['coordinates'][0]
                    pol = GEOSGeometry(str(feature['geometry']))
                elif pol.geom_type!="Polygon":
                    print("Geometria %s diferente de Poligonos! pulando %s."%(pol.geom_type,inom))
                    continue
                i = INOM(inom=inom, bounds=pol)
                try:
                    i.save()
                except IntegrityError as e:
                    print(e.message)
                    continue
                count+=1
            self.message_user(request, "Adicionados %s registros"%(str(count)))
            return redirect("..")
        form = JsonImportForm()
        payload = {"form": form}
        return render(
            request, "admin/upload_form.html", payload
        )
admin.site.register(INOM,MyOSMGeoAdminv2)

################ Download ##################
@admin.action(description='Update finalizado=True das linhas selecionadas')
def set_finalizado(modeladmin, request, queryset):
    queryset.update(finalizado=True)

@admin.action(description='Update finalizado=False das linhas selecionadas')
def set_nao_finalizado(modeladmin, request, queryset):
    queryset.update(finalizado=False)

@admin.action(description='Update name, base_name e tipo de acordo com a url')
def set_names(modeladmin, request, queryset):
    for e in queryset:
        linha = e.url
        e.nome = linha.split("/")[-1].split("?")[0]
        e.nome_base = e.nome.split("_BAND")[0]
        e.tipo = "red" if "BAND3" in e.nome else "green" if "BAND2" in e.nome else "blue" if "BAND1" in e.nome else "pan" if "BAND0" in e.nome else "" 
        e.save()

@admin.action(description='Update limites (após download)')
def set_bounds(modeladmin, request, queryset):
    for e in queryset:
        fpath=os.path.join(os.getcwd(),'uploads/bandas',e.nome)
        rst = GDALRaster(fpath, write=False)
        xmin, ymin, xmax, ymax = rst.extent
        pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        print(pol)
        poly = GEOSGeometry(pol,srid=rst.srid)
        e.bounds = poly
        e.save()



class CsvImportForm(forms.Form):
    file = forms.FileField()
class TextForm(forms.Form):
    caminho = forms.CharField()

class MyOSMGeoAdmin(OSMGeoAdmin):
    actions = [set_finalizado,set_nao_finalizado,set_names,'comecar_download',set_bounds]
    list_display = ('nome', 'tipo', 'iniciado_em','_content_length','progresso','terminado_em','finalizado')
    search_fields = ['nome', 'tipo' ]
    change_list_template = "cbers4amanager/download_changelist.html"
    #fields = ('nome','tipo','content_length')
    def _content_length(self, obj):
        if not obj.content_length:
            retorno = "-"
        elif obj.content_length<=1000:
            retorno = str(obj.content_length)+" B"
        elif 1000< obj.content_length<=1000000 :
            retorno = "{:.2f}".format(obj.content_length/1000.0)+" Kb"
        elif 1000000< obj.content_length<=1000000000 :
            retorno = "{:.2f}".format(obj.content_length/1000000.0)+" Mb"
        else:
            retorno = "{:.2f}".format(obj.content_length/1000000000.0)+" Gb"
        return retorno
    @admin.action(description='Começar Download')
    def comecar_download(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            aux = [str(q.pk) for q in queryset]
            # TODO: Proteger aqui
            try:
                process = Process.objects.get(name="Download")
            except:
                process = Process(name="Download",description="Todo minuto",run_if_err=True,
                                minute="*",hour="*",day_of_month="*",month="*",day_of_week="*")
                process.save()
            # DONE: Verificar se o id já está em description de um Task ativo
            ids = []
            for i in range(len(aux)):
                try:
                    q = Task.objects.get(description__contains="'"+aux[i]+"'")
                    # Existe ativo, então não cria outro
                except Task.DoesNotExist as e:
                    # Não existe ativo, então cria outro
                    ids.append(aux[i])
                    continue
            last = Task.objects.order_by('-id').first()
            next_id = last.id + 1 if last else 1
            t = Task(process=process,name="Download "+str(next_id), description= "Download dos itens: %s"%(ids),
                    interpreter= os.popen('which python3').read().replace('\n',''),
                    arguments = " ".join(ids))
            path = os.path.join(os.getcwd(),'cbers4amanager/management/download_cbers4a.py')
            with open(path, "rb") as py:
                t.code= ContentFile(py.read(), name=os.path.basename(path))
            try:
                t.save()
                self.message_user(request,
                                    "Download de %s iniciado."%(ids), 
                                    messages.SUCCESS)
            except IntegrityError as e:
                self.message_user(request,
                                    "Processo já existe. Reiniciando...", 
                                    messages.WARNING)
                pass
            job, tasks = Job.create(process)
        else:
            request.current_app = self.admin_site.name
            context = {
                'action':request.POST.get("action"),
                'queryset':queryset,
                'opts': self.model._meta,
                'tarefa': "DOWNLOAD"
            } 
            return render(request, "admin/download_confirmation.html", context)
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-txt/', self.import_txt),
            path('import-tiffs-de-pasta-local/', self.import_tiffs_de_pasta_local),
        ]
        return my_urls + urls
    def import_txt(self, request):
        if request.method == "POST":
            # create Genere object from passed in data
            txt = request.FILES["file"]
            text = txt.read().decode("utf-8") 
            linhas = [u for u in text.split("\n") if u]
            count = 0
            for linha in linhas:
                if ".xml" in linha: continue
                nome = linha.split("/")[-1].split("?")[0]
                nome_base = nome.split("_BAND")[0]
                tipo = "red" if "BAND3" in nome else "green" if "BAND2" in nome else "blue" if "BAND1" in nome else "pan" if "BAND0" in nome else ""
                d = Download(url=linha,nome=nome,nome_base=nome_base,tipo=tipo)
                try:
                    d.save()
                except IntegrityError as e:
                    print(str(e))
                    continue
                count+=1
            self.message_user(request, "Adicionados %s registros"%(str(count)))
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form,'opts': self.model._meta,}
        return render(
            request, "admin/upload_form.html", payload
        )
    def import_tiffs_de_pasta_local(self, request):
        if request.method == "POST":
            # create Genere object from passed in data
            caminho = request.POST["caminho"]
            onlytifsfiles = [f for f in os.listdir(caminho) if os.path.isfile(os.path.join(caminho, f)) and f.split(".")[-1] in ["tif","TIF","tiff","TIFF"]] 
            a,m = 0,0
            # 1) Encontrar se já existe a intenção de download desse arquivo com mesmo nome
            for f in onlytifsfiles:
                fullfname = os.path.join(caminho,f)
                print("IMPORTANDO:",f)
                try:
                    d = Download.objects.get(nome__contains=f)
                    if d.finalizado: continue
                    with open(fullfname, "wb") as tif:
                        d.arquivo= ContentFile(tif, name=f)
                    d.finalizado=True
                    d.progresso="100 %"
                    d.save()
                    m+=1
                except:
                    nome_base = f.split("_BAND")[0]
                    tipo = "red" if "BAND3" in f else "green" if "BAND2" in f else "blue" if "BAND1" in f else "pan" if "BAND0" in f else ""
                    d = Download(url=fullfname,nome=f,nome_base=nome_base,tipo=tipo,finalizado=True,progresso="100 %",terminado_em = timezone.now())
                    with open(fullfname, "rb") as tif:
                        d.arquivo= ContentFile(tif.read(), name=f)
                        tif.seek(0,2)
                        size = tif.tell()
                        if not size: 
                            print("PULANDO:",f)
                            continue
                        d.content_length = size
                    try:
                        d.save()
                        a+=1
                    except Exception as e:
                        print(str(e))
                        continue

            self.message_user(request,
             "Adicionados/Modificados/Encontrados (%s/%s/%s) registros de arquivos .tifs em %s"%(a,m,len(onlytifsfiles),caminho))
            return redirect("..")
        form = TextForm()
        payload = {"form": form,'opts': self.model._meta,}
        return render(
            request, "admin/pasta_local_tiffs_form.html", payload
        )

admin.site.register(Download,MyOSMGeoAdmin)


################ ComposicaoRGB ##################

from django.db.models.aggregates import Aggregate

class PostgreSQLGroupConcat(Aggregate):
    template = "array_to_string(array_agg(%(expressions)s), ',') "
    #template = '%(function)s(%(distinct)s %(expression)s)'
    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=CharField(), **extra)

class MyComposicaoRGBadmin(admin.ModelAdmin):
    search_fields = ['rgb']
    change_list_template = "cbers4amanager/composicaorgb_changelist.html"
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('get-downloads/', self.get_downloads),
        ]
        return my_urls + urls
    def get_downloads(self, request):
        queryset = Download.objects.filter(finalizado=True).values("nome_base").annotate(downloads=PostgreSQLGroupConcat('nome'))
        #print(queryset.query)
        agrupamento = {}
        for object in queryset.all():
            object.downloads.split(",")
        if request.method == "POST":
            # create Genere object from passed in data
            
            self.message_user(request, "Adicionados %s"%(str(request.POST)))
            return redirect("..")
        form = CsvImportForm()
        payload = {'queryset':queryset,'opts': self.model._meta,}
        return render(
            request, "admin/get_downloads_form.html", payload
        )



admin.site.register(ComposicaoRGB,MyComposicaoRGBadmin)

admin.site.register(INOMClippered)
admin.site.register(Pansharpened)

