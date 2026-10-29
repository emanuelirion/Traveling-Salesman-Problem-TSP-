# Entregas intermunicipais com pedágio — TSP multiobjetivo com NSGA-II

Uma transportadora regional atende várias cidades com **um caminhão** que sai da sede, passa por todas e volta. Cada trecho tem uma **distância (km)** e um **pedágio (R$)**; rodovias pedagiadas costumam ser mais curtas, e estradas sem pedágio alongam o caminho. O gerente de logística precisa conhecer as **melhores trocas entre quilômetros e pedágio** antes de escolher a rota.

Este projeto modela o problema como um **Traveling Salesman Problem (TSP) bi-objetivo** e o resolveu com o algoritmo **NSGA-II**. A entrega contempla:

1. O **conjunto de rotas não dominadas** (aproximação da fronteira de Pareto), com a distância e o pedágio de cada rota;
2. **Uma rota de compromisso escolhida** desse conjunto, fundamentada pelo método do Ponto Ideal Normalizado.

|               |                                                                                         |
| ------------- | --------------------------------------------------------------------------------------- |
| **Problema**   | TSP tradicional: um veículo, grafo completo, cada cidade visitada uma vez, volta à sede |
| **Categoria**  | Multiobjetivo                                                                           |
| **Objetivos**  | (1) minimizar a distância total; (2) minimizar o pedágio total                          |
| **Restrições** | Cada cidade recebe exatamente uma visita; a rota começa e termina na sede               |
| **Algoritmo**  | NSGA-II (Deb et al., 2002)                                                              |

---

## Estado do Projeto (Entrega Final)

| Etapa                                         | Situação                                                     |
| --------------------------------------------- | ------------------------------------------------------------ |
| Modelagem do problema                         | **Concluída**, em [`docs/MODELAGEM.md`](docs/MODELAGEM.md)   |
| Estrutura do repositório e README             | **Concluída** (este arquivo)                                 |
| Implementação do NSGA-II (`src/`, `scripts/`) | **Concluída** e modularizada                                 |
| Testes e validação (`tests/`)                 | **Concluídos** (validação via Força Bruta e Crowding Dist.)  |
| Instâncias e resultados (`data/`, `results/`) | **Concluídos** (gráficos de Pareto, Hipervolume e CSVs)      |

---

## 1. Modelagem do Problema

A modelagem completa está em **[`docs/MODELAGEM.md`](docs/MODELAGEM.md)**. Resumo:

- **Grafo:** completo e não direcionado. O vértice 0 é a sede; os vértices 1..N são as cidades. Cada aresta tem dois pesos: $d_{ij}$ (km) e $p_{ij}$ (R$).
- **Variáveis:** $x_{ij}\in\{0,1\}$ (o caminhão vai de $i$ direto para $j$) e $u_i$ (ordem de visita, para evitar sub-rotas, formulação MTZ).
- **Objetivos:** $\min f_1=\sum d_{ij}x_{ij}$ e $\min f_2=\sum p_{ij}x_{ij}$.
- **Restrições:** grau de entrada e de saída igual a 1 em todo vértice (cada cidade visitada uma vez) e eliminação de sub-rotas (a rota fecha na sede).
- **Dominância:** a rota A domina a B se não é pior em nenhum objetivo e é melhor em ao menos um. O conjunto das rotas não dominadas é a fronteira de Pareto.
- **Codificação no NSGA-II:** o cromossomo é uma **permutação das N cidades**, com a sede implícita nas pontas. As restrições valem por construção.
- **Operadores:** torneio binário por multidão, cruzamento OX, mutação por inversão/troca, sobrevivência $(\mu+\mu)$ com ordenação não dominada e distância de multidão (*Crowding Distance*).
- **Critério de Escolha da Rota:** **Método do Ponto Ideal Normalizado** (Min-Max + Distância Euclidiana até $[0, 0]$), identificando a "rota de compromisso" localizada no cotovelo (*knee*) da fronteira de Pareto.

---

## 2. Organização do Repositório

