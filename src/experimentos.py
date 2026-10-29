"""
Módulo de Experimentos, Métricas e Visualização
Responsável por processar a Fronteira de Pareto, calcular métricas e gerar gráficos.
"""

import os
import csv
from .compromisso import escolher_rota_compromisso

def salvar_resultados(instancia_nome: str, resultado, pesos_compromisso: float = 0.5) -> None:
    """
    Processa a fronteira final do NSGA-II, escolhe a rota de compromisso
    e exporta os resultados para a pasta results/<instancia_nome>/
    """
    diretorio = os.path.join("results", instancia_nome)
    os.makedirs(diretorio, exist_ok=True)
    
    frente_indices = resultado.fronteira_final
    if not frente_indices:
        print("Aviso: A fronteira final está vazia. Nenhum resultado para salvar.")
        return

    # Extrai objetivos de toda a população para o cálculo do compromisso
    objetivos = [(av.distancia, av.pedagio) for av in resultado.avaliacoes]
    
    # Escolhe a melhor rota pelo critério de compromisso normalizado
    melhor_idx = escolher_rota_compromisso(objetivos, frente_indices, peso_distancia=pesos_compromisso)
    
    # 1. Exportar para pareto.csv
    caminho_csv = os.path.join(diretorio, "pareto.csv")
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["distancia_km", "pedagio_rs", "eh_escolhida", "sequencia_vertices"])
        
        for idx in frente_indices:
            av = resultado.avaliacoes[idx]
            rota = resultado.rotas[idx]
            sequencia = [resultado.instancia.sede] + rota + [resultado.instancia.sede]
            escolhida = 1 if idx == melhor_idx else 0
            
            escritor.writerow([av.distancia, av.pedagio, escolhida, "->".join(map(str, sequencia))])
            
    print(f"Resultados exportados com sucesso para: {caminho_csv}")
    
    # 2. Gerar Gráfico (pareto.png)
    gerar_grafico_pareto(objetivos, frente_indices, melhor_idx, diretorio)

def gerar_grafico_pareto(objetivos, fronteira, melhor_idx, diretorio: str) -> None:
    """Gera o gráfico de dispersão da Fronteira de Pareto usando matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib não está instalado. Gráfico não gerado.")
        return

    geral_dist = [obj[0] for obj in objetivos]
    geral_ped = [obj[1] for obj in objetivos]

    pareto_dist = [objetivos[i][0] for i in fronteira]
    pareto_ped = [objetivos[i][1] for i in fronteira]

    escolhida_dist = objetivos[melhor_idx][0]
    escolhida_ped = objetivos[melhor_idx][1]

    plt.figure(figsize=(8, 6))
    plt.scatter(geral_dist, geral_ped, c="lightgray", label="População Geral", alpha=0.6)
    plt.plot(pareto_dist, pareto_ped, "o-", c="#1f77b4", label="Fronteira de Pareto", linewidth=2, markersize=6)
    plt.scatter([escolhida_dist], [escolhida_ped], c="red", s=120, zorder=5, label="Rota de Compromisso Escolhida", marker="*")

    plt.xlabel("Distância Total (km)")
    plt.ylabel("Custo de Pedágio (R$)")
    plt.title("Fronteira de Pareto - TSP Multiobjetivo (NSGA-II)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    caminho_img = os.path.join(diretorio, "pareto.png")
    plt.savefig(caminho_img, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Gráfico gerado e salvo em: {caminho_img}")