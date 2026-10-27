"""Mutações para rotas codificadas como permutação de cidades"""
import random
from .contratos import Rota

def mutacao_troca(rota: Rota, gerador: random.Random)-> Rota:
    """
    Troca duas cidades de posição aleatoriamente (Swap).
    Introduz ruído simples para evitar que o algoritmo fique preso em mínimos locais.
    """
    filho = rota[:]
    if len(filho)< 2:
        return filho
    i, j = gerador.sample(range(len(filho)), 2)
    filho[i], filho[j] = filho[j], filho[i]
    return filho

def mutacao_inversao(rota: Rota, gerador: random.Random)-> Rota:
    """
    Inverte um segmento da rota (Operador 2-opt).
    
    Em grafos esparsos/incompletos, a inversão é muito superior à troca. 
    Quando invertemos um trecho, todas as estradas internas daquele trecho continuam
    existindo, apenas passamos por elas na contramão. Isso cria rotas novas sem destruir
    a factibilidade das conexões que o algoritmo já encontrou.
    """
    filho = rota[:]
    if len(filho)< 2:
        return filho
    i, j = sorted(gerador.sample(range(len(filho)), 2))
    filho[i: j +1] = reversed(filho[i: j +1])
    return filho

def mutar(rota: Rota, gerador: random.Random)-> Rota:
    """
    O algoritmo decide com 50% de chance se vai usar a Troca ou a Inversão,
    aproveitando os benefícios estruturais de ambas as abordagens.
    """
    operador = gerador.choice((mutacao_inversao, mutacao_troca))
    return operador(rota, gerador)