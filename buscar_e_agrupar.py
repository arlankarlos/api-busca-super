import re
from difflib import get_close_matches
from utils.api_sams import buscar_produtos_sams_club
from utils.api_atacadao import buscar_produtos_atacadao
from utils.api_carrefour import buscar_produtos_carrefour
from utils.api_bretas import buscar_produtos_bretas


def agrupar_produtos_similares(produtos: dict, similaridade: float = 0.8) -> dict:
    """
    Agrupa produtos por peso (normalizado em gramas) e categoria usando uma taxa de corte ajustável.

    Args:
        produtos (dict): Dicionário de produtos com seus respectivos preços e lojas.
        similaridade (float): Percentual de similaridade para considerar nomes como semelhantes (0 a 1).

    Returns:
        dict: Dicionário de produtos agrupados por similaridade de categoria e peso (em gramas).
    """
    produtos_agrupados = {}

    for nome, detalhes in produtos.items():
        # Normalizar nome, extrair peso e obter a categoria
        nome_normalizado = normalizar_nome_produto(nome)
        peso_em_gramas = extrair_peso_produto(nome)
        categoria = detalhes.get('categorias', 'Categoria desconhecida')

        # Chave de agrupamento é composta pela categoria e o peso do produto (em gramas)
        chave_agrupamento = f"{nome_normalizado}_{categoria.lower()}_{peso_em_gramas}g"

        # Verificar se existe um produto com a mesma categoria e peso no dicionário de agrupamento
        chave_similar = get_close_matches(
            chave_agrupamento, produtos_agrupados.keys(), n=1, cutoff=similaridade
        )

        if chave_similar:
            # Se encontrar produto com a mesma categoria e peso, adiciona ao grupo existente
            produtos_agrupados[chave_similar[0]].append(detalhes)
        else:
            # Se não encontrar, cria um novo grupo
            produtos_agrupados[chave_agrupamento] = [detalhes]

    return produtos_agrupados


def normalizar_nome_produto(nome):
    """
    Normaliza o nome do produto removendo caracteres especiais, números e palavras irrelevantes.

    Args:
        nome (str): O nome do produto a ser normalizado.

    Returns:
        str: O nome do produto normalizado.
    """
    # Converter para minúsculas e remover caracteres especiais
    nome = nome.lower()

    # Remover números (como pesos) e palavras como "pacote", "com", "g", "kg", "gramas", etc.
    nome = re.sub(r"\d+", "", nome)  # Remove números
    nome = re.sub(
        r"\b(pacote|com|g|kg|gramas|ml|l|unidade|tradicional|forma|na chapa|grãos)\b",
        "",
        nome,
    )  # Remove unidades e palavras irrelevantes
    nome = re.sub(r"\s+", " ", nome).strip()  # Remove espaços extras

    return nome


def extrair_peso_produto(nome):
    """
    Extrai o peso do nome do produto e converte para gramas (g) ou mililitros (ml).

    Args:
        nome (str): O nome do produto do qual o peso será extraído.

    Returns:
        float: O peso do produto em gramas (g) ou mililitros (ml), ou 'Peso desconhecido' se não for encontrado.
    """
    # Procurar por padrões de peso no nome (ex: 500g, 1kg, 2L, 250ml, etc.)
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s?(g|kg|ml|l)', nome.lower())

    if match:
        peso = float(match.group(1).replace(',', '.'))  # Converter o número para float e trocar vírgula por ponto
        unidade = match.group(2)

        # Converter para gramas ou mililitros
        if unidade == 'kg':
            return peso * 1000  # Converter kg para g
        elif unidade == 'g':
            return peso  # Já está em gramas
        elif unidade == 'l':
            return peso * 1000  # Converter litros para ml (consideramos ml como peso líquido)
        elif unidade == 'ml':
            return peso  # Já está em mililitros

    return 'Peso desconhecido'


def buscar_produto(produto):
    """
    Busca o produto em diferentes sites (Sams Club, Atacadão, Carrefour) e agrupa os resultados.

    Args:
        produto (str): Nome do produto a ser buscado.

    Returns:
        list: Lista com os resultados da busca, onde cada item é um dicionário contendo informações do produto.
    """
    # Inicializar lista de produtos
    produtos = []

    # Função auxiliar para adicionar produtos à lista
    def adicionar_produtos(site, lista_produtos):
        for item in lista_produtos:
            nome_produto = item.get('nome_produto')
            preco = item.get('preco')
            ean = item.get('ean')
            marca = item.get('marca')
            imagem_url = item.get('imagem_url')
            categorias = item.get('categorias')

            produtos.append({
                "nome_produto": nome_produto,
                "preco": preco,
                "ean": ean,
                "marca": marca,
                "imagem_url": imagem_url,
                "categorias": categorias,
                "site": site  # Adiciona o nome do site como um campo
            })

    # Tentar buscar em cada site e tratar exceções em caso de erro
    try:
        adicionar_produtos("Sams Club", buscar_produtos_sams_club(produto))
    except Exception as e:
        print(f"Erro ao buscar no Sams Club: {e}")

    try:
        adicionar_produtos("Atacadão", buscar_produtos_atacadao(produto))
    except Exception as e:
        print(f"Erro ao buscar no Atacadão: {e}")

    try:
        adicionar_produtos("Carrefour", buscar_produtos_carrefour(produto))
    except Exception as e:
        print(f"Erro ao buscar no Carrefour: {e}")

    try:
        adicionar_produtos("Bretas", buscar_produtos_bretas(produto))
    except Exception as e:
        print(f"Erro ao buscar no Bretas: {e}")

    return produtos  # Retorna uma lista de dicionários



# # Exemplo de uso:
# produto = input("Digite o nome do produto que deseja buscar: ")
# similaridade = float(input("Digite o nível de similaridade desejado (0 a 1): "))

# # Busca o produto nos sites e agrupa resultados similares
# resultado = buscar_produto(produto)
# produtos_agrupados = agrupar_produtos_similares(resultado, similaridade)

# # Exibe os resultados agrupados
# for chave_agrupamento, grupos in produtos_agrupados.items():
#     print(f"Produto: {chave_agrupamento}")
#     for grupo in grupos:
#         for site, detalhes in grupo.items():
#             print(f"  {site}:")
#             print(f"    Produto: {detalhes['nome_produto']}")
#             preco = detalhes.get('preco')
#             if preco is not None:
#                 print(f"    Preço: R$ {preco:.2f}")
#             else:
#                 print("    Preço: Não disponível")
#             print(f"    Marca: {detalhes['marca']}")
#             print(f"    Categoria: {detalhes['categorias']}")
#     print("-" * 50)
