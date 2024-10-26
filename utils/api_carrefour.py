import requests
from utils.clean_input import clean_input

# URL da API GraphQL
url = "https://mercado.carrefour.com.br/api/graphql"

# Cabeçalhos da requisição
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://mercado.carrefour.com.br/",
    "Cookie": "seus_cookies_aqui",
}


def buscar_produtos_carrefour(produto, url=url, headers=headers):
    """
    Busca produtos na API do Carrefour usando uma consulta GraphQL.

    Args:
        produto (str): O termo de pesquisa do produto a ser buscado.
        url (str): A URL da API do Carrefour.
        headers (dict): O cabeçalho da requisição, contendo informações como API keys e Content-Type.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um produto e contém as seguintes informações:
            - id (str): Identificador único do produto.
            - slug (str): Slug amigável do produto, utilizado em URLs.
            - nome (str): Nome do produto.
            - sku (str): Código SKU do produto.
            - ean (str): Código EAN/GTIN do produto.
            - marca (str): Nome da marca do produto.
            - preco (float): Preço do produto.
            - vendedor (str): Nome do vendedor.
            - quantidade_disponivel (int): Quantidade disponível do produto.
            - parcelamento (list): Lista de opções de parcelamento, contendo:
                - payment_method (str): Nome do método de pagamento.
                - installment_value (float): Valor de cada parcela.
                - installment_count (int): Número de parcelas disponíveis.
            - imagens (list): Lista de URLs das imagens do produto.
            - breadcrumb (list): Trilha de navegação para o produto, com cada item sendo um dicionário contendo:
                - name (str): Nome da categoria.
                - position (int): Posição na hierarquia de categorias.

    Exemplo de retorno:
    [
        {
            "id": "8390",
            "slug": "azeite-portugues-oliva-andorinha-500ml-8278474-8390",
            "nome": "Azeite Português Oliva Andorinha 500ml",
            "sku": "8390",
            "ean": "8278474",
            "marca": "Andorinha",
            "preco": 52.99,
            "vendedor": "Carrefour",
            "quantidade_disponivel": 10000,
            "parcelamento": [
                {"payment_method": "American Express", "installment_value": 52.99, "installment_count": 1},
                {"payment_method": "Visa", "installment_value": 52.99, "installment_count": 1},
                # ...
            ],
            "imagens": [
                "https://carrefourbrfood.vtexassets.com/arquivos/ids/7754109/azeite-portugues-tradicional-andorinha-500ml-1.jpg"
            ],
            "breadcrumb": [
                {"name": "Mercearia", "position": 1},
                {"name": "Azeite, Óleo e Vinagre", "position": 2},
                {"name": "Azeites", "position": 3}
            ]
        },
        # Outros produtos...
    ]
    """

    # Clean the input
    produto = clean_input(produto)

    # Payload da requisição GraphQL, agora com o produto como parâmetro
    payload = {
        "operationName": "ProductsQuery",
        "variables": {
            "isPharmacy": False,
            "first": 20,
            "after": "0",
            "sort": "score_desc",
            "term": produto,  # Usando o termo do produto passado como parâmetro
            "selectedFacets": [
                {
                    "key": "channel",
                    "value": '{"salesChannel":2,"regionId":"v2.F05A3DA1C76D4CCCAFB4EBFB21F46381"}',
                },
                {"key": "locale", "value": "pt-BR"},
                {"key": "region-id", "value": "v2.F05A3DA1C76D4CCCAFB4EBFB21F46381"},
            ],
        },
    }

    # Enviar a requisição POST para o GraphQL
    response = requests.post(url, json=payload, headers=headers)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        try:
            data = response.json()  # Tentar converter a resposta em JSON
        except ValueError:
            print("A resposta não está no formato JSON.")
            return []

        # Função interna para processar e retornar os dados dos produtos
        def processar_produtos(data):
            products = (
                data.get("data", {})
                .get("search", {})
                .get("products", {})
                .get("edges", [])
            )
            resultado = []

            for product in products:
                node = product.get("node", {})

                # Extração de informações
                # product_id = node.get("id", "ID não encontrado")
                # slug = node.get("slug", "Slug não encontrado")
                name = node.get("name", "Nome não encontrado")
                # sku = node.get("sku", "SKU não encontrado")
                ean = node.get("gtin", "EAN não encontrado")
                brand = node.get("brand", {}).get("brandName", "Marca não encontrada")

                # Preço e vendedores
                first_offer = node.get("offers", {}).get("offers", [])
                if first_offer:
                    offer = first_offer[0]
                    price = offer.get("price", "Preço não encontrado")
                    # seller_name = offer.get("seller", {}).get(
                    #     "identifier", "Vendedor não encontrado"
                    # )
                    # available_quantity = offer.get(
                    #     "quantity", "Quantidade não encontrada"
                    # )
                else:
                    price = "Preço não encontrado"
                    # seller_name = "Vendedor não encontrado"
                    # available_quantity = "Quantidade não encontrada"

                # Parcelamento
                installments = (
                    node.get("offers", {}).get("offers", [])[0].get("Installments", [])
                )
                installment_options = []
                for installment in installments:
                    installment_options.append(
                        {
                            "payment_method": installment.get(
                                "PaymentSystemName", "Método não encontrado"
                            ),
                            "installment_value": installment.get("Value", 0),
                            "installment_count": installment.get(
                                "NumberOfInstallments", 0
                            ),
                        }
                    )

                # Imagens do produto
                images = node.get("image", [])
                image_urls = [img.get("url", "") for img in images]

                # Breadcrumb (trilha de navegação)
                breadcrumb = node.get("breadcrumbList", {}).get("itemListElement", [])
                breadcrumb_list = [
                    {"name": item.get("name", ""), "position": item.get("position", 0)}
                    for item in breadcrumb
                ]
                categoria = clean_input(breadcrumb_list[0]['name'])
                # Adiciona todas as informações relevantes ao resultado
                resultado.append(
                    {
                        # "id": product_id,
                        # "slug": slug,
                        "nome_produto": name,
                        "preco": price,
                        "marca": brand,
                        # "sku": sku,
                        "ean": ean,
                        # "vendedor": seller_name,
                        # "quantidade_disponivel": available_quantity,
                        # "parcelamento": installment_options,
                        "imagem_url": image_urls[0],
                        "categorias": categoria,
                    }
                )

            return resultado

        # Processa e retorna os produtos
        return processar_produtos(data)

    else:
        print(f"Erro ao acessar a API: {response.status_code}")
        print(response.text)  # Exibir o conteúdo da resposta em caso de erro
        return []


