from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.admin import GISModelAdmin
from django.http import HttpResponse, HttpResponseNotFound
from .models import Projeto, INOM, Download, ComposicaoRGB, INOMClippered, Pansharpened
from django.shortcuts import redirect, render
from django import forms
from django.urls import path, re_path, reverse
import json
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import GDALRaster
from django.db import IntegrityError
from django.contrib import messages
from process.models import Process, Job, Task, JobTask
import os
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import CharField
from django.db.models.aggregates import Aggregate
from django.utils.html import mark_safe

class MySelectWithDownloadWidget(forms.widgets.Select):
    template_name = 'django/forms/widgets/select.html'
    option_template_name = 'django/forms/widgets/select_option.html'
    # TODO
############### PROJETO ###############
class MyProjetoAdmin(GISModelAdmin):
    search_fields = ['nome']
    list_display = ('nome','_aoi_associadas' )
    @admin.display()
    def _aoi_associadas(self,obj):
        manys = INOM.objects.select_related().filter(projeto_id=obj.id) # Rápido
        #manys = INOM.objects.filter(projeto_id=obj.id) # Lento
        return manys.count()
admin.site.register(Projeto,MyProjetoAdmin)



################ INOM ##################
class JsonImportForm(forms.Form):
    file = forms.FileField()

class MyInomAdmin(OSMGeoAdmin):
    actions = []
    list_display = ('inom', 'mi','projeto','melhor_imagem')
    change_list_template = "cbers4amanager/inom_changelist.html"
    search_fields = ['inom' ]
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
                mi = feature['properties'].get('mi','')
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
                i = INOM(inom=inom, mi=mi, bounds=pol)
                try:
                    i.save()
                except IntegrityError as e:
                    print(str(e))
                    continue
                count+=1
            self.message_user(request, "Adicionados %s registros"%(str(count)))
            return redirect("..")
        form = JsonImportForm()
        payload = {"form": form,'opts': self.model._meta,}
        return render(
            request, "admin/upload_form.html", payload
        )
admin.site.register(INOM,MyInomAdmin)

################ Download ##################
@admin.action(description='Update finalizado=True das linhas selecionadas')
def set_finalizado(modeladmin, request, queryset):
    queryset.update(finalizado=True)

@admin.action(description='Update finalizado=False das linhas selecionadas')
def set_nao_finalizado(modeladmin, request, queryset):
    queryset.update(finalizado=False,iniciado_em=None,terminado_em=None,progresso=None,arquivo=None)

@admin.action(description='Update name, base_name e tipo de acordo com a url')
def set_names(modeladmin, request, queryset):
    for e in queryset:
        linha = e.url
        e.nome = linha.split("/")[-1].split("?")[0]
        e.nome_base = e.nome.split("_BAND")[0]
        e.tipo = "red" if "BAND3" in e.nome else "green" if "BAND2" in e.nome else "blue" if "BAND1" in e.nome else "pan" if "BAND0" in e.nome else "nir" if "BAND4" in e.nome else "" 
        e.save()

@admin.action(description='Update limites (após download)')
def set_bounds(modeladmin, request, queryset):
    for e in queryset:
        rst = GDALRaster(e.arquivo, write=False)
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
def int2size(content_length):
    if not content_length:
        retorno = "-"
    elif content_length<=1000:
        retorno = str(content_length)+" B"
    elif 1000< content_length<=1000000 :
        retorno = "{:.2f}".format(content_length/1000.0)+" KB"
    elif 1000000< content_length<=1000000000 :
        retorno = "{:.2f}".format(content_length/1000000.0)+" MB"
    else:
        retorno = "{:.2f}".format(content_length/1000000000.0)+" GB"
    return retorno
