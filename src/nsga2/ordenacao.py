"""Dominância de Pareto, ordenação não dominada e distância de multidão.

Essas funções são o núcleo multiobjetivo do NSGA-II. Elas são injetadas em
``NSGA2`` como ``ordenar_fn`` e ``multidao_fn`` (ver ``algoritmo.py``).

Todos os objetivos são minimizados. Um indivíduo é identificado pelo seu índice
na lista de objetivos recebida.
"""

from collections.abc import Sequence
from math import inf

Objetivos = Sequence[tuple[float, float]]


def domina(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """Diz se ``a`` domina ``b`` no sentido de Pareto (minimização).

    ``a`` domina ``b`` quando não é pior em nenhum objetivo e é estritamente
    melhor em pelo menos um.
    """
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def domina_com_restricao(
    objetivos_a: tuple[float, float],
    violacoes_a: int,
    objetivos_b: tuple[float, float],
    violacoes_b: int,
) -> bool:
    """Dominância com tratamento de restrições (Deb et al., 2002).

    - Entre duas soluções factíveis, vale a dominância de Pareto.
    - Uma solução factível sempre domina uma infactível.
    - Entre duas infactíveis, a que tem menos violações domina.
    """
    if violacoes_a == 0 and violacoes_b == 0:
        return domina(objetivos_a, objetivos_b)
    return violacoes_a < violacoes_b


def ordenar_nao_dominados(
    objetivos: Objetivos, violacoes: Sequence[int]
) -> list[list[int]]:
    """Separa a população em frentes de não dominância (fast non-dominated sort).

    Args:
        objetivos: ``(distancia, pedagio)`` de cada indivíduo.
        violacoes: número de trechos inexistentes de cada indivíduo.

    Returns:
        Lista de frentes. ``frentes[0]`` contém os índices não dominados,
        ``frentes[1]`` os que só são dominados pela frente 0, e assim por diante.

    Complexidade: O(M · N²), com M objetivos e N indivíduos.
    """
    if len(objetivos) != len(violacoes):
        raise ValueError("objetivos e violacoes devem ter o mesmo tamanho")

    n = len(objetivos)
    dominados_por: list[list[int]] = [[] for _ in range(n)]
    contagem = [0] * n  # quantos indivíduos dominam cada um

    for p in range(n):
        for q in range(p + 1, n):
            if domina_com_restricao(
                objetivos[p], violacoes[p], objetivos[q], violacoes[q]
            ):
                dominados_por[p].append(q)
                contagem[q] += 1
            elif domina_com_restricao(
                objetivos[q], violacoes[q], objetivos[p], violacoes[p]
            ):
                dominados_por[q].append(p)
                contagem[p] += 1

    frentes = [[i for i in range(n) if contagem[i] == 0]]
    while frentes[-1]:
        proxima: list[int] = []
        for p in frentes[-1]:
            for q in dominados_por[p]:
                contagem[q] -= 1
                if contagem[q] == 0:
                    proxima.append(q)
        frentes.append(proxima)

    frentes.pop()  # remove a última frente, sempre vazia
    return frentes


def distancia_multidao(objetivos: Objetivos, frente: Sequence[int]) -> dict[int, float]:
    """Calcula a distância de multidão (crowding distance) de uma frente.

    Para cada objetivo, ordena a frente e soma a distância normalizada entre os
    dois vizinhos de cada indivíduo. Os extremos recebem infinito, o que
    preserva as pontas da fronteira. Quanto maior o valor, menos povoada é a
    região do indivíduo.

    Args:
        objetivos: ``(distancia, pedagio)`` de toda a população.
        frente: índices dos indivíduos da frente a ser avaliada.

    Returns:
        Dicionário ``índice -> distância de multidão``.
    """
    if not frente:
        return {}
    if len(frente) <= 2:
        return {i: inf for i in frente}

    distancias = {i: 0.0 for i in frente}
    for k in range(len(objetivos[frente[0]])):
        ordenada = sorted(frente, key=lambda i, k=k: objetivos[i][k])
        menor = objetivos[ordenada[0]][k]
        maior = objetivos[ordenada[-1]][k]

        distancias[ordenada[0]] = inf
        distancias[ordenada[-1]] = inf

        amplitude = maior - menor
        if amplitude == 0:
            continue  # todos iguais neste objetivo: não há o que normalizar

        for pos in range(1, len(ordenada) - 1):
            anterior = objetivos[ordenada[pos - 1]][k]
            seguinte = objetivos[ordenada[pos + 1]][k]
            distancias[ordenada[pos]] += (seguinte - anterior) / amplitude

    return distancias
