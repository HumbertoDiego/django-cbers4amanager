# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views
from django.views.static import serve
from django.conf import settings
import os

app_name = 'cbers4amanager'
urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('index', views.index, name='index'),
    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.MEDIA_ROOT, 'a'),
            'show_indexes': True
        }),
    re_path(r'^amostras/(?P<path>.*)$', serve, {
            'document_root': settings.CBERS4AMANAGER['SAMPLE_FOLDER'],
            'show_indexes': True
        }),
]