from django.conf.urls import url

from . import views

urlpatterns = [
               url(r'^$', views.homepage, name='homepage'),
               url(r'^issuehome/', views.issuehome, name='issuehome'),
               url(r'^filter/$', views.filter, name='filter'),
               ]
