from audioop import minmax
from django.contrib.gis.db import models
import os
from django.conf import settings

# 0) ASC 1:25k
class INOM(models.Model):
    inom = models.CharField(max_length=20,unique=True)
    bounds = models.PolygonField(blank=True, null=True )
    def __str__(self):
        return str(self.inom)

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

# 2)
class ComposicaoRGB(models.Model):
    red = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='red', blank=True, null=True )
    green = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='green', blank=True, null=True )
    blue = models.ForeignKey(Download, on_delete=models.SET_NULL, related_name='set', blank=True, null=True )
    rgb = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT, 'rgb'),blank=True, null=True )
    def __str__(self):
        return str(self.rgb)
    class Meta:
        verbose_name = ["2) Composição RGB"]

# 3) Cortar dentro dos INOMs 1:25k as composições RGB e a banda PAN
class INOMClippered(models.Model):
    inom = models.ForeignKey(INOM,on_delete=models.SET_NULL,blank=True, null=True )
    rgb = models.ForeignKey(ComposicaoRGB, on_delete=models.SET_NULL, blank=True, null=True)
    pancromatica = models.ForeignKey(Download, on_delete=models.SET_NULL, blank=True, null=True )
    cobertura_nuvens = models.FloatField(default=1, blank=True, null=True )
    pronto_para_pansharppen = models.BooleanField(default=False,blank=True, null=True )
    def __str__(self):
        return str(self.pronto_para_pansharppen)

# 4) Pan
class Pansharpened(models.Model):
    insumos = models.ForeignKey(INOMClippered, on_delete=models.SET_NULL, blank=True, null=True)
    pansharp = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT,'pansharp'),blank=True, null=True )
    def __str__(self):
        return str(self.pansharp)