class MyDownloadAdmin(OSMGeoAdmin):
    actions = [set_finalizado,set_nao_finalizado,set_names,'priorizar_download',set_bounds]
    list_display = ('_nome', 'tipo', 'iniciado_em','_content_length','_progresso','finalizado')
    search_fields = ['nome', 'tipo' ]
    list_filter = ('finalizado', 'tipo')
    change_list_template = "cbers4amanager/download_changelist.html"
    @admin.display(ordering='nome')
    def _nome(self, obj):
        return obj.nome.replace("_"," ")
    @admin.display(ordering='content_length')
    def _content_length(self, obj):
        return int2size(obj.content_length)
    @admin.display(ordering='progresso')   
    def _progresso(self, obj):
        if obj.progresso!=obj.content_length and obj.progresso:
            h = """<span id="%s">%s</span>"""%(str(obj.id)+"_progresso",int2size(obj.progresso))
            s = """<script>
            function %s() {
                var ob = document.getElementById("%s");
                ob.parentElement.parentElement.classList.remove("blink-one");
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = () => {
                    if (xhr.readyState === 4) {
                        console.log(xhr.response);
                        if (ob.textContent != xhr.response){
                            ob.textContent = xhr.response;
                            ob.parentElement.parentElement.classList.add("blink-one");
                        }
                    }
                }
                xhr.open("GET", "/get_progresso/%s/");
                xhr.send();
                setTimeout(%s, 10000);
            }
            %s();
            </script>"""%(
                "get_progresso_"+str(obj.id),
                str(obj.id)+"_progresso",
                str(obj.id),
                "get_progresso_"+str(obj.id),
                "get_progresso_"+str(obj.id)
                )
            return mark_safe('<div>%s %s</div>'%(h,s))
        else:
            return int2size(obj.progresso)
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-txt/', self.import_txt),
            path('import-tiffs-de-pasta-local/', self.import_tiffs_de_pasta_local),
            re_path(r'download-file/(?P<pk>\d+)$', self.download_file, name='cbers4amanager_download_download-file'),
        ]
        return my_urls + urls
    def render_change_form(self, request, context, *args, **kwargs):
        obj = context['original']
        if obj is not None:
            banda = obj.nome.split("_")[-1]
            field = forms.FilePathField(path=context['adminform'].form.fields['arquivo'].path,match='(.*)'+banda)
            choices = [('','---------')]
            choices.extend(field.choices)
            context['adminform'].form.fields['arquivo']._set_choices(choices)
            if obj.arquivo is not None:
                context['adminform'].form.fields['arquivo'].help_text += mark_safe('<br><a href="{}" target="blank">{}</a>'.format(
                    reverse('admin:cbers4amanager_download_download-file', args=[obj.pk])
                    ,os.path.basename(obj.arquivo)
                ))
        return super(MyDownloadAdmin, self).render_change_form(request, context, *args, **kwargs)
    def download_file(self, request, pk):
        p = Download.objects.get(pk=pk)
        arquivo = p.arquivo
        try:
            if arquivo:
                with open(arquivo, 'rb') as f:
                    file_data = f.read()
                    # sending response 
                    response = HttpResponse(file_data, content_type='image/tiff')
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(arquivo))
            else:
                response = HttpResponseNotFound('<h1>File not exist</h1>')
        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')
        return response
    @admin.action(description='Priorizar Download')
    def priorizar_download(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            queryset.update(prioridade=1)
            # STOP current downloads
            # Tb Encerra os related JOBs com erro, abrindo caminho pra um novo Job daqui a 1 minuto
            comando = "kill $(ps -auxw | grep make_download | grep -v grep | awk '/python/ {print $2}')"
            print(comando)
            os.system(comando)
        else:
            request.current_app = self.admin_site.name
            context = {
                'action':request.POST.get("action"),
                'queryset':queryset,
                'opts': self.model._meta,
                'tarefa': "PRIORIZAR"
            } 
            return render(request, "admin/download_confirmation.html", context)
    def import_txt(self, request):
        if request.method == "POST":
            # create Genere object from passed in data
            txt = request.FILES["file"]
            text = txt.read().decode("utf-8") 
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
                size = os.path.getsize(fullfname)
                if not size or size<100000: continue # arquivos muito pequenos podem ser atalhos ou hidden files
                print("IMPORTANDO:",f)
                try:
                    # Já existia a intenção desse download registrada no banco
                    d = Download.objects.get(nome__contains=f)
                    if d.finalizado: continue
                    if d.progresso==size: continue
                    # obsoleto qd este campo se tornou FilePath:
                    # with open(fullfname, "rb") as tif:
                    #     d.arquivo= ContentFile(tif.read(), name=f)
                    dst = os.path.join(Download._meta.get_field('arquivo').path,f)
                    if dst!=fullfname: os.rename(fullfname, dst)
                    d.arquivo = dst
                    d.finalizado=True
                    d.content_length=size
                    d.progresso=size
                    d.save()
                    m+=1
                except Exception as e:
                    print(str(e))
                    nome_base = f.split("_BAND")[0]
                    tipo = "red" if "BAND3" in f else "green" if "BAND2" in f else "blue" if "BAND1" in f else "pan" if "BAND0" in f else ""
                    d = Download(url=fullfname,nome=f,nome_base=nome_base,tipo=tipo,finalizado=True,terminado_em = timezone.now())
                    ## obsoleto qd este campo se tornou FilePath:
                    # with open(fullfname, "rb") as tif:
                    #     d.arquivo= ContentFile(tif.read(), name=f)
                    #     d.content_length = size
                    #     d.progresso = size
                    dst = os.path.join(Download._meta.get_field('arquivo').path,f) # Inofensivo se o destino=origem
                    if dst!=fullfname: os.rename(fullfname, dst)
                    d.arquivo = dst
                    d.content_length = d.progresso = os.path.getsize(dst)
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

admin.site.register(Download,MyDownloadAdmin)


################ ComposicaoRGB ##################
@admin.action(description='Update limites (após composição colorida)')
def set_bounds_rgb(modeladmin, request, queryset):
    for e in queryset:
        rst = GDALRaster(e.rgb, write=False)
        xmin, ymin, xmax, ymax = rst.extent
        pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        print(pol)
        poly = GEOSGeometry(pol,srid=rst.srid)
        e.bounds = poly
        e.save()

class PostgreSQLGroupConcat(Aggregate):
    template = "array_to_string(array_agg(%(expressions)s), ',') "
    #template = '%(function)s(%(distinct)s %(expression)s)'
    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=CharField(), **extra)

