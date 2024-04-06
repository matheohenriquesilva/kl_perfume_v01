from django.urls import path
from . import views

urlpatterns = [
    path('nova_venda/<int:id>', views.nova_venda, name="nova_venda"),
    path('novo_produto/', views.novo_produto, name="novo_produto"),
    path('novo_cliente/', views.novo_cliente, name="novo_cliente"),
    path('clientes/', views.cliente, name="cliente"),
    path('listar_clientes/', views.listar_clientes, name="listar_clientes"),
    path('remover_cliente/<int:id>', views.remover_cliente, name="remover_cliente"),
    path('vendas/', views.venda, name="venda"),
    path('listar_vendas/', views.listar_vendas, name="listar_vendas"),
    path('remover_venda/<int:id>', views.remover_venda, name="remover_venda"),
    path('produtos/', views.produto, name="produto"),
    path('listar_produtos/', views.listar_produtos, name="listar_produtos"),
    path('remover_produto/<int:id>', views.remover_produto, name="remover_produto"),
    path('ver_cliente/<int:id>', views.ver_cliente, name="ver_cliente"),
    path('adicionar_pagamento/', views.adicionar_pagamento, name="adicionar_pagamento"),
    path('ver_venda/<int:id>', views.ver_venda, name="ver_venda"),
    path('ver_produto/<int:id>', views.ver_produto, name="ver_produto"),
    path('remover_pagamento/<int:id>', views.remover_pagamento, name="remover_pagamento"),
    path('api_vendas_por_produtos/', views.api_vendas_por_produtos, name="api_vendas_por_produtos"),
    path('api_pagamentos_por_clientes/', views.api_pagamentos_por_clientes, name="api_pagamentos_por_clientes"),
    path('api_faturamento_por_mes/', views.api_faturamento_por_mes, name="api_faturamento_por_mes"),
    path('api_vendas_por_clientes/', views.api_vendas_por_clientes, name="api_vendas_por_clientes"),
    path('editar_cliente/<int:id>', views.editar_cliente, name="editar_cliente"),
    path('editar_produto/<int:id>', views.editar_produto, name="editar_produto"),
]
