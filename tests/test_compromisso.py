"""Testes do critério de escolha da rota final (ponto ideal normalizado)."""

import pytest

from src.nsga2.compromisso import escolher_rota_compromisso, pontuar_compromisso

# Fronteira do exemplo da apresentação.
FRONTEIRA = [(100.0, 40.0), (120.0, 20.0), (140.0, 10.0)]
A, B, C = range(3)


def test_escolhe_a_rota_equilibrada_com_pesos_iguais():
    assert escolher_rota_compromisso(FRONTEIRA, [A, B, C]) == B


def test_pontuacao_confere_com_calculo_manual():
    pontuacoes = pontuar_compromisso(FRONTEIRA, [A, B, C])
    assert pontuacoes[A] == pytest.approx(0.5**0.5)
    assert pontuacoes[B] == pytest.approx((0.5 * 0.25 + 0.5 * (1 / 3) ** 2) ** 0.5)
    assert pontuacoes[C] == pytest.approx(0.5**0.5)


def test_peso_um_escolhe_menor_distancia_e_peso_zero_menor_pedagio():
    assert escolher_rota_compromisso(FRONTEIRA, [A, B, C], peso_distancia=1.0) == A
    assert escolher_rota_compromisso(FRONTEIRA, [A, B, C], peso_distancia=0.0) == C


def test_empate_vence_a_menor_distancia():
    objetivos = [(10.0, 0.0), (0.0, 10.0)]
    assert escolher_rota_compromisso(objetivos, [0, 1]) == 1


def test_usa_apenas_a_fronteira_informada():
    objetivos = [(100.0, 40.0), (120.0, 20.0), (140.0, 10.0), (1.0, 1.0)]
    assert escolher_rota_compromisso(objetivos, [A, B, C]) == B


def test_fronteira_com_um_ponto_ou_objetivo_constante():
    assert escolher_rota_compromisso([(5.0, 5.0)], [0]) == 0
    assert escolher_rota_compromisso([(5.0, 3.0), (5.0, 1.0)], [0, 1], 0.5) == 1


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        escolher_rota_compromisso(FRONTEIRA, [])
    with pytest.raises(ValueError):
        escolher_rota_compromisso(FRONTEIRA, [A, B], peso_distancia=1.5)
