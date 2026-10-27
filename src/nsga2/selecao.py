"""Seleção do NSGA-II baseada em rank e distância de multidão (crowding distance)"""
import random

def torneio_por_multidao(
    ranks: list[int], multidao: list[float], gerador: random.Random) -> int:
    """
    Torneio binário com o Crowded-Comparison Operator.
    """
    # Escolhe dois indivíduos ao acaso para lutar pela vaga de reprodução
    i, j = gerador.sample(range(len(ranks)), 2)
    
    #  Fronteira de Pareto
    if ranks[i] != ranks[j]:
        return i if ranks[i] < ranks[j] else j
        
    # Crowding Distance
    if multidao[i] != multidao[j]:
        return i if multidao[i] > multidao[j] else j
        
    # Desempate absoluto aleatório
    return gerador.choice((i, j))


def selecao_ambiental(
    frentes: list[list[int]], multidao: list[float], tamanho_alvo: int
) -> list[int]:
    """
    Realiza o corte de Elitismo. 
    Lota a próxima geração preenchendo as vagas fronteira por fronteira.
    """
    selecionados: list[int] = []
    
    for frente in frentes:
        # Se as vagas acabaram, para a seleção
        if len(selecionados) >= tamanho_alvo:
            break
            
        # Se a fronteira inteira couber nas vagas restantes, adiciona todos
        if len(selecionados) + len(frente) <= tamanho_alvo:
            selecionados.extend(frente)
        else:
            # Se a fronteira é maior que as vagas restantes, ocorre o truncamento.
            ordenada = sorted(frente, key=lambda idx: multidao[idx], reverse=True)
            selecionados.extend(ordenada[: tamanho_alvo - len(selecionados)])
            
    return selecionados