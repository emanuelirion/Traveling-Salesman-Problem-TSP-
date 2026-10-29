"""Testes da dominância, da ordenação não dominada e da distância de multidão."""

import itertools
import math
import random

import pytest

from src.nsga2.ordenacao import (
    distancia_multidao,
    domina,
    domina_com_restricao,
    ordenar_nao_dominados,
)
from src.nsga2.selecao import selecao_ambiental, torneio_por_multidao

# Exemplo usado na apresentação: A, B e C são compromissos; D é dominada por A.
ROTAS = [(100.0, 40.0), (120.0, 20.0), (140.0, 10.0), (150.0, 50.0)]
A, B, C, D = range(4)


def test_a_domina_d_nos_dois_objetivos():
    assert domina(ROTAS[A], ROTAS[D])


def test_a_e_b_nao_se_dominam():
    assert not domina(ROTAS[A], ROTAS[B])
    assert not domina(ROTAS[B], ROTAS[A])


def test_solucoes_iguais_nao_se_dominam():
    assert not domina((1.0, 2.0), (1.0, 2.0))


def test_empate_em_um_objetivo_e_melhora_no_outro_domina():
    assert domina((1.0, 2.0), (1.0, 3.0))


def test_factivel_domina_infactivel_mesmo_com_objetivos_piores():
    assert domina_com_restricao((999.0, 999.0), 0, (1.0, 1.0), 2)
    assert not domina_com_restricao((1.0, 1.0), 2, (999.0, 999.0), 0)


def test_entre_infactiveis_vence_quem_tem_menos_violacoes():
    assert domina_com_restricao((50.0, 50.0), 1, (1.0, 1.0), 3)
    assert not domina_com_restricao((1.0, 1.0), 3, (50.0, 50.0), 1)
    assert not domina_com_restricao((1.0, 1.0), 2, (1.0, 1.0), 2)


def test_frentes_do_exemplo():
    frentes = ordenar_nao_dominados(ROTAS, [0, 0, 0, 0])
    assert [sorted(f) for f in frentes] == [[A, B, C], [D]]


def test_frentes_em_cadeia():
    objetivos = [(3.0, 3.0), (2.0, 2.0), (1.0, 1.0)]
    assert ordenar_nao_dominados(objetivos, [0, 0, 0]) == [[2], [1], [0]]


def test_infactiveis_ficam_atras_dos_factiveis():
    objetivos = [(10.0, 10.0), (100.0, 100.0), (5.0, 5.0)]
    frentes = ordenar_nao_dominados(objetivos, [1, 0, 3])
    assert frentes == [[1], [0], [2]]


def test_toda_a_populacao_aparece_exatamente_uma_vez():
    gerador = random.Random(7)
    objetivos = [(gerador.random(), gerador.random()) for _ in range(60)]
    frentes = ordenar_nao_dominados(objetivos, [0] * 60)
    todos = [i for frente in frentes for i in frente]
    assert sorted(todos) == list(range(60))


def test_frente_zero_nao_tem_dominancia_interna_e_as_demais_sao_dominadas():
    gerador = random.Random(11)
    objetivos = [(gerador.random(), gerador.random()) for _ in range(60)]
    frentes = ordenar_nao_dominados(objetivos, [0] * 60)

    for frente in frentes:
        for i in frente:
            for j in frente:
                assert not domina(objetivos[i], objetivos[j])
    for anterior, atual in itertools.pairwise(frentes):
        for j in atual:
            assert any(domina(objetivos[i], objetivos[j]) for i in anterior)


def test_populacao_vazia_e_tamanhos_diferentes():
    assert ordenar_nao_dominados([], []) == []
    with pytest.raises(ValueError):
        ordenar_nao_dominados([(1.0, 1.0)], [])


def test_multidao_extremos_infinitos_e_miolo_calculado():
    objetivos = [(0.0, 10.0), (5.0, 5.0), (10.0, 0.0)]
    dist = distancia_multidao(objetivos, [0, 1, 2])
    assert math.isinf(dist[0]) and math.isinf(dist[2])
    assert dist[1] == pytest.approx(2.0)  # 10/10 em cada objetivo


def test_multidao_favorece_regiao_menos_povoada():
    objetivos = [(0.0, 10.0), (1.0, 9.0), (2.0, 8.0), (9.0, 1.0), (10.0, 0.0)]
    dist = distancia_multidao(objetivos, [0, 1, 2, 3, 4])
    assert dist[3] > dist[1]


def test_multidao_frentes_pequenas_e_vazia():
    assert distancia_multidao([(1.0, 1.0)], []) == {}
    assert all(
        math.isinf(v)
        for v in distancia_multidao([(1.0, 1.0), (2.0, 0.0)], [0, 1]).values()
    )


def test_multidao_com_objetivo_constante_nao_divide_por_zero():
    objetivos = [(1.0, 5.0), (2.0, 5.0), (3.0, 5.0)]
    dist = distancia_multidao(objetivos, [0, 1, 2])
    assert dist[1] == pytest.approx(1.0)


def test_multidao_respeita_apenas_os_indices_da_frente():
    objetivos = [(0.0, 10.0), (100.0, 100.0), (5.0, 5.0), (10.0, 0.0)]
    dist = distancia_multidao(objetivos, [0, 2, 3])
    assert set(dist) == {0, 2, 3}
    assert dist[2] == pytest.approx(2.0)


def test_integracao_com_selecao_ambiental_corta_pela_multidao():
    """A última frente que não cabe é truncada pelos de maior multidão."""
    objetivos = [
        (0.0, 10.0),
        (1.0, 9.0),
        (5.0, 5.0),
        (9.0, 1.0),
        (10.0, 0.0),
        (20.0, 20.0),
    ]
    frentes = ordenar_nao_dominados(objetivos, [0] * 6)
    multidao = [0.0] * 6
    for frente in frentes:
        for idx, valor in distancia_multidao(objetivos, frente).items():
            multidao[idx] = valor

    escolhidos = selecao_ambiental(frentes, multidao, 4)
    assert len(escolhidos) == 4
    assert 5 not in escolhidos  # a frente dominada fica de fora
    assert {0, 4} <= set(escolhidos)  # as pontas da fronteira sobrevivem


def test_integracao_com_torneio_prefere_menor_rank():
    ranks, multidao = [0, 1], [0.0, math.inf]
    gerador = random.Random(1)
    assert all(torneio_por_multidao(ranks, multidao, gerador) == 0 for _ in range(20))
