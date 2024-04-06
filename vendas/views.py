from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Cliente, Tipo, Marca, Produto, Venda, Pagamento, Caixa
from django.contrib import messages
from django.contrib.messages import constants
from django.http import JsonResponse
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Create your views here.
@login_required()
def nova_venda(request, id):
    if request.method == "GET":
        cliente_poo = Cliente.objects.all()
        produtos_poo = Produto.objects.all()
        return render(request, 'nova_venda.html',{'clientes': cliente_poo, 'produtos': produtos_poo, 'id': id})
    elif request.method == "POST":
        cliente_poo = Cliente.objects.all()
        produtos_poo = Produto.objects.all()
        cliente_id = request.POST.get("cliente")
        produtos = request.POST.getlist("produtos")
        parcelas = request.POST.get("parcelas")
        #VALIDAR OS DADOS.
        if cliente_id == None or len(produtos) == 0:
            messages.add_message(request, constants.ERROR, 'Escolha pelo menos 1 CLIENTE e 1 PRODUTO.')
            return render(request, 'nova_venda.html', {'clientes': cliente_poo, 'produtos': produtos_poo, 'id': id})
        valor_compra = 0
        valor_venda = 0
        lucro = 0
        for produto_id in produtos:
            produto = Produto.objects.get(id=produto_id)
            valor_compra += round(produto.preco_compra, 2)
            valor_venda += round(produto.preco_venda, 2)
            lucro += round(produto.lucro, 2)
        venda = Venda(
            usuario=request.user,
            cliente_id=cliente_id,
            valor_compra=round(valor_compra, 2),
            valor_venda=round(valor_venda, 2),
            saldo_devedor=round(valor_venda, 2),
            lucro=round(lucro, 2),
            parcelas=parcelas,
            status='A'
        )
        caixa = Caixa.objects.get(usuario_id=request.user.id)
        caixa.saldo_devedor += round(valor_compra, 2)
        caixa.receber += round(valor_venda, 2)
        venda.save()
        caixa.save()
        cliente = Cliente.objects.get(id=cliente_id)
        for produto_id in produtos:
            produto = Produto.objects.get(id=produto_id)
            venda.produtos.add(produto)
        venda.save()
        cliente.saldo_devedor += venda.saldo_devedor
        cliente.saldo_devedor = round(cliente.saldo_devedor, 2)
        cliente.atualizar()
        cliente.save()
        messages.add_message(request, constants.SUCCESS, 'Venda cadastrada com sucesso.')
        return render(request, 'nova_venda.html', {'clientes': cliente_poo, 'produtos': produtos_poo, 'id': id})

@login_required()
def novo_produto(request):
    if request.method == "GET":
        tipos_poo = Tipo.objects.all()
        marcas_poo = Marca.objects.all()
        return render(request, 'novo_produto.html', {'tipos': tipos_poo, 'marcas': marcas_poo})
    elif request.method == "POST":
        nome = request.POST.get("nome").upper()
        marca = request.POST.get("marca")
        tipo = request.POST.get("tipo")
        existe = Produto.objects.filter(nome=nome, marca_id=marca, tipo_id=tipo, usuario_id=request.user.id)
        if len(existe) != 0:
            messages.add_message(request, constants.ERROR, 'Já existe um produto identico cadastrado.')
            return redirect('/home/novo_produto')
        valor_compra = request.POST.get("valor_compra")
        valor_venda = request.POST.get("valor_venda")
        if len(valor_compra) == 0 or len(valor_venda) == 0:
            messages.add_message(request, constants.ERROR, 'Você esqueceu de preencher algum valor.')
            return redirect('/home/novo_produto')
        valor_compra = float(request.POST.get("valor_compra"))
        valor_compra = round(valor_compra, 2)
        valor_venda = float(request.POST.get("valor_venda"))
        valor_venda = round(valor_venda, 2)
        ciclo = request.POST.get("ciclo")
        quantidade = request.POST.get("quantidade")
        #VALIDAR DADOS.
        if len(nome) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return redirect('/home/novo_produto')
        elif marca == None or tipo == None:
            messages.add_message(request, constants.ERROR, 'Nenhuma MARCA ou TIPO cadastrados.')
            return redirect('/home/novo_produto')
        elif valor_compra > 1000 or valor_venda > 1000:
            messages.add_message(request, constants.WARNING, 'Algum dos valores está fora do normal.')
            return redirect('/home/novo_produto')
        lucro = valor_venda - valor_compra
        lucro = round(lucro, 2)
        produto = Produto(
            nome=nome,
            marca_id=marca,
            tipo_id=tipo,
            preco_compra=valor_compra,
            preco_venda=valor_venda,
            ciclo=ciclo,
            lucro=lucro,
            quantidade=quantidade,
            usuario_id=request.user.id,
        )
        produto.save()
        messages.add_message(request, constants.SUCCESS, 'Produto cadastrado com sucesso.')
        return redirect('/home/novo_produto')

