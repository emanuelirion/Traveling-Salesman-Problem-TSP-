import os
import itertools
import matplotlib.pyplot as plt
from src.gerador import gerar_instancia_teste
from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.ordenacao import ordenar_nao_dominados, distancia_multidao

def main():
    os.makedirs("results", exist_ok=True)
    # 8 cidades + 1 sede = Grafo de 9 vértices
    instancia = gerar_instancia_teste(n_cidades=8, densidade_arestas=0.9, semente=10)
    
    print("Calculando fronteira exata por força bruta (isso pode levar alguns segundos)...")
    cidades_para_visitar = list(range(1, instancia.n_cidades + 1))
    avaliacoes_validas = []
    
    for permutacao in itertools.permutations(cidades_para_visitar):
        rota = list(permutacao)
        aval = instancia.avaliar(rota)
        if aval.violacoes == 0:
            avaliacoes_validas.append((aval.distancia, aval.pedagio))
            
    # Extrai a frente 0 real
    frentes_exatas = ordenar_nao_dominados(avaliacoes_validas, [0] * len(avaliacoes_validas))
    pareto_exato = [avaliacoes_validas[i] for i in frentes_exatas[0]]
    exato_dist = [p[0] for p in pareto_exato]
    exato_ped = [p[1] for p in pareto_exato]

    print("Rodando NSGA-II para comparar...")
    config = ConfiguracaoNSGA2(tamanho_populacao=40, geracoes=50, semente=10)
    nsga2 = NSGA2(instancia, config, ordenar_nao_dominados, distancia_multidao)
    res_nsga2 = nsga2.executar()
    
    nsga2_dist = [res_nsga2.avaliacoes[i].distancia for i in res_nsga2.fronteira_final]
    nsga2_ped = [res_nsga2.avaliacoes[i].pedagio for i in res_nsga2.fronteira_final]

    plt.figure(figsize=(9, 6))
    plt.scatter(exato_dist, exato_ped, c='gray', s=150, alpha=0.5, label='Fronteira Exata (Força Bruta)')
    plt.scatter(nsga2_dist, nsga2_ped, c='blue', marker='*', s=100, label='NSGA-II')
    
    plt.title("Comparação: NSGA-II vs Fronteira Exata (9 Cidades)")
    plt.xlabel("Distância Total (km)")
    plt.ylabel("Custo de Pedágio (R$)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("results/fronteira_exata.png", dpi=300, bbox_inches="tight")
    print("Gráfico salvo em results/fronteira_exata.png")

if __name__ == "__main__":
    main()