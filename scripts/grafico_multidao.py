import os
import matplotlib.pyplot as plt
from src.gerador import gerar_instancia_teste
from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.ordenacao import ordenar_nao_dominados, distancia_multidao

# Função dummy para desativar a multidão
def sem_multidao(objetivos, frente):
    return {idx: 1.0 for idx in frente}

def main():
    os.makedirs("results", exist_ok=True)
    instancia = gerar_instancia_teste(n_cidades=15, densidade_arestas=0.85, semente=42)
    config = ConfiguracaoNSGA2(tamanho_populacao=100, geracoes=150, semente=42)
    
    # Execução 1: COM Crowding Distance
    nsga2_com = NSGA2(instancia, config, ordenar_nao_dominados, distancia_multidao)
    res_com = nsga2_com.executar()
    pareto_com_dist = [res_com.avaliacoes[i].distancia for i in res_com.fronteira_final]
    pareto_com_ped = [res_com.avaliacoes[i].pedagio for i in res_com.fronteira_final]

    # Execução 2: SEM Crowding Distance
    nsga2_sem = NSGA2(instancia, config, ordenar_nao_dominados, sem_multidao)
    res_sem = nsga2_sem.executar()
    pareto_sem_dist = [res_sem.avaliacoes[i].distancia for i in res_sem.fronteira_final]
    pareto_sem_ped = [res_sem.avaliacoes[i].pedagio for i in res_sem.fronteira_final]

    plt.figure(figsize=(9, 6))
    plt.scatter(pareto_sem_dist, pareto_sem_ped, c='red', alpha=0.6, s=80, label='Sem Crowding Distance (Aglomerado)')
    plt.scatter(pareto_com_dist, pareto_com_ped, c='blue', s=80, label='Com Crowding Distance (Espalhado)')
    
    plt.title("Comparação: Com vs Sem Crowding Distance")
    plt.xlabel("Distância Total (km)")
    plt.ylabel("Custo de Pedágio (R$)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("results/com_vs_sem_multidao.png", dpi=300, bbox_inches="tight")
    print("Gráfico salvo em results/com_vs_sem_multidao.png")

if __name__ == "__main__":
    main()