@login_required()
def novo_cliente(request):
    if request.method == "GET":
        return render(request, 'novo_cliente.html')
    elif request.method == "POST":
        nome = request.POST.get('nome').upper()
        sobrenome = request.POST.get('sobrenome').upper()
        telefone = request.POST.get('telefone')
        #VALIDAR OS DADOS.
        campos = [nome, sobrenome, telefone]
        for dado in campos:
            if len(dado.strip()) == 0:
                messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
                return render(request, 'novo_cliente.html')
        existe = Cliente.objects.filter(usuario_id=request.user.id, nome=nome, sobrenome=sobrenome)
        if len(existe) != 0:
            messages.add_message(request, constants.ERROR, 'Já existe um cliente com esse nome e sobrenome.')
            return render(request, 'novo_cliente.html')
        cliente = Cliente(usuario=request.user, nome=nome, sobrenome=sobrenome, num_telefone=telefone)
        cliente.save()
        messages.add_message(request, constants.SUCCESS, 'Cliente cadastrado com sucesso.')
        return render(request, 'novo_cliente.html')

@login_required()
def cliente(request):
    if request.method == "GET":
        clientes = Cliente.objects.filter(usuario_id=request.user.id)
        vendas = Venda.objects.all()
        aux = {}
        for c in clientes:
            if c.saldo_devedor != 0:
                aux[c.id] = 0
                for v in vendas:
                    if v.cliente_id == c.id:
                        aux[c.id] += round(v.valor_venda, 2)
                aux[c.id] = round(((aux[c.id] - c.saldo_devedor) / aux[c.id]) * 100)
        return render(request, 'clientes.html', {'clientes': clientes, 'vendas': vendas, 'valores': aux})
    elif request.method == "POST":
        nome = request.POST.get("pesquisar")
        clientes = Cliente.objects.filter(usuario_id=request.user.id)
        vendas = Venda.objects.all()
        aux_clientes = []
        for cliente in clientes:
            if nome.upper() in cliente.nome.upper():
                aux_clientes.append(cliente)
        clientes = aux_clientes
        aux = {}
        for c in clientes:
            if c.saldo_devedor != 0:
                aux[c.id] = 0
                for v in vendas:
                    if v.cliente_id == c.id:
                        aux[c.id] += round(v.valor_venda, 2)
                aux[c.id] = round(((aux[c.id] - c.saldo_devedor) / aux[c.id]) * 100)
        if len(clientes) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'clientes.html', {'clientes': clientes, 'vendas': vendas, 'valores': aux})


@login_required()
def listar_clientes(request):
    if request.method == "GET":
        clientes = Cliente.objects.filter(usuario=request.user)
        return render(request, 'listar_clientes.html', {'clientes': clientes})
    elif request.method == "POST":
        nome = request.POST.get("pesquisar")
        clientes = Cliente.objects.filter(usuario_id=request.user.id)
        aux_clientes = []
        for cliente in clientes:
            if nome.upper() in cliente.nome.upper():
                aux_clientes.append(cliente)
        clientes = aux_clientes
        if len(clientes) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'listar_clientes.html', {'clientes': clientes})

@login_required()
def remover_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    vendas = Venda.objects.filter(cliente_id=id)
    caixa = Caixa.objects.get(usuario_id=request.user.id)
    for venda in vendas:
        caixa.saldo_atual -= round(venda.valor_venda - venda.saldo_devedor)
        caixa.saldo_devedor -= round(venda.valor_compra, 2)
        caixa.receber -= round(venda.saldo_devedor, 2)
    caixa.save()
    if not cliente.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse cliente não é seu.')
        return redirect('/home/listar_clientes')
    cliente.delete()
    messages.add_message(request, constants.SUCCESS, 'Cliente removido com sucesso.')
    return redirect('/home/listar_clientes')

