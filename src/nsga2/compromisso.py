"""
Módulo de Compromisso
Calcula a rota de compromisso usando o Ponto Ideal Normalizado (Min-Max + Euclidiana).
"""

def escolher_rota_compromisso(avaliacoes_fronteira, pesos_compromisso=0.5):
    """
    Recebe uma lista de tuplas ou objetos com (distancia, pedagio) para a fronteira final.
    Retorna o ÍNDICE da rota que está mais próxima do Ponto Ideal (0, 0) normalizado.
    """
    if not avaliacoes_fronteira:
        return None
        
    if len(avaliacoes_fronteira) == 1:
        return 0

    pontos = []
    for item in avaliacoes_fronteira:
        if isinstance(item, (tuple, list)):
            pontos.append((item[0], item[1]))
        elif hasattr(item, 'distancia') and hasattr(item, 'pedagio'):
            pontos.append((item.distancia, item.pedagio))
        else:
            # Caso receba tupla por getattr ou dict
            d = getattr(item, 'distancia', 0.0)
            p = getattr(item, 'pedagio', 0.0)
            pontos.append((d, p))

    distancias = [p[0] for p in pontos]
    pedagios = [p[1] for p in pontos]

    min_dist, max_dist = min(distancias), max(distancias)
    min_ped, max_ped = min(pedagios), max(pedagios)

    range_dist = (max_dist - min_dist) if (max_dist - min_dist) > 0 else 1.0
    range_ped = (max_ped - min_ped) if (max_ped - min_ped) > 0 else 1.0

    melhor_idx = 0
    menor_dist_euclidiana = float('inf')

    for i, (d, p) in enumerate(pontos):
        # Normalização Min-Max [0, 1]
        d_norm = (d - min_dist) / range_dist
        p_norm = (p - min_ped) / range_ped

        # Distância ao Ponto Ideal [0, 0]
        dist_euc = (d_norm ** 2 + p_norm ** 2) ** 0.5

        if dist_euc < menor_dist_euclidiana:
            menor_dist_euclidiana = dist_euc
            melhor_idx = i

    return melhor_idx