"""Laço principal do algoritmo NSGA-II para o problema do caixeiro viajante (TSP)."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ..operators.contratos import ContratoInstancia, Rota
from ..operators.cruzamento import cruzamento_ox
from ..operators.inicializacao import populacao_inicial, rota_aleatoria
from ..operators.mutacao import mutar
from ..operators.reparo import reparar_rota
from .configuracao import ConfiguracaoNSGA2
from .selecao import selecao_ambiental, torneio_por_multidao

Objetivos = list[tuple[float, float]]
FuncaoOrdenacao = Callable[[Objetivos, list[int]], list[list[int]]]
FuncaoMultidao = Callable[[Objetivos, list[int]], dict[int, float]]

class Avaliacao(Protocol):
    """Resultado de avaliar uma rota."""
    distancia: float
    pedagio: float
    violacoes: int

class InstanciaAvaliavel(ContratoInstancia, Protocol):
    def avaliar(self, rota: Rota) -> Avaliacao: ...

@dataclass(frozen=True)
class EstatisticasGeracao:
    geracao: int
    qtd_factiveis: int
    objetivos_frente: list[tuple[float, float]]

@dataclass(frozen=True)
class ResultadoNSGA2:
    rotas: list[Rota]
    avaliacoes: list[Avaliacao]
    frentes: list[list[int]]
    historico: list[EstatisticasGeracao]

    @property
    def fronteira_final(self) -> list[int]:
        # Para a entrega, só importam as rotas ótimas (Frente 0) que não usam ruas inexistentes (violacoes == 0)
        return [i for i in self.frentes[0] if self.avaliacoes[i].violacoes == 0]

class NSGA2:
    def __init__(
            self,
            instancia: InstanciaAvaliavel,
            configuracao: ConfiguracaoNSGA2,
            ordenar_fn: FuncaoOrdenacao,
            multidao_fn: FuncaoMultidao,
    ):
        self.instancia = instancia
        self.configuracao = configuracao
        self.ordenar_fn = ordenar_fn
        self.multidao_fn = multidao_fn

    def executar(self) -> ResultadoNSGA2:
        """
        Ponto de entrada do laço evolutivo. É aqui que o NSGA-II ganha vida.
        """
        cfg = self.configuracao
        gerador = random.Random(cfg.semente)
        
        # Nasce a população zero.
        rotas = populacao_inicial(self.instancia, cfg.tamanho_populacao, cfg.sementes_gulosas, cfg.fracao_inicial_factivel, gerador)
        avaliacoes = [self.instancia.avaliar(r) for r in rotas]
        historico: list[EstatisticasGeracao] = []

        # Inicia o ciclo de gerações (O motor do algoritmo)
        for geracao in range(cfg.geracoes):
            # Delega a matemática de Pareto e Crowding Distance
            frentes, ranks, multidao = self._classificar(avaliacoes)
            historico.append(self._estatisticas(geracao, frentes, avaliacoes))
            
            # Gera a população de filhos usando os operadores genéticos
            filhos = self._gerar_filhos(rotas, ranks, multidao, gerador)
            aval_filhos = [self.instancia.avaliar(r) for r in filhos]
            
            # Junta pais e filhos (2N) e corta de volta para o tamanho N
            rotas, avaliacoes = self._sobreviver(rotas + filhos, avaliacoes + aval_filhos, gerador)

        # Retorna o relatório final após todas as gerações
        frentes, _, _ = self._classificar(avaliacoes)
        historico.append(self._estatisticas(cfg.geracoes, frentes, avaliacoes))
        return ResultadoNSGA2(rotas, avaliacoes, frentes, historico)

    def _classificar(self, avaliacoes: list[Avaliacao]):
        """
        Prepara as estruturas de dados de Rank (Fronteira) e Multidão.
        Esses valores serão usados pela sua função de torneio logo em seguida.
        """
        objetivos = [(a.distancia, a.pedagio) for a in avaliacoes]
        violacoes = [a.violacoes for a in avaliacoes]
        
        frentes = self.ordenar_fn(objetivos, violacoes)
        
        ranks = [0] * len(avaliacoes)
        multidao = [0.0] * len(avaliacoes) 
        
        for rank, frente in enumerate(frentes):
            distancias = self.multidao_fn(objetivos, frente)
            for idx in frente:
                ranks[idx] = rank
                multidao[idx] = distancias.get(idx, 0.0)
                
        return frentes, ranks, multidao

    def _gerar_filhos(self, rotas, ranks, multidao, gerador) -> list[Rota]:
        """
        Aplica os operadores biológicos: Seleção, Cruzamento e Mutação.
        Garante que a nova geração seja criada respeitando as restrições do TSP.
        """
        cfg = self.configuracao
        filhos: list[Rota] = []
        
        while len(filhos) < cfg.tamanho_populacao:
            # Seleciona pais priorizando áreas menos exploradas do gráfico
            pai_a = rotas[torneio_por_multidao(ranks, multidao, gerador)]
            pai_b = rotas[torneio_por_multidao(ranks, multidao, gerador)]
            
            # Cruzamento OX
            if gerador.random() < cfg.prob_cruzamento:
                novos = cruzamento_ox(pai_a, pai_b, gerador) 
            else:
                novos = (pai_a[:], pai_b[:])
                
            for filho in novos:
                # Adiciona ruído genético para evitar estagnação
                if gerador.random() < cfg.prob_mutacao:
                    filho = mutar(filho, gerador)
                
                # Tenta consertar rotas que passaram por ruas inexistentes
                filho = reparar_rota(filho, self.instancia, gerador, cfg.tentativas_reparo)
                filhos.append(filho)
                
        return filhos[:cfg.tamanho_populacao]

    def _sobreviver(self, super_rotas, super_avaliacoes, gerador):
        """
        Aplica o Elitismo e a Seleção Ambiental.
        Recebe uma população dobrada (Pais + Filhos) e define quem sobrevive.
        """
        #  Evita que a população seja dominada por rotas idênticas
        manter = self._unicos_por_objetivos(super_avaliacoes)
        rotas_unicas = [super_rotas[i] for i in manter]
        avals_unicas = [super_avaliacoes[i] for i in manter]
        
        # Reclassifica a população agora que está limpa e dobrada
        frentes, _, multidao = self._classificar(avals_unicas)
        
        # seleciona exatamente N sobreviventes
        escolhidos = selecao_ambiental(frentes, multidao, self.configuracao.tamanho_populacao)
        
        novas_rotas = [rotas_unicas[i] for i in escolhidos]
        novas_avaliacoes = [avals_unicas[i] for i in escolhidos]
        
        while len(novas_rotas) < self.configuracao.tamanho_populacao: 
            extra = rota_aleatoria(self.instancia, gerador)
            novas_rotas.append(extra)
            novas_avaliacoes.append(self.instancia.avaliar(extra))
            
        return novas_rotas, novas_avaliacoes

    @staticmethod
    def _estatisticas(geracao: int, frentes, avaliacoes) -> EstatisticasGeracao:
        factiveis = [i for i in frentes[0] if avaliacoes[i].violacoes == 0]
        pontos = sorted((avaliacoes[i].distancia, avaliacoes[i].pedagio) for i in factiveis)
        total_factiveis = sum(1 for a in avaliacoes if a.violacoes == 0)
        return EstatisticasGeracao(geracao, total_factiveis, pontos)

    @staticmethod
    def _unicos_por_objetivos(avaliacoes: list[Avaliacao]) -> list[int]:
        """
        Filtro de diversidade. Se duas rotas têm o mesmo custo e pedágio, 
        mantemos apenas uma. Isso mantém a fronteira de Pareto rica e distribuída.
        """
        vistos = set()
        manter = []
        for idx, a in enumerate(avaliacoes):
            chave = (a.violacoes, round(a.distancia, 6), round(a.pedagio, 6))
            if chave not in vistos:
                vistos.add(chave)
                manter.append(idx)
        return manter