@login_required()
def venda(request):
    if request.method == "GET":
        vendas = Venda.objects.filter(usuario_id=request.user.id, status="A")
        clientes = Cliente.objects.filter(usuario_id=request.user.id)
        aux_vendas = []
        data_atual = datetime.now()
        for venda in vendas:
            vencimento = datetime(venda.data.year, venda.data.month, 1)
            vencimento = vencimento + relativedelta(months=venda.parcelas)
            if data_atual > vencimento:
                aux_vendas.append(venda)
        vendas = aux_vendas
        return render(request, 'vendas.html', {'vendas': vendas, 'clientes': clientes})
    elif request.method == "POST":
        vendas = Venda.objects.filter(usuario_id=request.user.id, status="A")
        clientes = Cliente.objects.filter(usuario_id=request.user.id)
        aux_vendas = []
        data_atual = datetime.now()
        for venda in vendas:
            vencimento = datetime(venda.data.year, venda.data.month, venda.data.day)
            vencimento = vencimento + relativedelta(months=venda.parcelas)
            if data_atual > vencimento:
                aux_vendas.append(venda)
        vendas = aux_vendas
        nome = request.POST.get("pesquisar")
        aux = []
        for venda in vendas:
            cliente = Cliente.objects.get(id=venda.cliente_id)
            if nome.upper() in cliente.nome.upper():
                aux.append(venda)
        vendas = aux
        if len(vendas) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'vendas.html', {'vendas': vendas, 'clientes': clientes})

@login_required()
def listar_vendas(request):
    if request.method == "GET":
        vendas = Venda.objects.filter(usuario=request.user)
        clientes = Cliente.objects.filter(usuario=request.user)
        return render(request, 'listar_vendas.html', {'vendas': vendas, 'clientes': clientes})
    elif request.method == "POST":
        vendas = Venda.objects.filter(usuario=request.user)
        clientes = Cliente.objects.filter(usuario=request.user)
        nome = request.POST.get("pesquisar")
        aux = []
        for venda in vendas:
            cliente = Cliente.objects.get(id=venda.cliente_id)
            if nome.upper() in cliente.nome.upper():
                aux.append(venda)
        vendas = aux
        if len(vendas) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'listar_vendas.html', {'vendas': vendas, 'clientes': clientes})

@login_required()
def remover_venda(request, id):
    venda = Venda.objects.get(id=id)
    cliente = Cliente.objects.get(id=venda.cliente_id)
    if not venda.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Essa venda não é sua.')
        return redirect('/home/listar_vendas')
    caixa = Caixa.objects.get(usuario_id=request.user.id)
    caixa.saldo_atual -= round(venda.valor_venda - venda.saldo_devedor)
    caixa.saldo_devedor -= round(venda.valor_compra, 2)
    caixa.receber -= round(venda.saldo_devedor, 2)
    caixa.save()
    cliente.saldo_devedor -= venda.saldo_devedor
    cliente.saldo_devedor = round(cliente.saldo_devedor, 2)
    cliente.save()
    venda.delete()
    messages.add_message(request, constants.SUCCESS, 'Venda removida com sucesso.')
    return redirect('/home/listar_vendas')

@login_required()
def produto(request):
    if request.method == "GET":
        produtos = Produto.objects.all()
        tipos = Tipo.objects.all()
        marcas = Marca.objects.all()
        return render(request, 'produtos.html',  {'produtos': produtos, 'tipos': tipos,  'marcas': marcas})
    elif request.method == "POST":
        nome = request.POST.get("pesquisar")
        produtos = Produto.objects.all()
        tipos = Tipo.objects.all()
        marcas = Marca.objects.all()
        aux = []
        for produto in produtos:
            if nome.upper() in produto.nome.upper():
                aux.append(produto)
        produtos = aux
        if len(produtos) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'produtos.html', {'produtos': produtos, 'tipos': tipos,  'marcas': marcas})

def gerar_cor_aleatoria():
    import random
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return f'rgb({red}, {green}, {blue})'

