from src.nsga2.configuracao import ConfiguracaoNSGA2
from src.nsga2.algoritmo import NSGA2
from src.nsga2.selecao import selecao_ambiental, torneio_por_multidao
from src.gerador import gerar_instancia_teste

# 1. Gera a instância do problema
instancia = gerar_instancia_teste(n_cidades=15, densidade_arestas=0.9, semente=42)

# 2. Define a configuração
config = ConfiguracaoNSGA2(
    tamanho_populacao=50,
    geracoes=100,
    semente=42
)

# Dummy/Placeholder de ordenação para teste
def ordenacao_simples(objetivos, violacoes):
    # Retorna os índices organizados em uma única frente para teste
    factiveis = sorted(range(len(objetivos)), key=lambda i: (violacoes[i], objetivos[i][0] + objetivos[i][1]))
    return [factiveis]

def multidao_simples(objetivos, frente):
    return {idx: 1.0 for idx in frente}

# 3. Instancia e executa o NSGA-II
algoritmo = NSGA2(
    instancia=instancia,
    configuracao=config,
    ordenar_fn=ordenacao_simples,
    multidao_fn=multidao_simples
)

resultado = algoritmo.executar()

print(f"Execução concluída! Quantidade de rotas na fronteira final: {len(resultado.fronteira_final)}")
if resultado.fronteira_final:
    melhor_idx = resultado.fronteira_final[0]
    print(f"Exemplo de Rota: {resultado.rotas[melhor_idx]}")
    print(f"Avaliação: Distância = {resultado.avaliacoes[melhor_idx].distancia} km, "
          f"Pedágio = R$ {resultado.avaliacoes[melhor_idx].pedagio}, "
          f"Violações = {resultado.avaliacoes[melhor_idx].violacoes}")