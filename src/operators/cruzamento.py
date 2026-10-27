"""Cruzamento para rotas codificadas como permutação de cidades"""
import random
from .contratos import Rota

def cruzamento_ox(
        pai_a: Rota, pai_b: Rota, gerador: random.Random) -> tuple[Rota, Rota]:
    """
    Order Crossover (OX): gera dois filhos que continuam sendo permutações.
    """
    tamanho = len(pai_a)
    if tamanho < 2:
        return pai_a[:], pai_b[:]
        
    # Sorteia os índices que vão definir o "miolo" copiado intacto do pai
    inicio, fim = sorted(gerador.sample(range(tamanho), 2))
    
    return(
        _filho_ox(pai_a, pai_b, inicio, fim),
        _filho_ox(pai_b, pai_a, inicio, fim)
    )

def _filho_ox(doador: Rota, complemento: Rota, inicio: int, fim: int)-> Rota:
    tamanho = len(doador)
    filho: list[int | None] = [None] * tamanho
    
    # Copia o trecho do doador (Pai A) exatamente na mesma posição
    filho[inicio: fim +1] = doador[inicio: fim +1]
    herdadas = set(doador[inicio: fim +1])
    
    # Pega as cidades do Pai B que ainda não estão no filho, respeitando a ordem circular
    restantes = [c for c in complemento[fim + 1:] + complemento[: fim+1] if c not in herdadas]
    
    # Define onde existem buracos no filho para encaixar as cidades restantes
    posicoes_livres = list(range(fim +1, tamanho)) + list(range(0, inicio))
    
    for posicao, cidade in zip(posicoes_livres, restantes):
        filho[posicao] = cidade
        
    return filho