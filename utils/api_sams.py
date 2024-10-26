import requests
import base64
import json
from utils.clean_input import clean_input

# URL da API GraphQL do Sams Club
url = "https://www.samsclub.com.br/_v/segment/graphql/v1"


def buscar_produtos_sams_club(produto):
    """
    Faz uma requisição à API do Sams Club para buscar produtos com base em um termo de pesquisa.

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

    Raises:
        ValueError: Se a resposta da API não puder ser convertida para JSON.

    Exemplo de uso:
    >>> produtos_encontrados = buscar_produtos_sams_club("leite condensado")
    >>> for produto in produtos_encontrados:
    >>>     print(f"Produto: {produto['nome_produto']}")
    >>>     print(f"Preço: R$ {produto['preco']:.2f}")
    >>>     print(f"Marca: {produto['marca']}")
    >>>     print(f"Link: {produto['link']}")
    >>>     print(f"Categorias: {produto['categorias']}")
    >>>     print(f"EAN: {produto['ean']}")
    >>>     print(f"Peso: {produto['peso']}")
    >>>     print(f"Embalagem: {produto['embalagem']}")
    >>>     print("-" * 50)

    Observações:
    - A função faz uma requisição POST para a API GraphQL do Sams Club e retorna uma lista com os produtos encontrados.
    - A função limpa a entrada do termo de pesquisa e adapta o payload da requisição.
    """
    # Decodificar o valor Base64 original do campo "variables"
    encoded_variables = "eyJwcm9kdWN0T3JpZ2luVnRleCI6ZmFsc2UsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJoaWRlVW5hdmFpbGFibGVJdGVtcyI6ZmFsc2UsImFkdmVydGlzZW1lbnRPcHRpb25zIjp7InNob3dTcG9uc29yZWQiOnRydWUsInNwb25zb3JlZENvdW50IjoyLCJyZXBlYXRTcG9uc29yZWRQcm9kdWN0cyI6ZmFsc2UsImFkdmVydGlzZW1lbnRQbGFjZW1lbnQiOiJhdXRvY29tcGxldGUifSwiZnVsbFRleHQiOiJhcnJveiIsImNvdW50IjozLCJzaGlwcGluZ09wdGlvbnMiOltdLCJ2YXJpYW50IjpudWxsfQ=="
    # Clean the input
    produto = clean_input(produto)
    # Decodificar de Base64 para JSON
    decoded_variables = base64.b64decode(encoded_variables).decode("utf-8")
    variables = json.loads(decoded_variables)

    # Modificar o termo da pesquisa
    variables["fullText"] = produto

    # Payload para a requisição
    payload = {
        "operationName": "productSuggestions",
        "variables": variables,
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "323b66ebea3c8157a59a448e1e702b955910a82d5751b67a045527bd35c55fc0",
                "sender": "vtex.store-resources@0.x",
                "provider": "vtex.search-graphql@0.x",
            }
        },
    }

    # Cabeçalhos da requisição
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"https://www.samsclub.com.br/{produto}?_q={produto}&map=ft",
        "Cookie": "VtexWorkspace=master%3A-; _ga=GA1.1.1437265494.1729109939; etc...",
    }
    # Enviar a requisição POST para o GraphQL com os parâmetros
    response = requests.post(url, headers=headers, json=payload)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        try:
            data = response.json()
            produtos = (
                data.get("data", {}).get("productSuggestions", {}).get("products", [])
            )

            # Lista para armazenar os produtos e preços
            resultados = []

            if produtos:
                for produto in produtos:
                    # Extrair nome do produto
                    nome_produto = produto.get("productName", "Null")

                    # Extrair preço
                    preco = produto["items"][0]["sellers"][0]["commertialOffer"].get(
                        "Price", "Null"
                    )

                    # Extrair URL da imagem
                    imagem_url = produto["items"][0]["images"][0]["imageUrl"]

                    # Extrair marca
                    marca = produto.get("brand", "Null")

                    # Extrair link do produto
                    link_produto = produto.get("link", "Null")

                    # Extrair categorias
                    categorias = produto.get("categories", [])

                    # Extrair EAN (referência do produto)
                    ean = produto["items"][0].get("ean", "Null")

                    # Extrair especificações (peso e embalagem)
                    especificacoes = produto.get("specificationGroups", [])

                    # Inicializar valores padrão
                    peso = "Null"
                    embalagem = "Null"

                    # Procurar pelas especificações de peso e embalagem
                    for grupo in especificacoes:
                        for especificacao in grupo.get("specifications", []):
                            if especificacao.get("name") == "Peso":
                                peso = especificacao.get("values", ["Null"])[0]
                            elif especificacao.get("name") == "Embalagem":
                                embalagem = especificacao.get("values", ["Null"])[0]
                    categoria = clean_input(categorias[-1])

                    # Adicionar as informações extraídas na lista de resultados
                    resultados.append(
                        {
                            "nome_produto": nome_produto,
                            "preco": preco,
                            "marca": marca,
                            # "link": link_produto,
                            "ean": ean,
                            # "peso": peso,
                            "imagem_url": imagem_url,
                            "categorias": categoria,
                            # "embalagem": embalagem,
                        }
                    )

                return resultados
            else:
                return []
        except ValueError:
            print("A resposta não está no formato JSON.")
            return []
    else:
        print(f"Erro ao acessar a API: {response.status_code}")
        return []


# # Exemplo de uso da função
# produtos_encontrados = buscar_produtos_sams_club("banana")

# for produto in produtos_encontrados:
#     print(f"Produto: {produto['nome_produto']}")
#     print(f"Preço: R$ {produto['preco']:.2f}")
#     print(f"Marca: {produto['marca']}")
#     print(f"Link: {produto['link']}")
#     print(f"Categorias: {clean_input(produto['categorias'][-1])}")
#     print(f"EAN: {produto['ean']}")
#     print(f"Peso: {produto['peso']}")
#     print(f"Embalagem: {produto['embalagem']}")
#     print("-" * 50)
# # print(produtos_encontrados[0])
