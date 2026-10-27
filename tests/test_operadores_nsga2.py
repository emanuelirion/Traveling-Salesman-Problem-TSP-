"""Testes do módulo de operadores genéticos e simulação do NSGA-II."""

import random
from dataclasses import dataclass
from src.nsga2.algoritmo import NSGA2
from src.nsga2.configuracao import ConfiguracaoNSGA2

# ---------------------------------------------------------
# STUBS: Simulando o código do Integrante 1 (Dados e Grafo)
# ---------------------------------------------------------
@dataclass
class AvaliacaoFalsa:
    distancia: float
    pedagio: float
    violacoes: int

class InstanciaFalsa:
    def __init__(self, n_cidades=15):
        self.sede = 0
        self.n_cidades = n_cidades
        self._gerador = random.Random(42)

    def tem_aresta(self, i: int, j: int) -> bool:
        # Simula um grafo onde 80% das estradas existem
        return self._gerador.random() < 0.8

    def vizinhos(self, cidade: int) -> list[int]:
        return [j for j in range(self.n_cidades + 1) if j != cidade and self.tem_aresta(cidade, j)]

    def distancia(self, i: int, j: int) -> float:
        return self._gerador.uniform(10.0, 100.0)

    def pedagio(self, i: int, j: int) -> float:
        return self._gerador.uniform(2.0, 20.0)

    def avaliar(self, rota: list[int]) -> AvaliacaoFalsa:
        dist = sum(self.distancia(rota[i], rota[i+1]) for i in range(len(rota)-1))
        ped = sum(self.pedagio(rota[i], rota[i+1]) for i in range(len(rota)-1))
        violacoes = sum(1 for i in range(len(rota)-1) if not self.tem_aresta(rota[i], rota[i+1]))
        return AvaliacaoFalsa(distancia=dist, pedagio=ped, violacoes=violacoes)

# ---------------------------------------------------------
# STUBS: Simulando o código do Integrante 3 (Pareto)
# ---------------------------------------------------------
def ordenar_falso(objetivos: list[tuple[float, float]], violacoes: list[int]) -> list[list[int]]:
    """Simula a separação em Fronteiras de Pareto agrupando aleatoriamente."""
    indices = list(range(len(objetivos)))
    random.shuffle(indices)
    meio = len(indices) // 2
    return [indices[:meio], indices[meio:]]

def multidao_falsa(objetivos: list[tuple[float, float]], frente: list[int]) -> dict[int, float]:
    """Gera distâncias de multidão aleatórias para o torneio."""
    return {idx: random.uniform(0.1, 2.0) for idx in frente}

# ---------------------------------------------------------
# EXECUÇÃO DO TESTE
# ---------------------------------------------------------
def testar_execucao():
    print("Iniciando testes com stubs (InstanciaFalsa, ordenar_falso, multidao_falsa)...")
    
    instancia = InstanciaFalsa()
    config = ConfiguracaoNSGA2(tamanho_populacao=20, geracoes=10, semente=42)
    
    algoritmo = NSGA2(
        instancia=instancia,
        configuracao=config,
        ordenar_fn=ordenar_falso,
        multidao_fn=multidao_falsa
    )
    
    resultado = algoritmo.executar()
    
    print("-" * 50)
    print(f"SUCESSO! O algoritmo completou {config.geracoes} gerações.")
    print(f"Tamanho da população final: {len(resultado.rotas)} rotas mantidas pelo elitismo.")
    print(f"Número de rotas na fronteira final (sem violações): {len(resultado.fronteira_final)}")
    print("-" * 50)
    print("O seu módulo de Operadores Genéticos e Ciclo Evolutivo está funcionando!")
    print("Quando os outros integrantes terminarem, basta substituir os stubs pelas funções deles.")

if __name__ == "__main__":
    testar_execucao()