# # Exemplo de uso da função buscar_produtos_carrefour
# produtos = buscar_produtos_carrefour("banana prata")

# # Verifica se há resultados
# if produtos:
#     for produto in produtos:
#         print(f"ID do Produto: {produto['id']}")
#         print(f"Slug: {produto['slug']}")
#         print(f"Nome: {produto['nome_produto']}")
#         print(f"SKU: {produto['sku']}")
#         print(f"EAN: {produto['ean']}")
#         print(f"Marca: {produto['marca']}")
#         print(f"Preço: R$ {produto['preco']:.2f}")
#         print(f"Vendedor: {produto['vendedor']}")
#         print(f"Quantidade Disponível: {produto['quantidade_disponivel']}")

#         # # Exibe as opções de parcelamento
#         # print("Opções de Parcelamento:")
#         # for parcela in produto["parcelamento"]:
#         #     print(
#         #         f"  - {parcela['payment_method']}: {parcela['installment_count']}x de R$ {parcela['installment_value']:.2f}"
#         #     )

#         # # Exibe URLs das imagens
#         # print("Imagens do Produto:")
#         # for imagem in produto["imagens"]:
#         #     print(f"  - {imagem}")

#         # Exibe a trilha de navegação (breadcrumb)
#         # print("Breadcrumb (Trilha de Navegação):")
#         # for breadcrumb in produto["categorias"]:
#         #     print(f"  - {categorias['position']}: {categorias['name']}")
#         print(f"Categorias: {clean_input(produto['categorias'][0]['name'])}" )
#         print("-" * 50)  # Separador para cada produto
# else:
#     print("Nenhum produto encontrado.")
