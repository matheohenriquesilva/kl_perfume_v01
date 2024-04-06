from django.contrib import admin
from .models import Tipo, Marca, Produto, Cliente, Venda, Caixa, Pagamento, Boleto

# Register your models here.
admin.site.register(Tipo)
admin.site.register(Marca)
admin.site.register(Produto)
admin.site.register(Cliente)
admin.site.register(Venda)
admin.site.register(Caixa)
admin.site.register(Pagamento)
admin.site.register(Boleto)
