"""
Módulo Gerador de Instâncias de Teste para o TSP Multiobjetivo.
"""
import math
import random
from typing import Tuple
from .operators.instancia import InstanciaGrafo


def gerar_instancia_teste(
    n_cidades: int = 20,
    dimensao_mapa: Tuple[float, float] = (100.0, 100.0),
    densidade_arestas: float = 0.85,
    prob_pedagio: float = 0.5,
    faixa_pedagio: Tuple[float, float] = (5.0, 30.0),
    semente: int | None = 42,
    simetrico: bool = True,
) -> InstanciaGrafo:
    """
    Gera uma instância sintética do problema.

    :param n_cidades: Quantidade de cidades a visitar (excluindo a sede).
    :param dimensao_mapa: Área plana (largura, altura) para gerar coordenadas.
    :param densidade_arestas: Chance de existir conexão entre dois vértices (0.0 a 1.0).
    :param prob_pedagio: Probabilidade de um trecho existente ter pedágio.
    :param faixa_pedagio: Intervalo de valores (min, max) para os pedágios em R$.
    :param semente: Semente aleatória para reprodutibilidade.
    :param simetrico: Se True, a distância e pedágio de A->B é igual a B->A.
    """
    if semente is not None:
        random.seed(semente)

    total_vertices = n_cidades + 1  # Inclui a sede (índice 0)

    # 1. Gera coordenadas 2D aleatórias para as cidades
    coordenadas = {
        i: (random.uniform(0, dimensao_mapa[0]), random.uniform(0, dimensao_mapa[1]))
        for i in range(total_vertices)
    }

    matriz_distancia = {}
    matriz_pedagio = {}
    adjacencias = {i: [] for i in range(total_vertices)}

    # 2. Constrói as conexões do grafo
    for u in range(total_vertices):
        for v in range(total_vertices):
            if u == v:
                continue

            # Para grafos simétricos, reutiliza as propriedades do arco oposto se já existir
            if simetrico and u > v:
                if (v, u) in matriz_distancia:
                    matriz_distancia[(u, v)] = matriz_distancia[(v, u)]
                    matriz_pedagio[(u, v)] = matriz_pedagio[(v, u)]
                    adjacencias[u].append(v)
                continue

            # Define se a aresta/rua existe baseando-se na densidade
            if random.random() < densidade_arestas:
                x1, y1 = coordenadas[u]
                x2, y2 = coordenadas[v]
                distancia = math.hypot(x2 - x1, y2 - y1)

                # Define custo de pedágio
                pedagio = random.uniform(*faixa_pedagio) if random.random() < prob_pedagio else 0.0

                matriz_distancia[(u, v)] = round(distancia, 2)
                matriz_pedagio[(u, v)] = round(pedagio, 2)
                adjacencias[u].append(v)

    return InstanciaGrafo(
        n_cidades=n_cidades,
        matriz_distancia=matriz_distancia,
        matriz_pedagio=matriz_pedagio,
        adjacencias=adjacencias,
        sede=0,
    )