@csrf_exempt
def api_pagamentos_por_clientes(request):
    clientes = Cliente.objects.filter(usuario_id=request.user.id)
    pagamentos = Pagamento.objects.all()

    aux_pagamentos = []

    for cliente in clientes:
        aux = 0
        for pagamento in pagamentos:
            if pagamento.cliente_id == cliente.id:
                aux += round(pagamento.valor, 2)
        aux_pagamentos.append(aux)

    # GERAR CORES
    cores_distintas = [gerar_cor_aleatoria() for _ in range(len(clientes))]
    # GERAR CORES

    clientes = [c.nome for c in clientes]
    data = {
        'qtd_pagamentos': aux_pagamentos,
        'labels': clientes,
        'cores': cores_distintas
    }
    return JsonResponse(data)

@csrf_exempt
def api_vendas_por_produtos(request):
    produtos = Produto.objects.all()

    qtd_vendas = []
    qtd_produtos = []
    produtos_aux = []
    vendas = Venda.objects.filter(usuario_id=request.user.id)
    for venda in vendas:
        for p in venda.produtos.all():
            qtd_produtos.append(p)

    for produto in produtos:
        aux = 0
        for pr in qtd_produtos:
            if pr.id == produto.id:
                aux += 1
        if aux != 0:
            produtos_aux.append(produto)
            qtd_vendas.append(aux)

    # GERAR CORES
    cores_distintas = [gerar_cor_aleatoria() for _ in range(len(produtos))]
    # GERAR CORES

    produtos = [p.nome for p in produtos_aux]
    data = {
        'qtd_vendas': qtd_vendas,
        'labels':  produtos,
        'cores': cores_distintas
    }

    return JsonResponse(data)

@csrf_exempt
def api_faturamento_por_mes(request):
    x = Venda.objects.filter(usuario_id=request.user.id)


    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
    data = []
    data2 = []
    labels = []
    cont = 0
    mes = datetime.now().month
    ano = datetime.now().year
    for i in range(12):
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1

        y = sum([i.valor_venda for i in x if i.data.month == mes and i.data.year == ano])
        z = sum([i.lucro for i in x if i.data.month == mes and i.data.year == ano])
        labels.append(meses[mes-1])
        data.append(y)
        data2.append(z)
        cont += 1

    # GERAR CORES
    cores_distintas = [gerar_cor_aleatoria() for _ in range(12)]
    # GERAR CORES

    data_jason = {'data': data[::-1], 'labels': labels[::-1], 'cores': cores_distintas, 'data2': data2[::-1]}

    return JsonResponse(data_jason)

@csrf_exempt
def api_vendas_por_clientes(request):
    vendas = Venda.objects.filter(usuario_id=request.user.id)
    clientes = Cliente.objects.filter(usuario_id=request.user.id)

    cliente_aux = []

    for cliente in clientes:
        aux = 0
        for venda in vendas:
            if venda.cliente_id == cliente.id:
                aux += 1
        cliente_aux.append(aux)

    # GERAR CORES
    cores_distintas = [gerar_cor_aleatoria() for _ in range(len(clientes))]
    # GERAR CORES

    clientes = [c.nome for c in clientes]
    data_venda = {
        'qtd_vendas': cliente_aux,
        'labels': clientes,
        'cores': cores_distintas
    }

    return JsonResponse(data_venda)

@login_required()
def listar_produtos(request):
    if request.method == "GET":
        produto = Produto.objects.all()
        tipos = Tipo.objects.all()
        marcas = Marca.objects.all()
        return render(request, 'listar_produtos.html', {'produtos': produto, 'tipos': tipos,  'marcas': marcas})
    elif request.method == "POST":
        nome = request.POST.get("pesquisar")
        produtos = Produto.objects.all()
        tipos = Tipo.objects.all()
        marcas = Marca.objects.all()
        aux = []
        for produto in produtos:
            if nome.upper() in produto.nome.upper() and produto.usuario_id == request.user.id:
                aux.append(produto)
        produtos = aux
        if len(produtos) == 0 and nome != "":
            messages.add_message(request, constants.ERROR, f'Nenhum resultado para a pesquisa "{nome.upper()}"')
        return render(request, 'listar_produtos.html', {'produtos': produtos, 'tipos': tipos,  'marcas': marcas})

