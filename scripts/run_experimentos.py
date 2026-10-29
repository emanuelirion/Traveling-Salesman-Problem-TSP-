"""
Script principal de execução de experimentos.
"""

from src.gerador import gerar_instancia_teste
from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.ordenacao import ordenar_nao_dominados, distancia_multidao
from src.experimentos import salvar_resultados

def main():
    print("A iniciar o experimento do NSGA-II...")
    
    # 1. Gera a instância sintética (garantindo grafo conexo e não completo)
    instancia = gerar_instancia_teste(n_cidades=15, densidade_arestas=0.85, semente=42)
    
    # 2. Configura os parâmetros do algoritmo
    config = ConfiguracaoNSGA2(
        tamanho_populacao=100,
        geracoes=150,
        semente=42
    )
    
    # 3. Executa o NSGA-II com ordenação de Pareto e Distância de Multidão
    algoritmo = NSGA2(
        instancia=instancia,
        configuracao=config,
        ordenar_fn=ordenar_nao_dominados,
        multidao_fn=distancia_multidao
    )
    
    resultado = algoritmo.executar()
    print(f"Execução concluída! Encontradas {len(resultado.fronteira_final)} rotas na frente de Pareto ótima.")
    
    # 4. Salva os resultados (pareto.csv e pareto.png) na pasta results/
    salvar_resultados("instancia_teste_15", resultado, instancia, pesos_compromisso=0.5)
    
if __name__ == "__main__":
    main()