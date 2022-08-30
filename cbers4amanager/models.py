from django.contrib.gis.db import models
import os
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import mark_safe

# -1) Projetos
class Projeto(models.Model):
    nome = models.CharField(max_length=30,unique=True)
    bounds = models.PolygonField(blank=True, null=True)
    def __str__(self):
        return str(self.nome)

# 0) ASC 1:25k
class INOM(models.Model):
    inom = models.CharField(max_length=20,unique=True)
    mi = models.CharField(max_length=20,blank=True,null=True,verbose_name = "Mapa Índice")
    bounds = models.PolygonField(blank=True, null=True )
    melhor_imagem = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/pansharp'),
                                    blank=True, null=True, match='(.*).tif', max_length=300,
    )
    projeto = models.ForeignKey(Projeto, on_delete=models.SET_NULL, blank=True, null=True, related_name='relateds',)
    def __str__(self):
        return str(self.inom)
    class Meta:
        verbose_name = "Área de interesse"
        verbose_name_plural = "Áreas de interesse"

# 1)
class Download(models.Model):
    url = models.CharField(max_length=500,unique=True)
    nome = models.CharField(max_length=500,blank=True, null=True )
    nome_base = models.CharField(max_length=500,blank=True, null=True )
    tipo = models.CharField(max_length=5,blank=True, null=True,
                            choices=[('nir','Infravermelho Próximo'),('red','Vermelho'),('green','Verde'),('blue','Azul'),('pan','Pancromática'),('','Indefinido')],
                            default='')
    iniciado_em = models.DateTimeField(blank=True, null=True )
    terminado_em = models.DateTimeField(blank=True, null=True )
    content_length = models.BigIntegerField(blank=True, null=True )
    progresso = models.BigIntegerField(blank=True, null=True )
    arquivo = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/bandas'),blank=True, null=True)
    bounds = models.PolygonField(blank=True, null=True )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.nome)
    class Meta:
        verbose_name = "Download"
        verbose_name_plural = "1) Downloads"

# 2.1)
class ComposicaoRGB(models.Model):
    red = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='red', blank=True, null=True )
    green = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='green', blank=True, null=True )
    blue = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='set', blank=True, null=True )
    nome_base = models.CharField(max_length=500,blank=True, null=True, unique=True )
    rgb = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/rgbs'),blank=True, null=True,match='(.*)RGB.tif', help_text='Este arquivo será criado após escolher a opção "Começar composição das linhas selecionadas".' )
    bounds = models.PolygonField(blank=True, null=True )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.red.nome_base or self.green.nome_base or self.blue.nome_base or self.nome_base)+"_RGB.tif"
    class Meta:
        verbose_name = "Composição RGB"
        verbose_name_plural = "2.1) Composições RGB"

# 2.2)
# class ComposicaoNDVI(models.Model):
#     red = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='vermelho', blank=True, null=True )
#     nir = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='nir', blank=True, null=True )
#     nome_base = models.CharField(max_length=500,blank=True, null=True, unique=True )
#     ndvi = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/ndvis'),blank=True, null=True,match='(.*)NDVI.tif', help_text='Este arquivo será criado após escolher a opção "Começar composição das linhas selecionadas".' )
#     bounds = models.PolygonField(blank=True, null=True )
#     finalizado = models.BooleanField(default=False,blank=True, null=True )
#     def __str__(self):
#         return str(self.red.nome_base or self.nir.nome_base or self.nome_base)+"_NDVI.tif"
#     class Meta:
#         verbose_name = "Composição NDVI"
#         verbose_name_plural = "2.2) Composições NDVI"


# 3) Cortar dentro dos INOMs 1:25k as composições RGB e a banda PANV
class INOMClippered(models.Model):
    nome = models.CharField(max_length=500, unique=True )
    inom = models.ForeignKey(INOM,on_delete=models.SET_NULL,blank=True, null=True )
    rgb = models.ForeignKey(ComposicaoRGB, on_delete=models.SET_NULL, blank=True, null=True)
    pancromatica = models.ForeignKey(Download, on_delete=models.SET_NULL, blank=True, null=True,verbose_name="Pancromática" )
    recorte_rgb = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/recortes'),blank=True, null=True, match='(.*)RGB.tif', max_length=300, help_text='Este arquivo será criado após escolher a opção "Começar recorte RGB das linhas selecionadas". ' )
    recorte_pancromatica = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/recortes'),blank=True, null=True,match='(.*)PAN.tif', max_length=300, help_text='Este arquivo será criado após escolher a opção "Começar recorte PAN das linhas selecionadas".' )
    area_util =  models.FloatField(blank=True, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name="Área com dados (%)", help_text=mark_safe('Este dado será computado após escolher a opção "Começar recorte RGB das linhas selecionadas". <br>Equivale ao "STATISTICS_VALID_PERCENT" mínimo entre as bandas do Recorte RGB, obtido pelo comando <i>gdalinfo recorte.tif -stats</i>.') )
    cobertura_nuvens = models.FloatField(blank=True, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name="Área de nuvens (%)", help_text=mark_safe('Este dado será computado após escolher a opção "Começar recorte RGB das linhas selecionadas". <br>Equivale ao "STATISTICS_VALID_PERCENT" da classificação das nuvens, obtido pelo comando <i>gdalinfo nuvens.tif -stats</i>.')  )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Recorte RGB/PAN"
        verbose_name_plural = "3) Recortes RGB/PAN"

# 4) Pan
class Pansharpened(models.Model):
    insumos = models.ForeignKey(INOMClippered, on_delete=models.SET_NULL, blank=True, null=True)
    pansharp = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'a/pansharp'),
                                    blank=True, null=True, match='(.*).tif', max_length=300,
                                    help_text='Este arquivo será criado após escolher a opção "Começar Fusão RGB/PAN das linhas selecionadas". ',
    )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        if self.pansharp: return os.path.basename(self.pansharp)
        else: return str(self.insumos)
    class Meta:
        verbose_name = "Fusão RGB/PAN"
        verbose_name_plural = "4) Fusão RGB/PAN"