@login_required()
def remover_produto(request, id):
    produto = Produto.objects.get(id=id)
    produto.delete()
    messages.add_message(request, constants.SUCCESS, 'Produto removido com sucesso.')
    return redirect('/home/listar_produtos')

@login_required()
def ver_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    venda = Venda.objects.filter(cliente_id=id)
    pagamento = Pagamento.objects.filter(cliente_id=id)
    return render(request, 'ver_cliente.html', {'cliente': cliente, 'vendas': venda, 'pagamentos': pagamento})

@login_required()
def adicionar_pagamento(request):
    if request.method == "GET":
        return redirect('/home/listar_clientes')
    else:
        id_venda = request.POST.get("id_venda")
        try:
            venda = Venda.objects.get(id=id_venda)
        except:
            messages.add_message(request, constants.ERROR, 'Não existe venda com esse ID.')
            return redirect(f'/home/listar_clientes')
        if len(id_venda) == 0:
            messages.add_message(request, constants.ERROR, 'O ID do pagamento é zero.')
            return redirect(f'/home/listar_clientes')
        venda = Venda.objects.get(id=id_venda)
        cliente = Cliente.objects.get(id=venda.cliente_id)
        valor = request.POST.get("valor")
        if len(valor) == 0:
            messages.add_message(request, constants.ERROR, 'O valor do pagamento é zero.')
            return redirect(f'/home/ver_cliente/{cliente.id}')
        valor = float(request.POST.get("valor"))
        valor = round(valor, 2)
        if valor > venda.saldo_devedor:
            messages.add_message(request, constants.ERROR, 'O valor do pagamento é maior que o saldo devedor da venda.')
            return redirect(f'/home/ver_cliente/{cliente.id}')
        else:
            pagamento = Pagamento(
                usuario=request.user,
                cliente=cliente,
                venda=venda,
                valor=valor
            )
            pagamento.save()
            venda.saldo_devedor -= valor
            venda.saldo_devedor = round(venda.saldo_devedor, 2)
            cliente.saldo_devedor -= valor
            cliente.saldo_devedor = round(cliente.saldo_devedor, 2)
            cliente.atualizar()
            venda.atualizar()
            venda.save()
            cliente.save()
            caixa = Caixa.objects.get(usuario_id=request.user.id)
            caixa.receber -= pagamento.valor
            caixa.receber = round(caixa.receber, 2)
            caixa.saldo_atual += pagamento.valor
            caixa.saldo_atual = round(caixa.saldo_atual, 2)
            caixa.save()
            messages.add_message(request, constants.SUCCESS, f'Pagamento de R${valor} efetuado com sucesso, novo saldo devedor de {cliente.nome} é R${cliente.saldo_devedor}.')
            return redirect(f'/home/ver_cliente/{cliente.id}')

@login_required()
def ver_venda(request, id):
    venda = Venda.objects.get(id=id)
    cliente = Cliente.objects.get(id=venda.cliente_id)
    pagamento = Pagamento.objects.filter(venda_id=id)
    return render(request, 'ver_venda.html', {'cliente': cliente, 'venda': venda, 'venda_produtos': venda.produtos.all(), 'pagamentos': pagamento})

@login_required()
def ver_produto(request, id):
    produto = Produto.objects.get(id=id)
    return render(request, 'ver_produto.html', {'produto': produto})

@login_required()
def remover_pagamento(request, id):
    pagamento = Pagamento.objects.get(id=id)
    cliente = Cliente.objects.get(id=pagamento.cliente_id)
    if not pagamento.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Esse pagamento não é seu.')
        return redirect('/home/listar_clientes')
    else:
        cliente.saldo_devedor += pagamento.valor
        cliente.saldo_devedor = round(cliente.saldo_devedor, 2)
        cliente.save()
        venda = Venda.objects.get(id=pagamento.venda_id)
        venda.saldo_devedor += pagamento.valor
        venda.saldo_devedor = round(venda.saldo_devedor, 2)
        venda.save()
        caixa = Caixa.objects.get(usuario_id=request.user.id)
        caixa.receber += pagamento.valor
        caixa.receber = round(caixa.receber, 2)
        caixa.saldo_atual -= pagamento.valor
        caixa.saldo_atual = round(caixa.saldo_atual, 2)
        caixa.save()
        pagamento.delete()
        messages.add_message(request, constants.SUCCESS, 'Pagamento removido com sucesso.')
        return redirect('/home/listar_clientes')

