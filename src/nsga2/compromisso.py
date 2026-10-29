"""Escolha da rota final: a mais próxima do ponto ideal normalizado.

O NSGA-II devolve um conjunto de rotas não dominadas. Este módulo escolhe uma
delas pelo critério definido em ``docs/MODELAGEM.md`` (seção 7).
"""

from collections.abc import Sequence
from math import sqrt

Objetivos = Sequence[tuple[float, float]]


def pontuar_compromisso(
    objetivos: Objetivos,
    fronteira: Sequence[int],
    peso_distancia: float = 0.5,
) -> dict[int, float]:
    """Calcula, para cada rota da fronteira, a distância ao ponto ideal.

    Cada objetivo é normalizado pela amplitude da própria fronteira:
    ``z_k = (f_k - min f_k) / (max f_k - min f_k)``. O ponto ideal é (0, 0) e a
    pontuação é ``sqrt(w_d * z1² + w_p * z2²)``, com ``w_p = 1 - w_d``.
    Quanto menor, melhor.

    Args:
        objetivos: ``(distancia, pedagio)`` de toda a população.
        fronteira: índices das rotas não dominadas.
        peso_distancia: peso ``w_d`` da distância, entre 0 e 1.

    Raises:
        ValueError: se a fronteira estiver vazia ou o peso estiver fora de [0, 1].
    """
    if not fronteira:
        raise ValueError("a fronteira não pode ser vazia")
    if not 0.0 <= peso_distancia <= 1.0:
        raise ValueError("peso_distancia deve estar entre 0 e 1")

    pesos = (peso_distancia, 1.0 - peso_distancia)
    n_objetivos = len(pesos)
    menores = [min(objetivos[i][k] for i in fronteira) for k in range(n_objetivos)]
    maiores = [max(objetivos[i][k] for i in fronteira) for k in range(n_objetivos)]

    pontuacoes: dict[int, float] = {}
    for i in fronteira:
        soma = 0.0
        for k in range(n_objetivos):
            amplitude = maiores[k] - menores[k]
            z = (objetivos[i][k] - menores[k]) / amplitude if amplitude > 0 else 0.0
            soma += pesos[k] * z * z
        pontuacoes[i] = sqrt(soma)
    return pontuacoes


def escolher_rota_compromisso(
    objetivos: Objetivos,
    fronteira: Sequence[int],
    peso_distancia: float = 0.5,
) -> int:
    """Escolhe a rota de menor distância ao ponto ideal normalizado.

    Em caso de empate, vence a rota de menor distância (km).

    Returns:
        Índice, em ``objetivos``, da rota escolhida.
    """
    pontuacoes = pontuar_compromisso(objetivos, fronteira, peso_distancia)
    return min(
        fronteira,
        key=lambda i: (round(pontuacoes[i], 12), objetivos[i][0]),
    )
