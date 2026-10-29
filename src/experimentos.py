"""
Módulo de Experimentos, Métricas e Visualização
Responsável por processar a Fronteira de Pareto, calcular métricas e gerar gráficos.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from src.nsga2.compromisso import escolher_rota_compromisso

def salvar_resultados(nome_instancia, resultado, instancia, pesos_compromisso=0.5):
    pasta_destino = os.path.join("results", nome_instancia)
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Prepara a lista de pares (distancia, pedagio) reais para a fronteira
    avaliacoes_fronteira = [
        (resultado.avaliacoes[idx].distancia, resultado.avaliacoes[idx].pedagio)
        for idx in resultado.fronteira_final
    ]
    
    # 1. Escolhe a rota usando a matemática real do Ponto Ideal
    indice_compromisso = escolher_rota_compromisso(avaliacoes_fronteira, pesos_compromisso)
    
    dados_csv = []
    for i, idx in enumerate(resultado.fronteira_final):
        rota = resultado.rotas[idx]
        avaliacao = resultado.avaliacoes[idx]
        eh_escolhida = 1 if i == indice_compromisso else 0
        sequencia = [instancia.sede] + rota + [instancia.sede]
        
        dados_csv.append({
            "rota_id": idx,
            "custo_distancia": avaliacao.distancia,
            "custo_pedagio": avaliacao.pedagio,
            "violacoes": avaliacao.violacoes,
            "eh_escolhida": eh_escolhida,
            "sequencia_cidades": " -> ".join(map(str, sequencia))
        })
        
    df = pd.DataFrame(dados_csv)
    caminho_csv = os.path.join(pasta_destino, "pareto.csv")
    df.to_csv(caminho_csv, index=False)
    print(f"Resultados exportados para: {caminho_csv}")
    
    # Gera o gráfico
    plt.figure(figsize=(8, 6))
    distancias = [p[0] for p in avaliacoes_fronteira]
    pedagios = [p[1] for p in avaliacoes_fronteira]
    
    plt.scatter(distancias, pedagios, c='blue', label='Fronteira de Pareto', zorder=3)
    
    if indice_compromisso is not None and 0 <= indice_compromisso < len(avaliacoes_fronteira):
        pt_comp = avaliacoes_fronteira[indice_compromisso]
        plt.scatter(
            [pt_comp[0]], [pt_comp[1]],
            c='blue', marker='*', s=200, label='Rota de Compromisso', zorder=4
        )
        
    plt.xlabel("Distância Total")
    plt.ylabel("Custo de Portagens / Pedágio")
    plt.title(f"Fronteira de Pareto - {nome_instancia}")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    caminho_grafico = os.path.join(pasta_destino, "pareto.png")
    plt.savefig(caminho_grafico, dpi=300)
    plt.close()
    print(f"Gráfico salvo em: {caminho_grafico}")

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
    plt.scatter([escolhida_dist], [escolhida_ped], c="blue", s=120, zorder=5, label="Rota de Compromisso Escolhida", marker="*")

    plt.xlabel("Distância Total (km)")
    plt.ylabel("Custo de Pedágio (R$)")
    plt.title("Fronteira de Pareto - TSP Multiobjetivo (NSGA-II)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    cam_img = os.path.join(diretorio, "pareto.png")
    plt.savefig(cam_img, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Gráfico gerado e salvo em: {cam_img}")