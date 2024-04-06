from django.urls import path
from . import views

urlpatterns = [
    path('', views.caixa, name="caixa"),
    path('novo_boleto/', views.novo_boleto, name="novo_boleto"),
    path('listar_boletos/', views.listar_boletos, name="listar_boletos"),
    path('remover_boleto/<int:id>', views.remover_boleto, name="remover_boleto"),
    path('ver_boleto/<int:id>', views.ver_boleto, name="ver_boleto"),
    path('pagar_boleto_caixa/<int:id>', views.pagar_boleto_caixa, name="pagar_boleto_caixa"),
    path('pagar_boleto_externo/<int:id>', views.pagar_boleto_externo, name="pagar_boleto_externo"),
]
