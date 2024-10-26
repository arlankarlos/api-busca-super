"""função para trocar as letras especiais por letras comuns,
retirar os acentos e remover os simbolos especiais

biblioteca unicodedata
biblioteca unidecode
biblioteca re
"""
import unicodedata
import re
from unidecode import unidecode
# a função recebe uma string e retorna a string
# sem acentos, sem simbolos especias

def clean_input(input_string: str) -> str:
    # trocando as letras especiais por letras comuns
    input_string = unidecode(input_string)
    # retirando os acentos
    input_string = unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('ASCII')
    # retirando os simbolos especiais
    input_string = re.sub(r'[^\w\s]', '', input_string)
    # retornando a string
    return input_string.lower()

# print(clean_input("áéíóúçãõ"))