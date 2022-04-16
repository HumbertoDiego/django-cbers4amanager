from audioop import minmax
from django.contrib.gis.db import models
import os
from django.conf import settings

# 0) ASC 1:25k
class INOM(models.Model):
    inom = models.CharField(max_length=20,unique=True)
    mi = models.CharField(max_length=20,blank=True,null=True,verbose_name = "Mapa Índice")
    bounds = models.PolygonField(blank=True, null=True )
    def __str__(self):
        return str(self.inom)
    class Meta:
        verbose_name = "Área de Interesse"
        verbose_name_plural = "0) Áreas de Interesse"

# 1)
class Download(models.Model):
    url = models.CharField(max_length=500,unique=True)
    nome = models.CharField(max_length=500,blank=True, null=True )
    nome_base = models.CharField(max_length=500,blank=True, null=True )
    tipo = models.CharField(max_length=5,blank=True, null=True,
                            choices=[('red','Vermelho'),('green','Verde'),('blue','Azul'),('pan','Pancromática'),('','Indefinido')],
                            default='')
    bounds = models.PolygonField(blank=True, null=True )
    iniciado_em = models.DateTimeField(blank=True, null=True )
    terminado_em = models.DateTimeField(blank=True, null=True )
    content_length = models.BigIntegerField(blank=True, null=True )
    progresso = models.CharField(max_length=10,blank=True, null=True )
    arquivo = models.FileField(upload_to='bandas/',blank=True, null=True )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.nome)
    class Meta:
        verbose_name = "Download"
        verbose_name_plural = "1) Downloads"

# 2)
class ComposicaoRGB(models.Model):
    red = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='red', blank=True, null=True )
    green = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='green', blank=True, null=True )
    blue = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='set', blank=True, null=True )
    nome_base = models.CharField(max_length=500,blank=True, null=True, unique=True )
    rgb = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'rgbs'),blank=True, null=True,match='(.*)RGB.tif', help_text='Este arquivo será criado após escolher a opção "Começar composição das linhas selecionadas".' )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.red.nome_base or self.green.nome_base or self.blue.nome_base or self.nome_base)+"_RGB.tif"
    class Meta:
        verbose_name = "Composição RGB"
        verbose_name_plural = "2) Composições RGB"

# 3) Cortar dentro dos INOMs 1:25k as composições RGB e a banda PAN
class INOMClippered(models.Model):
    nome = models.CharField(max_length=500, unique=True )
    inom = models.ForeignKey(INOM,on_delete=models.SET_NULL,blank=True, null=True )
    rgb = models.ForeignKey(ComposicaoRGB, on_delete=models.SET_NULL, blank=True, null=True)
    pancromatica = models.ForeignKey(Download, on_delete=models.SET_NULL, blank=True, null=True,verbose_name="Pancromática" )
    recorte_rgb = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'recortes'),blank=True, null=True,match='(.*)RGB.tif', help_text='Este arquivo será criado após escolher a opção "Começar recorte RGB das linhas selecionadas".' )
    recorte_pancromatica = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'recortes'),blank=True, null=True,match='(.*)RGB.tif', help_text='Este arquivo será criado após escolher a opção "Começar recorte PAN das linhas selecionadas".' )
    cobertura_nuvens = models.FloatField(default=1, blank=True, null=True )
    finalizado = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.rgb.nome_base)+"_"+str(self.inom)
    class Meta:
        verbose_name = "Recorte RGB/PAN"
        verbose_name_plural = "3) Recortes RGB/PAN"

# 4) Pan
class Pansharpened(models.Model):
    insumos = models.ForeignKey(INOMClippered, on_delete=models.SET_NULL, blank=True, null=True)
    pansharp = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT,'pansharp'),blank=True, null=True )
    def __str__(self):
        return str(self.pansharp)
    class Meta:
        verbose_name = "Fusão RGB/PAN"
        verbose_name_plural = "4) Fusão RGB/PAN"