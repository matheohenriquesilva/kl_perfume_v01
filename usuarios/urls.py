from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('controlador/', views.controlador, name="controlador"),
    path('cadastro/', views.cadastro, name="cadastro"),
    path('login/', views.logar, name="login"),
    path('sair/', views.sair, name="sair"),
]