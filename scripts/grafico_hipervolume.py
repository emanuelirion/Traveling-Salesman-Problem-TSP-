import os
import matplotlib.pyplot as plt
from src.gerador import gerar_instancia_teste
from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.ordenacao import ordenar_nao_dominados, distancia_multidao

def calcular_hipervolume_2d(frente_objetivos, ref_x, ref_y):
    """Calcula a área dominada pela fronteira em relação a um ponto de referência."""
    if not frente_objetivos: return 0.0
    pontos = sorted(frente_objetivos) # Ordena pela distância (x)
    hv = 0.0
    y_anterior = ref_y
    for x, y in pontos:
        if x > ref_x or y > ref_y: continue
        hv += (ref_x - x) * (y_anterior - y)
        y_anterior = y
    return hv

def main():
    os.makedirs("results", exist_ok=True)
    instancia = gerar_instancia_teste(n_cidades=15, densidade_arestas=0.85, semente=42)
    
    # Pontos de referência (valores altos e pessimistas para a instância)
    REF_DISTANCIA = 2000.0
    REF_PEDAGIO = 500.0
    
    sementes = [10, 42, 99]
    plt.figure(figsize=(9, 6))

    for semente in sementes:
        config = ConfiguracaoNSGA2(tamanho_populacao=80, geracoes=100, semente=semente)
        nsga2 = NSGA2(instancia, config, ordenar_nao_dominados, distancia_multidao)
        resultado = nsga2.executar()
        
        hv_historia = []
        for estatistica in resultado.historico:
            hv = calcular_hipervolume_2d(estatistica.objetivos_frente, REF_DISTANCIA, REF_PEDAGIO)
            hv_historia.append(hv)
            
        plt.plot(range(len(hv_historia)), hv_historia, linewidth=2, label=f'Semente {semente}')

    plt.title("Evolução do Hipervolume por Geração e Semente")
    plt.xlabel("Geração")
    plt.ylabel("Hipervolume")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("results/hipervolume.png", dpi=300, bbox_inches="tight")
    print("Gráfico salvo em results/hipervolume.png")

if __name__ == "__main__":
    main()