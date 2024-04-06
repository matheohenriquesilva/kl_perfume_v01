from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from vendas.models import Caixa, Venda, Boleto
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, date

# Create your views here.
@login_required()
def caixa(request):
    if request.method == "GET":
        caixa = Caixa.objects.get(usuario_id=request.user.id)
        return render(request, 'caixa.html', {'caixa': caixa})

@login_required()
def novo_boleto(request):
    if request.method == "GET":
        vendas = Venda.objects.all()
        return render(request, 'novo_boleto.html', {'vendas': vendas})
    elif request.method == "POST":
        vendas_poo = Venda.objects.all()
        vendas = request.POST.getlist("vendas")
        data_vencimento = request.POST.get("data_vencimento")
        if len(vendas) == 0:
            messages.add_message(request, constants.ERROR, 'Escolha pelo menos uma VENDA.')
            return render(request, 'novo_boleto.html', {'vendas': vendas_poo})
        elif len(data_vencimento) == 0:
            messages.add_message(request, constants.ERROR, 'Escolha uma data de vencimento.')
            return render(request, 'novo_boleto.html', {'vendas': vendas_poo})
        boleto = Boleto(
            data_vencimento=data_vencimento,
            usuario_id=request.user.id
        )
        boleto.save()
        for venda_id in vendas:
            venda = Venda.objects.get(id=venda_id)
            boleto.valor += venda.valor_compra
            boleto.valor = round(boleto.valor, 2)
            boleto.vendas.add(venda)
        boleto_aux = Boleto.objects.filter(data_emissao=boleto.data_emissao, data_vencimento=data_vencimento, status=boleto.status, valor=boleto.valor)
        if boleto_aux is not None:
            for b in boleto_aux:
                if b.id != boleto.id:
                    messages.add_message(request, constants.ERROR, 'Já existe um boleto com esses dados iguais, Revise as informações.')
                    return render(request, 'novo_boleto.html', {'vendas': vendas_poo})
        boleto.save()
        messages.add_message(request, constants.SUCCESS, 'Boleto cadastrado com sucesso.')
        return redirect('/caixa/novo_boleto')

@login_required()
def listar_boletos(request):
    if request.method == "GET":
        data_atual = date.today()
        boletos = Boleto.objects.filter(usuario=request.user)
        for b in boletos:
            if b.status == "D" and b.data_vencimento < data_atual:
                b.status = "V"
        return render(request, 'listar_boletos.html', {'boletos': boletos})

@login_required()
def remover_boleto(request, id):
    boleto = Boleto.objects.get(id=id)
    boleto.delete()
    messages.add_message(request, constants.SUCCESS, 'Boleto removido com sucesso.')
    return redirect('/caixa/listar_boletos')

@login_required()
def ver_boleto(request, id):
    data_atual = date.today()
    boletos = Boleto.objects.all()
    for b in boletos:
        if b.status == "D" and b.data_vencimento < data_atual:
            b.status = "V"
    boleto = Boleto.objects.get(id=id)
    return render(request, "ver_boleto.html", {'boleto': boleto, 'vendas_boleto': boleto.vendas.all()})

@login_required()
def pagar_boleto_caixa(request, id):
    if request.method == "GET":
        return redirect(f"/caixa/ver_boleto/{id}")
    elif request.method == "POST":
        boleto = Boleto.objects.get(id=id)
        caixa = Caixa.objects.get(usuario_id=request.user.id)
        if caixa.saldo_atual < boleto.valor:
            messages.add_message(request, constants.ERROR, 'Saldo insuficiente para pagamento do Boleto.')
            return redirect(f"/caixa/ver_boleto/{id}")
        elif boleto.status == "P":
            messages.add_message(request, constants.ERROR, 'O Boleto já está pago.')
            return redirect(f"/caixa/ver_boleto/{id}")
        caixa.saldo_atual -= boleto.valor
        round(caixa.saldo_atual, 2)
        caixa.saldo_devedor -= boleto.valor
        round(caixa.saldo_devedor, 2)
        caixa.save()
        boleto.status = "P"
        boleto.data_pagamento = datetime.now()
        boleto.save()
        messages.add_message(request, constants.SUCCESS, f'PAGAMENTO FEITO COM SUCESSO, seu novo saldo em caixa é de {caixa.saldo_atual}.')
        return redirect(f"/caixa/ver_boleto/{id}")

@login_required()
def pagar_boleto_externo(request, id):
    if request.method == "GET":
        return redirect(f"/caixa/ver_boleto/{id}")
    elif request.method == "POST":
        boleto = Boleto.objects.get(id=id)
        caixa = Caixa.objects.get(usuario_id=request.user.id)
        if boleto.status == "P":
            messages.add_message(request, constants.ERROR, 'O Boleto já está pago.')
            return redirect(f"/caixa/ver_boleto/{id}")
        caixa.saldo_devedor -= boleto.valor
        round(caixa.saldo_devedor, 2)
        caixa.save()
        boleto.status = "P"
        boleto.data_pagamento = datetime.now()
        boleto.save()
        messages.add_message(request, constants.SUCCESS, f'PAGAMENTO FEITO COM SUCESSO, seu novo saldo em caixa é de {caixa.saldo_atual}.')
        return redirect(f"/caixa/ver_boleto/{id}")
