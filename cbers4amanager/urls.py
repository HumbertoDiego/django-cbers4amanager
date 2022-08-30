# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views
from django.views.static import serve

app_name = 'cbers4amanager'
urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('index', views.index, name='index'),
    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    re_path(r'^static/cbers4amanager/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]