from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Tipo(models.Model):
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo

class Marca(models.Model):
    marca = models.CharField(max_length=50)

    def __str__(self):
        return self.marca

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING)
    marca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING)
    preco_compra = models.FloatField()
    preco_venda = models.FloatField()
    ciclo = models.IntegerField()
    lucro = models.FloatField()
    quantidade = models.IntegerField(default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.nome.upper():_<35} | PC: R$ {self.preco_compra:<.2f} | PV: R$ {self.preco_venda:<.2f} | Lucro: R$ {self.lucro:<.2f} | Qntd: {self.quantidade} | {self.marca} | {self.tipo}"

class Cliente(models.Model):
    choices_status = (('D', 'DEVENDO'),
                      ('P', 'PAGO'),
                      ('I', 'INATIVO'))
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    num_telefone = models.CharField(max_length=15)
    status = models.CharField(max_length=1, choices=choices_status, default='I')
    saldo_devedor = models.FloatField(default=0)

    def atualizar(self):
        if self.status == 'I':
            self.status = 'D'
        elif self.saldo_devedor <= 0:
            self.status = 'P'
        elif self.saldo_devedor > 0:
            self.status = 'D'

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"

class Venda(models.Model):
    choices_status = (('A', 'EM ABERTO'),
                      ('P', 'PAGO'))
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produtos = models.ManyToManyField(Produto)
    valor_compra = models.FloatField()
    valor_venda = models.FloatField()
    lucro = models.FloatField()
    parcelas = models.IntegerField()
    saldo_devedor = models.FloatField()
    status = models.CharField(max_length=1, choices=choices_status)
    data = models.DateField(default=timezone.now())

    def atualizar(self):
        if self.saldo_devedor > 0:
            self.status = 'A'
        else:
            self.status = 'P'

    def __str__(self):
        return f"ID: {self.id} -|- DATA: {self.data} |- VC: {self.valor_compra:_<10} -|- VV: {self.valor_venda:_<10} -|- User: {self.usuario.username} -|- Cliente: {self.cliente.nome:_<30}"

class Caixa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    saldo_atual = models.FloatField(default=0)
    saldo_devedor = models.FloatField(default=0)
    receber = models.FloatField(default=0)


class Pagamento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    valor = models.FloatField()
    data = models.DateField(default=timezone.now())

    def __str__(self):
        return f"|-{self.usuario.username}-|-{self.cliente.nome}-|-{self.venda.id}-|-R${self.valor}-|-{self.data}-|"

class Boleto(models.Model):
    choices_status = (('D', 'DEVENDO'),
                      ('P', 'PAGO'),
                      ('V', 'VENCIDO'))
    data_emissao = models.DateField(default=timezone.now())
    data_vencimento = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor = models.FloatField(default=0)
    vendas = models.ManyToManyField(Venda)
    status = models.CharField(max_length=1, choices=choices_status, default='D')
    data_pagamento = models.DateField(default=timezone.now())

    def __str__(self):
        return f"{self.id} - {self.usuario.username} - {self.valor} - {self.data_vencimento} - {self.status}"
