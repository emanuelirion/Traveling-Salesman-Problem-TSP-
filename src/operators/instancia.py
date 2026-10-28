"""
Módulo de Modelagem da Instância do Grafo e Avaliação de Rotas.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple
from .contratos import ContratoInstancia, Rota


@dataclass(frozen=True)
class ResultadoAvaliacao:
    """Estrutura imutável com o resultado da avaliação multiobjetivo."""
    distancia: float
    pedagio: float
    violacoes: int


class InstanciaGrafo(ContratoInstancia):
    """
    Estrutura de dados para o grafo de cidades com distâncias e pedágios.
    Suporta grafos conexos e não-completos.
    """

    def __init__(
        self,
        n_cidades: int,
        matriz_distancia: Dict[Tuple[int, int], float],
        matriz_pedagio: Dict[Tuple[int, int], float],
        adjacencias: Dict[int, List[int]],
        sede: int = 0,
    ):
        self.n_cidades = n_cidades
        self.sede = sede
        self._distancias = matriz_distancia
        self._pedagios = matriz_pedagio
        self._adjacencias = adjacencias

    def tem_aresta(self, i: int, j: int) -> bool:
        """Verifica se existe conexão direta (rua/rodovia) entre duas cidades."""
        return (i, j) in self._distancias

    def vizinhos(self, cidade: int) -> List[int]:
        """Retorna as cidades diretamente conectadas à cidade informada."""
        return self._adjacencias.get(cidade, [])

    def distancia(self, i: int, j: int) -> float:
        """Retorna a distância (km) entre i e j."""
        return self._distancias.get((i, j), float("inf"))

    def pedagio(self, i: int, j: int) -> float:
        """Retorna o custo de pedágio (R$) entre i e j."""
        return self._pedagios.get((i, j), float("inf"))

    def avaliar(self, rota: Rota) -> ResultadoAvaliacao:
        """
        Decodifica o cromossomo e calcula os dois objetivos de forma independente:
        1. Custo Total de Distância (km)
        2. Custo Total de Pedágio (R$)
        
        Também contabiliza o número de arestas inexistentes percorridas (violações).
        """
        if not rota:
            return ResultadoAvaliacao(distancia=0.0, pedagio=0.0, violacoes=0)

        # Reconstrói o ciclo completo inserindo a sede no início e no fim
        ciclo_completo = [self.sede] + rota + [self.sede]

        distancia_total = 0.0
        pedagio_total = 0.0
        violacoes = 0

        # Percorre trecho a trecho do ciclo
        for u, v in zip(ciclo_completo[:-1], ciclo_completo[1:]):
            if self.tem_aresta(u, v):
                distancia_total += self.distancia(u, v)
                pedagio_total += self.pedagio(u, v)
            else:
                violacoes += 1

        return ResultadoAvaliacao(
            distancia=round(distancia_total, 2),
            pedagio=round(pedagio_total, 2),
            violacoes=violacoes,
        )