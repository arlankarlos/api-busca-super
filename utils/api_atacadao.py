import requests
from utils.clean_input import clean_input


# Função que busca produtos no Atacadão
def buscar_produtos_atacadao(produto):
    """
    Faz uma requisição à API do Atacadão para buscar produtos com base no termo de pesquisa.

    Args:
        produto (str): O termo de pesquisa do produto a ser buscado.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário contém as seguintes informações de um produto:
            - nome_produto (str): O nome do produto.
            - preco (float): O preço do produto.
            - marca (str): A marca do produto.
            - link (str): O link para a página do produto.
            - categorias (list): Uma lista de categorias às quais o produto pertence.
            - ean (str): O código EAN do produto.
            - peso (str): O peso do produto.
            - embalagem (str): A embalagem do produto.
            - vendedores (list): Lista de vendedores, com preço e condições de pagamento.
            - parcelamento (list): Lista de opções de parcelamento.

    Exemplo de uso:
    >>> produtos_encontrados = buscar_produtos_atacadao("arroz")
    >>> for produto in produtos_encontrados:
    >>>     print(f"Produto: {produto['nome_produto']}")
    >>>     print(f"Preço: R$ {produto['preco']:.2f}")
    >>>     print(f"Marca: {produto['marca']}")
    >>>     print(f"Link: {produto['link']}")
    >>>     print(f"Categorias: {produto['categorias']}")
    >>>     print(f"EAN: {produto['ean']}")
    >>>     print(f"Peso: {produto['peso']}")
    >>>     print(f"Embalagem: {produto['embalagem']}")
    >>>     print(f"Vendedores: {produto['vendedores']}")
    >>>     print(f"Parcelamento: {produto['parcelamento']}")
    >>>     print('-' * 50)
    """

    # Clean the input
    produto = clean_input(produto)
    # URL da API GraphQL
    url = "https://www.atacadao.com.br/api/graphql"

    # Payload da requisição GraphQL com o termo de pesquisa ajustado
    payload = {
        "operationName": "ProductsQuery",
        "variables": {
            "first": 20,
            "after": "0",
            "sort": "score_desc",
            "term": produto,  # Produto recebido como parâmetro
            "selectedFacets": [
                {
                    "key": "channel",
                    "value": '{"salesChannel":"1","seller":"atacadaobr817","regionId":"U1cjYXRhY2FkYW9icjgxNw=="}',
                },
                {"key": "locale", "value": "pt-BR"},
            ],
        },
    }

    # Cabeçalhos da requisição
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"https://www.atacadao.com.br/s?q={produto}&sort=score_desc&page=0&ae=historical_search",
        "Cookie": "checkout.vtex.com=__ofid=68f3a5d309b7413e8a4fdea674c08c76; ...",  # Cookies da sessão
    }

    # Enviar a requisição POST para o GraphQL
    response = requests.post(url, json=payload, headers=headers)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        try:
            data = response.json()  # Converter a resposta para JSON
            return process_products(data)  # Retornar os produtos processados
        except ValueError:
            print("A resposta não está no formato JSON.")
            return []
    else:
        print(f"Erro ao acessar a API: {response.status_code}")
        return []


# Função para processar e retornar informações dos produtos
def process_products(data):
    """
    Processa os dados retornados pela API e extrai informações dos produtos.

    Args:
        data (dict): Dados brutos retornados pela API.

    Returns:
        list: Lista de dicionários com as informações dos produtos.
    """
    products = (
        data.get("data", {}).get("search", {}).get("products", {}).get("edges", [])
    )
    result = []

    for product in products:
        node = product.get("node", {})

        # Extrair informações principais do produto
        nome_produto = node.get("name", "Nome não encontrado")
        ean = node.get("gtin", "EAN não disponível")
        marca = node.get("brand", {}).get("brandName", "Marca não disponível")
        link = node.get("slug", "")
        link_produto = f"https://www.atacadao.com.br/{link}"
        categorias = [
            cat.get("name", "Categoria não disponível")
            for cat in node.get("breadcrumbList", {}).get("itemListElement", [])
        ]

        # Imagem do produto
        imagem_url = node.get("image", [{}])[0].get("url", "Imagem não disponível")

        # Ofertas e vendedores
        offers = node.get("offers", {}).get("offers", [])
        vendedores = []
        for offer in offers:
            vendedor = offer.get("seller", {}).get(
                "identifier", "Vendedor não disponível"
            )
            preco = offer.get("price", "Preço não disponível")
            vendedores.append({"vendedor": vendedor, "preco": preco})

        # Parcelamento
        parcelamento = (
            node.get("sellers", [{}])[0]
            .get("commertialOffer", {})
            .get("Installments", [])
        )
        opcoes_parcelamento = []
        for p in parcelamento:
            metodo_pagamento = p.get("PaymentSystemName", "Método não disponível")
            parcelas = p.get("NumberOfInstallments", 1)
            valor_parcela = p.get("Value", 0)
            opcoes_parcelamento.append(
                {
                    "metodo_pagamento": metodo_pagamento,
                    "parcelas": parcelas,
                    "valor_parcela": valor_parcela,
                }
            )
        categoria = clean_input(categorias[0])
        # Adicionar todas as informações relevantes ao resultado
        result.append(
            {
                "nome_produto": nome_produto,
                "preco": preco, # type: ignore
                "marca": marca,
                # "link": link_produto,
                "ean": ean,
                "imagem_url": imagem_url,
                "categorias": categoria,
                # "vendedores": vendedores,
                # "parcelamento": opcoes_parcelamento,
            }
        )

    return result




# # Exemplo de uso da função
# produtos_encontrados = buscar_produtos_atacadao("uva")
# for produto in produtos_encontrados:
#     print(f"Produto: {produto['nome_produto']}")
#     print(f"Preço: R$ {produto['preco']}")
#     print(f"Marca: {produto['marca']}")
#     # print(f"Link: {produto['link']}")
#     print(f"Categorias: {clean_input(produto['categorias'][0])}")
#     print(f"EAN: {produto['ean']}")
#     print(f"Imagem: {produto['imagem_url']}")
#     # print(f"Vendedores: {produto['vendedores']}")
#     # print(f"Parcelamento: {produto['parcelamento']}")
#     print("-" * 50)
