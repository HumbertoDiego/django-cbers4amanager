from django.shortcuts import render
from django.http import HttpResponse
from .models import INOM, Download, ComposicaoRGB, INOMClippered, Pansharpened
import django.contrib.gis.db.models.functions as St
from django.conf import settings

def index(request):
    context = {} 
    return render(request, 'cbers4amanager/index.html', context)

def get_progresso(request,d_id):
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
    return HttpResponse("%s" % int2size(Download.objects.get(id=d_id).progresso))