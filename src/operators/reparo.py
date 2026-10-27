"""Reparo de rotas que usam trechos inexistentes (grafo conexo, não completo)."""
import random
from collections.abc import Iterator

from .contratos import ContratoInstancia, Rota

def reparar_rota(
    rota: Rota, instancia: ContratoInstancia, gerador: random.Random, max_tentativas: int
) -> Rota:
    """
    Como o grafo não é completo, os cruzamentos (OX) fatalmente criarão rotas sugerindo ruas que 
    não existem. Se apenas puníssemos essas rotas, o NSGA-II demoraria muito para convergir. 
    Este reparador atua proativamente: ele identifica a rua inexistente e usa movimentos locais
    (2-opt guiado) para tentar conectar a rota a um vizinho real. Se o reparo diminuir a 
    quantidade de erros da rota, ele é aceito.
    """
    caminho = [instancia.sede, *rota, instancia.sede]
    
    for _ in range(max_tentativas):
        invalidos = _arestas_invalidas(caminho, instancia)
        # Se não há mais arestas inexistentes, a rota está perfeitamente consertada
        if not invalidos:
            break
            
        # Pega uma aresta problemática aleatória e tenta consertá-la
        k = gerador.choice(invalidos)
        for candidato in _caminhos_candidatos(caminho, k, instancia, gerador):
            # Só aceita a mutação se ela de fato reduziu os erros
            if len(_arestas_invalidas(candidato, instancia)) < len(invalidos):
                caminho = candidato
                break
                
    return caminho[1:-1]

def _arestas_invalidas(caminho: Rota, instancia: ContratoInstancia) -> list[int]:
    """Varre a rota para listar quais índices tentam atravessar ruas que não existem."""
    return [
        k
        for k in range(len(caminho) - 1)
        if not instancia.tem_aresta(caminho[k], caminho[k + 1])
    ]

def _segmento_invertido(caminho: Rota, i: int, j: int) -> Rota:
    """Operador básico para aplicar a inversão do reparo."""
    return caminho[:i] + caminho[i : j + 1][::-1] + caminho[j + 1 :]

def _caminhos_candidatos(
    caminho: Rota, k: int, instancia: ContratoInstancia, gerador: random.Random
) -> Iterator[Rota]:
    """Gera vizinhança de reparo procurando cidades conectadas factíveis."""
    a, b = caminho[k], caminho[k + 1]
    
    # Tenta reconectar a partir do vértice 'a'
    for cidade in _embaralhada(instancia.vizinhos(a), gerador):
        posicao = caminho.index(cidade)
        if cidade != instancia.sede and posicao > k + 1:
            yield _segmento_invertido(caminho, k + 1, posicao)
            
    # Tenta reconectar a partir do vértice 'b'
    for cidade in _embaralhada(instancia.vizinhos(b), gerador):
        posicao = caminho.index(cidade)
        if cidade != instancia.sede and posicao < k:
            yield _segmento_invertido(caminho, posicao, k)

def _embaralhada(itens: list[int], gerador: random.Random) -> list[int]:
    itens = list(itens)
    gerador.shuffle(itens)
    return itens