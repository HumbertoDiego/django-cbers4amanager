from django.shortcuts import render
from .models import INOM, Download, ComposicaoRGB, INOMClippered, Pansharpened
import django.contrib.gis.db.models.functions as St
from django.conf import settings

def index(request):
    context = {} 
    return render(request, 'cbers4amanager/index.html', context)
