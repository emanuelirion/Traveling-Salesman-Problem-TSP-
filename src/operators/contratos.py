"""Contrato entre os operadores e a instância do problema."""
from typing import Protocol
Rota = list[int]

class ContratoInstancia(Protocol):
    """ 
    O que os operadores precisam saber do grafo conexo (não completo).
    """
    sede: int
    n_cidades: int

    def tem_aresta(self, i: int, j: int) -> bool:
        """Verifica se a rua existe. Crucial para os reparos e buscas."""
    def vizinhos(self, cidade: int) -> list[int]:
        """Quem está conectado diretamente. Usado na busca em profundidade."""
    def distancia(self, i: int, j: int) -> float:
        """Distância (km) do trecho existente (i, j)"""
    def pedagio(self, i: int, j: int) -> float:
        """Pedágio (R$) do trecho existente (i, j)"""