@login_required()
def editar_cliente(request, id):
    if request.method == "GET":
        cliente = Cliente.objects.get(id=id)
        return render(request, 'editar_cliente.html', {'cliente': cliente})
    elif request.method == "POST":
        nome = request.POST.get('nome').upper()
        sobrenome = request.POST.get('sobrenome').upper()
        telefone = request.POST.get('telefone')
        #VALIDAR OS DADOS.
        campos = [nome, sobrenome, telefone]
        for dado in campos:
            if len(dado.strip()) == 0:
                messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
                return render(request, 'novo_cliente.html')
        cliente_aux = Cliente.objects.get(id=id)
        cliente = Cliente.objects.filter(usuario_id=request.user.id, nome=nome, sobrenome=sobrenome)
        if cliente is not None and cliente_aux.num_telefone == telefone:
            messages.add_message(request, constants.ERROR, 'Já existe um cliente com esse nome e sobrenome.')
            return render(request, 'ver_cliente.html', {'cliente': cliente_aux})
        cliente_aux.nome = nome
        cliente_aux.sobrenome = sobrenome
        cliente_aux.num_telefone = telefone
        cliente_aux.save()
        messages.add_message(request, constants.SUCCESS, 'Cliente editado com sucesso.')
        return redirect(f'/home/ver_cliente/{cliente_aux.id}')

@login_required()
def editar_produto(request, id):
    if request.method == "GET":
        tipos_poo = Tipo.objects.all()
        marcas_poo = Marca.objects.all()
        produto = Produto.objects.get(id=id)
        valor_compra = str(produto.preco_compra)
        valor_venda = str(produto.preco_venda)
        return render(request, 'editar_produto.html', {'tipos': tipos_poo, 'marcas': marcas_poo, 'produto': produto, 'vc': valor_compra, 'vv': valor_venda})
    elif request.method == "POST":
        nome = request.POST.get("nome").upper()
        marca = request.POST.get("marca")
        tipo = request.POST.get("tipo")
        produto = Produto.objects.get(id=id)
        a = Produto.objects.filter(nome=nome, marca_id=marca, tipo_id=tipo)
        if a is not None and produto.id != id:
            messages.add_message(request, constants.ERROR, 'Já existe um produto identico cadastrado.')
            return redirect(f'/home/editar_produto/{produto.id}')
        valor_compra = request.POST.get("valor_compra")
        valor_venda = request.POST.get("valor_venda")
        if len(valor_compra) == 0 or len(valor_venda) == 0:
            messages.add_message(request, constants.ERROR, 'Você esqueceu de preencher algum valor.')
            return redirect('/home/novo_produto')
        valor_compra = float(request.POST.get("valor_compra"))
        valor_compra = round(valor_compra, 2)
        valor_venda = float(request.POST.get("valor_venda"))
        valor_venda = round(valor_venda, 2)
        ciclo = request.POST.get("ciclo")
        quantidade = request.POST.get("quantidade")
        #VALIDAR DADOS.
        if len(nome) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return redirect('/home/novo_produto')
        elif marca == None or tipo == None:
            messages.add_message(request, constants.ERROR, 'Nenhuma MARCA ou TIPO cadastrados.')
            return redirect('/home/novo_produto')
        elif valor_compra > 1000 or valor_venda > 1000:
            messages.add_message(request, constants.WARNING, 'Algum dos valores está fora do normal.')
            return redirect('/home/novo_produto')
        lucro = valor_venda - valor_compra
        lucro = round(lucro, 2)
        produto.nome = nome
        produto.marca_id = marca
        produto.tipo_id = tipo
        produto.preco_compra = valor_compra
        produto.preco_venda = valor_venda
        produto.ciclo = ciclo
        produto.quantidade = quantidade
        produto.lucro = lucro
        produto.save()
        messages.add_message(request, constants.SUCCESS, 'Produto editado com sucesso.')
        return redirect(f'/home/editar_produto/{produto.id}')
