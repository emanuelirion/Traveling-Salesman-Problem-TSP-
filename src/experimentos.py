"""
Módulo de Experimentos, Métricas e Visualização
Responsável por processar a Fronteira de Pareto, calcular métricas e gerar gráficos.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from src.nsga2.compromisso import escolher_rota_compromisso

def salvar_resultados(nome_instancia, resultado, instancia, pesos_compromisso=0.5):
    """
    Processa a fronteira de Pareto final, calcula a rota de compromisso,
    exporta os dados para CSV e gera o gráfico visual.
    """
    # Cria a pasta de resultados se não existir
    pasta_destino = os.path.join("results", nome_instancia)
    os.makedirs(pasta_destino, exist_ok=True)
    
    # 1. Escolhe a rota de compromisso usando a Distância de Multidão e os pesos
    indice_compromisso = escolher_rota_compromisso(resultado.fronteira_final, pesos_compromisso)
    
    dados_csv = []
    
    for i, idx in enumerate(resultado.fronteira_final):
        # Obtém a rota e a avaliação real usando o índice da fronteira
        rota = resultado.rotas[idx]
        avaliacao = resultado.avaliacoes[idx]
        
        # Verifica se este indivíduo é o escolhido como compromisso
        eh_escolhida = 1 if i == indice_compromisso else 0
        
        # Garante que a rota começa e termina na sede da instância
        sequencia = [instancia.sede] + rota + [instancia.sede]
        
        dados_csv.append({
            "rota_id": idx,
            "custo_distancia": avaliacao.distancia,
            "custo_pedagio": avaliacao.pedagio,
            "violacoes": avaliacao.violacoes,
            "eh_escolhida": eh_escolhida,
            "sequencia_cidades": " -> ".join(map(str, sequencia))
        })
        
    # 2. Guarda os dados em CSV
    df = pd.DataFrame(dados_csv)
    caminho_csv = os.path.join(pasta_destino, "pareto.csv")
    df.to_csv(caminho_csv, index=False)
    print(f"Resultados exportados com sucesso para: {caminho_csv}")
    
    # 3. Gera e guarda o gráfico da Fronteira de Pareto
    plt.figure(figsize=(8, 6))
    
    distancias = [resultado.avaliacoes[idx].distancia for idx in resultado.fronteira_final]
    pedagios = [resultado.avaliacoes[idx].pedagio for idx in resultado.fronteira_final]
    
    plt.scatter(distancias, pedagios, c='blue', label='Fronteira de Pareto', zorder=3)
    
    # Destaca a rota de compromisso escolhida
    if indice_compromisso is not None and 0 <= indice_compromisso < len(resultado.fronteira_final):
        idx_comp = resultado.fronteira_final[indice_compromisso]
        aval_comp = resultado.avaliacoes[idx_comp]
        plt.scatter(
            [aval_comp.distancia], [aval_comp.pedagio],
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
    print(f"Gráfico gerado e salvo em: {caminho_grafico}")

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