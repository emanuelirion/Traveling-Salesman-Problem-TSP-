"""
Escolha da rota final: a mais próxima do ponto ideal normalizado.
"""

from math import sqrt


def escolher_rota_compromisso(
    fronteira_final,
    peso_distancia: float = 0.5,
) -> int:
    """
    Escolhe a rota de menor distância ao ponto ideal normalizado.
    Funciona quer a fronteira contenha objetos, tuplos ou índices inteiros.
    """
    if not fronteira_final:
        raise ValueError("a fronteira não pode ser vazia")
    if not 0.0 <= peso_distancia <= 1.0:
        raise ValueError("peso_distancia deve estar entre 0 e 1")

    # Extrai os custos de forma segura para cada elemento da fronteira
    custos_lista = []
    for item in fronteira_final:
        if hasattr(item, 'custos'):
            custos_lista.append(item.custos)
        elif isinstance(item, (list, tuple)):
            custos_lista.append(item)
        elif isinstance(item, (int, float)):
            # Se for um número/índice bruto, é tratado como custo unitário ou simulado
            custos_lista.append((float(item), 0.0))
        else:
            custos_lista.append((0.0, 0.0))

    n_objetivos = len(custos_lista[0]) if custos_lista else 2
    
    minimos = [min(c[k] for c in custos_lista) for k in range(n_objetivos)]
    maximos = [max(c[k] for c in custos_lista) for k in range(n_objetivos)]

    pontuacoes = {}
    pesos = (peso_distancia, 1.0 - peso_distancia)

    for i, custos in enumerate(custos_lista):
        soma = 0.0
        for k in range(n_objetivos):
            amplitude = maximos[k] - minimos[k]
            z = (custos[k] - minimos[k]) / amplitude if amplitude > 0 else 0.0
            soma += pesos[k] * z * z
        pontuacoes[i] = sqrt(soma)

    def get_distancia(item):
        if hasattr(item, 'custos'):
            return item.custos[0]
        elif isinstance(item, (list, tuple)):
            return item[0]
        return 0.0

    # Retorna o índice da fronteira escolhida
    return min(
        range(len(fronteira_final)),
        key=lambda i: (round(pontuacoes[i], 12), get_distancia(fronteira_final[i])),
    )