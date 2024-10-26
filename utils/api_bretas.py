import requests
import base64
import json
from utils.clean_input import clean_input

# URL da API GraphQL
url = "https://www.bretas.com.br/_v/segment/graphql/v1"

# Cabeçalhos da requisição
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "cookie": "COOKIES_AQUI",  # Substituir pelos cookies necessários
    "dnt": "1",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

def substituir_fulltext(produto, variables_encoded):
    # Decodificar o Base64 para JSON
    decoded_vars = base64.b64decode(variables_encoded).decode("utf-8")
    
    # Converter a string JSON em dicionário Python
    variables_dict = json.loads(decoded_vars)
    
    # Substituir o valor do campo "fullText"
    variables_dict["fullText"] = produto
    
    # Converter o dicionário de volta para JSON e então para Base64
    updated_vars = json.dumps(variables_dict)
    updated_vars_encoded = base64.b64encode(updated_vars.encode("utf-8")).decode("utf-8")
    
    return updated_vars_encoded

def buscar_produtos_bretas(produto, url=url, headers=headers):
    """Função para buscar produtos no site do Bretas usando GraphQL"""

    # Limpar a entrada
    produto = clean_input(produto)

    # A string original de variables codificada em Base64
    original_variables = "eyJwcm9kdWN0T3JpZ2luVnRleCI6ZmFsc2UsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwiZnVsbFRleHQiOiJhcnJveiIsImNvdW50Ijo0LCJzaGlwcGluZ09wdGlvbnMiOltdLCJ2YXJpYW50IjpudWxsfQ=="
    
    # Substituir o termo "arroz" pelo produto desejado, como "banana"
    updated_variables = substituir_fulltext(produto, original_variables)

    # Payload da requisição GraphQL, com as variáveis atualizadas
    payload = {
        "workspace": "master",
        "maxAge": "medium",
        "appsEtag": "remove",
        "domain": "store",
        "locale": "pt-BR",
        "__bindingId": "cf09c6b8-4837-488f-b744-47f2b52bb2c4",
        "operationName": "productSuggestions",
        "variables": {"term": produto},  # Passando o termo de busca corretamente
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "323b66ebea3c8157a59a448e1e702b955910a82d5751b67a045527bd35c55fc0",
                "sender": "vtex.store-resources@0.x",
                "provider": "vtex.search-graphql@0.x",
            },
            "variables": updated_variables,  # Usando a string Base64 atualizada
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

        def processar_produtos(data):
            resultados = []

            # Percorrer os produtos no JSON
            produtos = (
                data.get("data", {}).get("productSuggestions", {}).get("products", [])
            )

            for produto in produtos:
                nome_produto = produto.get("productName", "Nome não disponível")
                categorias = produto.get("categories", ["Categoria não disponível"])
                marca = produto.get("brand", "Marca não disponível")
                ean = None
                imagem_url = None
                preco = None
                peso = "Peso não disponível"
                embalagem = "Embalagem não disponível"
                especificacoes = produto.get("specificationGroups", [])

                # Procurar o primeiro item (SKU) para extrair detalhes
                if produto.get("items"):
                    item = produto["items"][0]

                    # EAN
                    ean = item.get("ean", "EAN não disponível")

                    # Imagem do produto
                    imagens = item.get("images", [])
                    if imagens:
                        imagem_url = imagens[0].get("imageUrl", "Imagem não disponível")

                    # Preço
                    sellers = item.get("sellers", [])
                    if sellers:
                        preco = (
                            sellers[0]
                            .get("commertialOffer", {})
                            .get("Price", "Preço não disponível")
                        )

                # Procurar pelas especificações de peso e embalagem
                for grupo in especificacoes:
                    for especificacao in grupo.get("specifications", []):
                        if especificacao.get("name") == "Peso":
                            peso = especificacao.get("values", ["Peso não disponível"])[
                                0
                            ]
                        elif especificacao.get("name") == "Embalagem":
                            embalagem = especificacao.get(
                                "values", ["Embalagem não disponível"]
                            )[0]

                categoria = clean_input(categorias[-1])

                # Adicionar as informações extraídas na lista de resultados
                resultados.append(
                    {
                        "nome_produto": nome_produto,
                        "preco": preco,
                        "marca": marca,
                        "ean": ean,
                        "imagem_url": imagem_url,
                        "categorias": categoria,
                        "peso": peso,
                        "embalagem": embalagem,
                    }
                )

            return resultados

        # Processa e retorna os produtos
        return processar_produtos(data)

    else:
        print(f"Erro ao acessar a API: {response.status_code}")
        print(response.text)  # Exibir o conteúdo da resposta em caso de erro
        return []


# # Testando a busca por "banana"
# produtos = buscar_produtos_bretas("banana")

# # Verifica se há resultados
# if produtos:
#     for produto in produtos:
#         print(f"Nome: {produto['nome_produto']}")
#         print(f"Preço: R$ {produto['preco']:.2f}")
#         print(f"Marca: {produto['marca']}")
#         print(f"EAN: {produto['ean']}")
#         print(f"Imagem: {produto['imagem_url']}")
#         print(f"Categorias: {clean_input(produto['categorias'])}")
#         print("-" * 50)  # Separador para cada produto
# else:
#     print("Nenhum produto encontrado.")