```
Traveling-Salesman-Problem-TSP/
├── README.md                      <- este arquivo
├── .gitignore
├── docs/
│   └── MODELAGEM.md               <- modelagem completa (matemática, NSGA-II, critério de escolha, validação)
├── src/                           <- código-fonte do NSGA-II
│   ├── README.md
│   ├── nsga2/
│   │   ├── algoritmo.py
│   │   ├── compromisso.py
│   │   ├── configuracao.py
│   │   ├── ordenacao.py
│   │   └── selecao.py
│   └── operators/
│       ├── contratos.py
│       ├── cruzamento.py
│       ├── inicializacao.py
│       ├── instancia.py
│       ├── mutacao.py
│       └── reparo.py
├── scripts/                       <- programas de linha de comando
│   ├── README.md
│   ├── main.py
│   ├── run_experimentos.py
│   ├── experimentos.py
│   └── gerador.py
├── data/                          <- instâncias de entrada em CSV
│   └── README.md
├── results/                       <- saídas das execuções
│   └── README.md
└── tests/                         <- testes automatizados
    ├── README.md
    ├── test_compromisso.py
    └── test_ordenacao.py
```

| Pasta / arquivo | Papel                                                                                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/`         | Documentação de projeto. É onde está a modelagem.                                                                                                          |
| `src/`          | Lógica do algoritmo, em módulos: grafo e avaliação, Pareto, operadores, laço do NSGA-II, critério de escolha (módulos previstos na seção 11 da modelagem). |
| `scripts/`      | Pontos de entrada para gerar instâncias, executar o algoritmo e comparar sementes.                                                                         |
| `data/`         | Entradas em CSV. Cada instância é uma pasta com `cidades.csv` e `arestas.csv`.                                                                             |
| `results/`      | Saídas geradas pelos scripts (rotas não dominadas, rota escolhida, gráficos).                                                                              |
| `tests/`        | Verificação dos operadores, do cálculo de Pareto e comparação com a solução exata em instâncias pequenas.                                                  |

Cada pasta tem um `README.md` curto explicando o que vai nela, o que também mantém a pasta visível no GitHub.

### Formato dos dados (definido na modelagem)

`arestas.csv` — grafo completo, uma linha por aresta ($i<j$):

```csv
origem,destino,distancia_km,pedagio_rs
0,1,81.598,34.812
0,2,373.724,0.000
...
```

`cidades.csv` — `id,nome,x_km,y_km` (o id 0 é a sede; as coordenadas só servem para desenhar a rota).

---

## 3. Formato das Saídas Geradas

Cada execução armazena em `results/<nome_instancia>/`:

| Arquivo       | Conteúdo                                                                               |
| ------------- | -------------------------------------------------------------------------------------- |
| `pareto.csv`  | Conjunto de rotas não dominadas, com distância, pedágio, flag `eh_escolhida` e ordem.  |
| `pareto.png`  | Gráfico da Fronteira de Pareto ($km \times R\$$) com a Rota de Compromisso destacada.  |
| `convergencia.png` | Evolução do Hipervolume por geração ao longo de múltiplas sementes.               |

---

## 4. Validação Experimental e Resultados

O algoritmo foi validado empiricamente sob três perspectivas de análise:

1. **Convergência (Hipervolume):** Acompanhamento do crescimento do hipervolume ao longo das gerações com diferentes sementes (10, 42, 99), demonstrando a estabilidade e rápida convergência do NSGA-II.
2. **Qualidade da Diversidade (Crowding Distance):** Comparação experimental provando que a preservação da distância de multidão garante uma distribuição uniforme das soluções ao longo de toda a fronteira.
3. **Aproximação da Fronteira Exata:** Testado em instâncias de até 9 cidades contra a busca por **Força Bruta**, comprovando que o NSGA-II encontra soluções praticamente idênticas às ótimas globais.

---

## 5. Limitações

- Distâncias e pedágios simétricos; pedágio fixo por trecho.
- Restrito aos dois objetivos definidos (não considera janelas de tempo nem frota múltipla).
- Por tratar-se de uma meta-heurística, o NSGA-II garante aproximação de alta qualidade da fronteira de Pareto, mas sem prova analítica de otimalidade em instâncias de grande escala.

---

## 6. Equipe

Trabalho desenvolvido para a entrega do Checkpoint e Entrega Final:

| Nome | Matrícula |
| :--- | :--- |
| Emanuel Irion da Rosa | 2310100375 |
| Fabiano Mion | Matrícula |
| Hanna Mendonça | 2510101034 |
| Renata Bedinotto | 2410200496 |

## Referência Principal

Deb, K.; Pratap, A.; Agarwal, S.; Meyarivan, T. _A fast and elitist multiobjective genetic algorithm: NSGA-II_. IEEE Transactions on Evolutionary Computation, 6(2), 182–197, 2002.
