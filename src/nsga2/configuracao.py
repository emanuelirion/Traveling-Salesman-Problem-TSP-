""" Parâmetros do NSGA-II """
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfiguracaoNSGA2:
    """Hiperparâmetros do ciclo evolutivo.
    O uso de @dataclass(frozen=True) garante que nenhum parâmetro seja 
    alterado acidentalmente no meio da execução do algoritmo (imutabilidade).
    """
    
    tamanho_populacao: int = 100   # Quantas rotas competem por geração
    geracoes: int = 300            # Critério de parada do algoritmo
    prob_cruzamento: float = 0.9   # Alta chance de combinar pais
    prob_mutacao: float = 0.3      # Chance moderada de mutação
    tentativas_reparo: int = 20    # Insistência em arrumar rotas inválidas no grafo incompleto
    sementes_gulosas: int = 11     # Rotas pré-calculadas por vizinho mais próximo para dar vantagem inicial
    fracao_inicial_factivel: float = 0.5
    semente: int | None = 1        # resultados iguais em todas as execuções