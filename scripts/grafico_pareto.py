import os
import matplotlib.pyplot as plt
from src.gerador import gerar_instancia_teste
from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.ordenacao import ordenar_nao_dominados, distancia_multidao
from src.nsga2.compromisso import escolher_rota_compromisso

def main():
    os.makedirs("results", exist_ok=True)
    
    # 1. Gera a instância e roda o algoritmo
    instancia = gerar_instancia_teste(n_cidades=15, densidade_arestas=0.85, semente=42)
    config = ConfiguracaoNSGA2(tamanho_populacao=100, geracoes=150, semente=42)
    nsga2 = NSGA2(instancia, config, ordenar_nao_dominados, distancia_multidao)
    resultado = nsga2.executar()
    
    # 2. Extrai os dados da fronteira de Pareto
    fronteira = resultado.fronteira_final
    distancias = [resultado.avaliacoes[idx].distancia for idx in fronteira]
    pedagios = [resultado.avaliacoes[idx].pedagio for idx in fronteira]
    
    # 3. Encontra a rota de compromisso ideal
    idx_compromisso = escolher_rota_compromisso(fronteira, peso_distancia=0.5)
    rota_escolhida = resultado.avaliacoes[fronteira[idx_compromisso]]
    
    # 4. Plota o gráfico
    plt.figure(figsize=(9, 6))
    plt.scatter(distancias, pedagios, c='blue', s=80, alpha=0.7, label='Fronteira de Pareto')
    
    # Destaca a rota escolhida
    plt.scatter(
        [rota_escolhida.distancia], [rota_escolhida.pedagio], 
        c='gold', edgecolors='black', marker='*', s=300, zorder=5, 
        label='Rota de Compromisso Escolhida'
    )
    
    plt.title("Fronteira de Pareto: Distância (km) × Pedágio (R$)")
    plt.xlabel("Distância Total (km)")
    plt.ylabel("Custo de Pedágio (R$)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    caminho = "results/pareto_final.png"
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    print(f"Gráfico salvo em {caminho}")

if __name__ == "__main__":
    main()