class MyComposicaoRGBadmin(OSMGeoAdmin):
    search_fields = ['rgb']
    actions = [set_bounds_rgb]
    list_display = ('_nome', 'finalizado','_download')
    change_list_template = "cbers4amanager/composicaorgb_changelist.html"
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('get-downloads/', self.get_downloads),
            re_path(r'download-file/(?P<pk>\d+)$', self.download_file, name='cbers4amanager_composicaorgb_download-file'),
        ]
        return my_urls + urls
    def render_change_form(self, request, context, *args, **kwargs):
        obj = context['original']
        if obj is not None:
            if obj.rgb is not None:
                context['adminform'].form.fields['rgb'].help_text += mark_safe('<br><a href="{}" target="blank">{}</a>'.format(
                    reverse('admin:cbers4amanager_composicaorgb_download-file', args=[obj.pk])
                    ,os.path.basename(obj.rgb)
                ))
        return super(MyComposicaoRGBadmin, self).render_change_form(request, context, *args, **kwargs)
    @admin.display(ordering='finalizado')
    def _download(self,obj):
        if obj.rgb:
            return mark_safe('<a href="{}"><img src="/static/admin/img/icon-viewlink.svg" alt="View"></a>'.format(reverse('admin:cbers4amanager_composicaorgb_download-file', args=[obj.pk])))
        else:
            return "-"
    @admin.display(ordering='nome_base')
    def _nome(self,obj):
        return str(obj.red.nome_base or obj.green.nome_base or obj.blue.nome_base or obj.nome_base)+"_RGB.tif"
    def download_file(self, request, pk):
        p = ComposicaoRGB.objects.get(pk=pk)
        arquivo = p.rgb
        try:
            if arquivo:
                with open(arquivo, 'rb') as f:
                    file_data = f.read()
                    # sending response 
                    response = HttpResponse(file_data, content_type='image/tiff')
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(arquivo))
            else:
                response = HttpResponseNotFound('<h1>File not exist</h1>')
        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')
        return response
    def get_downloads(self, request):
        queryset = Download.objects.filter(finalizado=True)
        newqueryset = queryset.filter(nome__icontains="BAND3") | queryset.filter(nome__icontains="BAND2") | queryset.filter(nome__icontains="BAND1") 
        finalqueryset = newqueryset.values("nome_base").annotate(downloads=PostgreSQLGroupConcat('nome'))
        #print(queryset.query)
        agrupamento = []
        for object in finalqueryset.all():
            if not ComposicaoRGB.objects.filter(nome_base=object['nome_base']) and all(i in object['downloads'] for i in ["BAND3","BAND2","BAND1"]):
                print(object)
                bandas = {}
                for nome in object['downloads'].split(","):
                    if "BAND3" in nome:
                        bandas['red']=('style=color:red',nome)
                for nome in object['downloads'].split(","):
                    if "BAND2" in nome:
                        bandas['green']=('style=color:green',nome)
                for nome in object['downloads'].split(","):
                    if "BAND1" in nome:
                        bandas['blue']=('style=color:blue',nome)
                agrupamento.append(bandas)
        if request.method == "POST":
            # create Genere object from passed in data
            for bandas in agrupamento:
                red = Download.objects.get(nome=bandas['red'][1])
                green = Download.objects.get(nome=bandas['green'][1])
                blue = Download.objects.get(nome=bandas['blue'][1])
                rgb = ComposicaoRGB(red=red, green=green, blue=blue)
                rgb.nome_base = red.nome_base or green.nome_base or blue.nome_base
                rgb.save()
            self.message_user(request, "Adicionados %s registros"%(len(agrupamento)))
            return redirect("..")
        payload = {'queryset':finalqueryset,'opts': self.model._meta,'agrupamento':agrupamento}
        return render(
            request, "admin/get_downloads_form.html", payload
        )
    @admin.action(description='Começar Composição das linhas selecionadas')
    def comecar_composicao(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            aux = [str(q.pk) for q in queryset]
            print(aux)
            try:
                process = Process.objects.get(name="Composição")
            except:
                process = Process(name="Composição",description="Toda hora",run_if_err=True,
                                minute="1",hour="*",day_of_month="*",month="*",day_of_week="*")
                process.save()
            # DONE: Verificar se o id já está em description de um Task ativo
            ids = []
            for i in range(len(aux)):
                try:
                    q = Task.objects.filter(process=process).get(description__contains="'"+aux[i]+"'")
                    # Existe ativo, então não cria outro
                except Task.DoesNotExist as e:
                    # Não existe ativo, então cria outro
                    ids.append(aux[i])
                    continue
            last = Task.objects.order_by('-id').first()
            next_id = last.id + 1 if last else 1
            t = Task(process=process,name="Composição "+str(next_id), description= "Composição dos itens: %s"%(ids),
                    interpreter= os.popen('which python3').read().replace('\n',''),
                    arguments = " ".join(ids))
            path = os.path.join(os.getcwd(),'cbers4amanager/management/composicaorgb_cbers4a.py')
            with open(path, "rb") as py:
                t.code= ContentFile(py.read(), name=os.path.basename(path))
            try:
                t.save()
                self.message_user(request,
                                    "Composição de %s iniciada."%(ids), 
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
                'tarefa': "COMPOSICAO"
            } 
            return render(request, "admin/composicao_confirmation.html", context)

admin.site.register(ComposicaoRGB,MyComposicaoRGBadmin)

class MyINOMClipperedAdmin(admin.ModelAdmin):
    actions = ['comecar_recortes_rgb','comecar_recortes_pan',set_finalizado]
    search_fields = ['nome']
    list_display = ('nome', '_recorte_rgb', '_recorte_pan', '_area_util', 'finalizado')
    change_list_template = "cbers4amanager/inomclippered_changelist.html"
    @admin.display(ordering='area_util')
    def _area_util(self,obj):
        if obj.area_util:
            nv = obj.cobertura_nuvens if obj.cobertura_nuvens else 0
            retorno = str(round((obj.area_util - nv)*100/obj.area_util,2))
        elif obj.area_util==None:
            retorno = "-"
        elif int(obj.area_util)==0:
            retorno = "0.0"
        else:
            retorno = "-"
        return retorno
    _area_util.short_description = 'Área Útil (%)'
    @admin.display(ordering='recorte_rgb')
    def _recorte_rgb(self,obj):
        if not obj.recorte_rgb:
            retorno = mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')
        else:
            retorno = mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return retorno
    @admin.display(ordering='recorte_pancromatica')
    def _recorte_pan(self,obj):
        if not obj.recorte_pancromatica:
            retorno = mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')
        else:
            retorno = mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return retorno
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('get-composicao/', self.get_composicao),
            re_path(r'download-file/(?P<pk>\d+)/(?P<field_name>\w+)$', self.download_file, name='cbers4amanager_inomclippered_download-file')
        ]
        return my_urls + urls
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['pancromatica'].queryset = Download.objects.filter(nome__contains='BAND0')
        obj = context['original']
        if obj is not None:
            if obj.recorte_rgb is not None:
                context['adminform'].form.fields['recorte_rgb'].help_text += mark_safe('<br><a href="{}" target="blank">{}</a>'.format(
                    reverse('admin:cbers4amanager_inomclippered_download-file', args=[obj.pk,'recorte_rgb'])
                    ,os.path.basename(obj.recorte_rgb)
                ))
            if obj.recorte_pancromatica is not None:
                context['adminform'].form.fields['recorte_pancromatica'].help_text += mark_safe('<br><a href="{}" target="blank">{}</a>'.format(
                    reverse('admin:cbers4amanager_inomclippered_download-file', args=[obj.pk,'recorte_pancromatica'])
                    ,os.path.basename(obj.recorte_pancromatica)
                ))
        return super(MyINOMClipperedAdmin, self).render_change_form(request, context, *args, **kwargs)
    def download_file(self, request, pk, field_name):
        i = INOMClippered.objects.get(pk=pk)
        arquivo = i.recorte_pancromatica if field_name=="recorte_pancromatica" else i.recorte_rgb
        try:
            with open(arquivo, 'rb') as f:
                file_data = f.read()
                # sending response 
                response = HttpResponse(file_data, content_type='image/tiff')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(arquivo))
        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')
            response['Content-Disposition'] = 'attachment; filename="whatever.txt"'
        return response
    def getIntersection(self, comprgb):
        print(comprgb)
        rst = GDALRaster(comprgb.rgb, write=False)
        xmin, ymin, xmax, ymax = rst.extent
        pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        poly = GEOSGeometry(pol,srid=rst.srid)
        queryset = INOM.objects.filter(bounds__intersects=poly)
        return queryset
    def get_composicao(self, request):
        msg=""
        rgbs_ja_registrados_para_recorte = INOMClippered.objects.values('rgb').all()
        n_registrar_esses_ids = list(set([i['rgb'] for i in rgbs_ja_registrados_para_recorte]))
        queryset = ComposicaoRGB.objects.filter(finalizado=True).exclude(id__in=n_registrar_esses_ids)
        if request.method == "POST":
            # create Genere object from passed in data
            count = 0
            for comprgb in queryset.all():
                try:
                    inoms = self.getIntersection(comprgb)
                except:
                    continue
                print(inoms)
                if not inoms: 
                    msg += ": Sem interseção com áreas de interesse."
                    continue
                for inom in inoms.all():
                    if not INOMClippered.objects.filter(nome=comprgb.nome_base+"_"+inom.inom):
                        i = INOMClippered(nome=comprgb.nome_base+"_"+inom.inom,inom=inom,rgb=comprgb)
                        try:
                            i.pancromatica = Download.objects.filter(finalizado=True).get(nome_base__iexact=comprgb.nome_base,tipo='pan')
                        except:
                            pass
                        i.save()
                        count+=1
            self.message_user(request, "Adicionados %s registros%s"%(count,msg))
            return redirect("..")
        payload = {'queryset':queryset,'opts': self.model._meta}
        return render(
            request, "admin/get_composicoes_form.html", payload
        )
    @admin.action(description='Começar Recortes RGB das linhas selecionadas')
    def comecar_recortes_rgb(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            # TODO
            self.message_user(request, "Adicionados %s registros"%(queryset))
        else:
            request.current_app = self.admin_site.name
            context = {
                'action':request.POST.get("action"),
                'queryset':queryset,
                'opts': self.model._meta,
                'tarefa': "RECORTE"
            } 
            return render(request, "admin/recorte_confirmation.html", context)
    @admin.action(description='Começar Recortes PAN das linhas selecionadas')
    def comecar_recortes_pan(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            #TODO
            self.message_user(request, "Adicionados %s registros"%(queryset))
        else:
            request.current_app = self.admin_site.name
            context = {
                'action':request.POST.get("action"),
                'queryset':queryset,
                'opts': self.model._meta,
                'tarefa': "COMPOSICAO"
            } 
            return render(request, "admin/recorte_confirmation.html", context)
    @admin.action(description='Update finalizado=True das linhas selecionadas')
    def set_finalizado(modeladmin, request, queryset):
        queryset.update(finalizado=True)
    
admin.site.register(INOMClippered,MyINOMClipperedAdmin)


class MyPansharpenedAdmin(admin.ModelAdmin):
    actions = ['comecar_pansharp']
    list_display = ('_nome', 'finalizado','_download')
    change_list_template = "cbers4amanager/pansharp_changelist.html"
    readonly_fields = ('download_link',)
    fields = ('insumos','pansharp', 'finalizado','download_link')
    @admin.display(ordering='pansharp')
    def _download(self,obj):
        if obj.pansharp:
            return mark_safe('<a href="{}"><img src="/static/admin/img/icon-viewlink.svg" alt="View"></a>'.format(reverse('admin:cbers4amanager_pansharpened_download_pansharp', args=[obj.pk])))
        else:
            return "-"
    @admin.display(ordering='pansharp')
    def _nome(self,obj):
        if obj.pansharp: return os.path.basename(obj.pansharp)
        else: return str(obj.insumos)
    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['pansharp'].queryset = Download.objects.filter(nome__contains='BAND0')
         return super(MyPansharpenedAdmin, self).render_change_form(request, context, *args, **kwargs)
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('get-recortes/', self.get_recortes),
            re_path(r'download-file/(?P<pk>\d+)$', self.download_file, name='cbers4amanager_pansharpened_download_pansharp')
        ]
        return my_urls + urls
    def download_link(self, obj):
        if obj.id is not None:
            return mark_safe(
                '<a href="{}">Download file</a>'.format(reverse('admin:cbers4amanager_pansharpened_download_pansharp', args=[obj.pk]))
            ) 
        else:
            return '-'
    download_link.short_description = "Download resultado"
    def download_file(self, request, pk):
        p = Pansharpened.objects.get(pk=pk)
        arquivo = p.pansharp
        try:
            with open(arquivo, 'rb') as f:
                file_data = f.read()
                # sending response 
                response = HttpResponse(file_data, content_type='image/tiff')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(arquivo))
        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')
            response['Content-Disposition'] = 'attachment; filename="whatever.txt"'
        return response
    def get_recortes(self, request):
        insumos_para_pansharp_ja_registrados = Pansharpened.objects.values('insumos').all()
        n_registrar_esses_ids = list(set([i['insumos'] for i in insumos_para_pansharp_ja_registrados]))
        queryset = INOMClippered.objects.filter(finalizado=True).exclude(id__in=n_registrar_esses_ids)
        if request.method == "POST":
            # create Genere object from passed in data
            count = 0
            for inomclippered in queryset.all():
                p = Pansharpened(insumos=inomclippered)
                p.save()
                count += 1
            self.message_user(request, "Adicionados %s registros"%(count))
            return redirect("..")
        payload = {'queryset':queryset,'opts': self.model._meta}
        return render(
            request, "admin/get_recortes_form.html", payload
        )
    @admin.action(description='Começar Pansharpening das linhas selecionadas')
    def comecar_pansharp(self, request, queryset):
        if request.method=='POST' and "confirmation" in request.POST:
            #TODO
            self.message_user(request, "Adicionados %s registros"%(queryset))
        else:
            request.current_app = self.admin_site.name
            context = {
                'action':request.POST.get("action"),
                'queryset':queryset,
                'opts': self.model._meta,
                'tarefa': "PANSHARP"
            } 
            return render(request, "admin/recorte_confirmation.html", context)
    



admin.site.register(Pansharpened, MyPansharpenedAdmin)

