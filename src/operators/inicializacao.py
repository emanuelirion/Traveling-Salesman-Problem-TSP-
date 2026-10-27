"""População inicial para o TSP em grafo conexo não completo."""
import random
from collections.abc import Callable

from .contratos import ContratoInstancia, Rota
Ordenador = Callable[[int, list[int]], list[int]]

def rota_aleatoria(instancia: ContratoInstancia, gerador: random.Random) -> Rota:
    """Gera uma permutação puramente aleatória (comum em grafos completos)."""
    cidades = [c for c in range(instancia.n_cidades + 1) if c != instancia.sede]
    gerador.shuffle(cidades)
    return cidades

def buscar_ciclo(
    instancia: ContratoInstancia, ordenar: Ordenador, orcamento: int = 20_000) -> Rota | None:
    """
    Em um grafo não completo, montar uma rota indo para o "vizinho mais próximo" pode
    fazer o caminhão chegar em uma cidade que só tem ruas para cidades já visitadas
    (beco sem saída). Por isso, usamos uma Busca em Profundidade (DFS) com limite de passos.
    Se o caminhão trancar, o algoritmo faz o "backtracking" (volta um passo) e tenta outra rua.
    """
    sede, n_vertices = instancia.sede, instancia.n_cidades + 1
    caminho = [sede]
    visitadas = {sede}
    pilha = [ordenar(sede, list(instancia.vizinhos(sede)))]
    passos = 0
    
    while pilha and passos < orcamento:
        passos += 1
        candidatas = pilha[-1]
        
        # Se esgotaram os vizinhos dessa cidade, faz backtracking (recua)
        if not candidatas:
            pilha.pop()
            visitadas.discard(caminho.pop())
            continue
            
        cidade = candidatas.pop()
        if cidade in visitadas:
            continue
            
        # Garante que a última cidade consiga voltar para a sede
        if len(caminho) == n_vertices - 1 and not instancia.tem_aresta(cidade, sede):
            continue  
            
        caminho.append(cidade)
        visitadas.add(cidade)
        
        # Fechou o ciclo perfeitamente
        if len(caminho) == n_vertices:
            return caminho[1:]
            
        pilha.append(ordenar(cidade, list(instancia.vizinhos(cidade))))
    return None

def rota_gulosa_factivel(
    instancia: ContratoInstancia, peso_distancia: float, orcamento: int = 20_000) -> Rota | None:
    """
    Para não começar o NSGA-II do zero, inserimos indivíduos "gulosos".
    Como temos DOIS objetivos, usamos um peso normalizado (`peso_distancia`).
    Se inserirmos sementes variando esse peso (de 0 a 1), garantimos que a população inicial
    já nasça cobrindo os dois extremos da Fronteira de Pareto.
    """
    km_max, pedagio_max = _escalas_das_arestas(instancia)

    def custo(cidade: int, outra: int) -> float:
        km = instancia.distancia(cidade, outra) / km_max
        reais = instancia.pedagio(cidade, outra) / pedagio_max
        return peso_distancia * km + (1 - peso_distancia) * reais

    def ordenar(cidade: int, vizinhos: list[int]) -> list[int]:
        # Ordena os vizinhos do mais promissor (menor custo agregado) para o pior
        return sorted(vizinhos, key=lambda outra: custo(cidade, outra), reverse=True)

    return buscar_ciclo(instancia, ordenar, orcamento)

def rota_factivel_aleatoria(
    instancia: ContratoInstancia,
    gerador: random.Random,
    orcamento: int = 20_000,
    reinicios: int = 20,
) -> Rota | None:
    """Ciclo hamiltoniano aleatório (ordem aleatória dos vizinhos)."""
    def ordenar(_cidade: int, vizinhos: list[int]) -> list[int]:
        gerador.shuffle(vizinhos)
        return vizinhos

    por_tentativa = max(orcamento // reinicios, 1)
    for _ in range(reinicios):
        rota = buscar_ciclo(instancia, ordenar, por_tentativa)
        if rota is not None:
            return rota
    return None

def populacao_inicial(
    instancia: ContratoInstancia,
    tamanho: int,
    sementes_gulosas: int,
    fracao_factivel: float,
    gerador: random.Random,
) -> list[Rota]:
    """
    Sementes gulosas (até 20%) + rotas factíveis aleatórias + permutações aleatórias.
    As sementes cobrem as pontas da fronteira; o restante mantém a diversidade genética.
    """
    populacao: list[Rota] = []
    vistas: set[tuple[int, ...]] = set()

    def adicionar(rota: Rota | None) -> None:
        if rota is not None and tuple(rota) not in vistas:
            vistas.add(tuple(rota))
            populacao.append(rota)

    n_sementes = min(sementes_gulosas, tamanho // 5)
    for k in range(n_sementes):
        peso = k / (n_sementes - 1) if n_sementes > 1 else 0.5
        adicionar(rota_gulosa_factivel(instancia, peso))

    alvo_factivel = int(tamanho * fracao_factivel)
    falhas = 0
    while len(populacao) < alvo_factivel and falhas < 5:
        antes = len(populacao)
        adicionar(rota_factivel_aleatoria(instancia, gerador))
        falhas = falhas + 1 if len(populacao) == antes else 0

    while len(populacao) < tamanho:
        populacao.append(rota_aleatoria(instancia, gerador))
    return populacao

def _escalas_das_arestas(instancia: ContratoInstancia) -> tuple[float, float]:
    """Maiores km e pedágio entre os trechos existentes (para normalizar)."""
    km_max = pedagio_max = 0.0
    for i in range(instancia.n_cidades + 1):
        for j in instancia.vizinhos(i):
            km_max = max(km_max, instancia.distancia(i, j))
            pedagio_max = max(pedagio_max, instancia.pedagio(i, j))
    return (km_max or 1.0), (pedagio_max or 1.0)