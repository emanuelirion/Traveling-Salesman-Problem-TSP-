# Entregas intermunicipais com pedágio — TSP multiobjetivo com NSGA-II

Uma transportadora regional atende várias cidades com **um caminhão** que sai da sede, passa por todas e volta. Cada trecho tem uma **distância (km)** e um **pedágio (R$)**; rodovias pedagiadas costumam ser mais curtas, e estradas sem pedágio alongam o caminho. O gerente de logística precisa conhecer as **melhores trocas entre quilômetros e pedágio** antes de escolher a rota.

Este projeto modela o problema como um **Traveling Salesman Problem (TSP) bi-objetivo** e o resolverá com o algoritmo **NSGA-II**. A entrega será:

1. o **conjunto de rotas não dominadas** (aproximação da fronteira de Pareto), com a distância e o pedágio de cada rota;
2. **uma rota escolhida** desse conjunto, com critério definido e justificado.

|                |                                                                                         |
| -------------- | --------------------------------------------------------------------------------------- |
| **Problema**   | TSP tradicional: um veículo, grafo completo, cada cidade visitada uma vez, volta à sede |
| **Categoria**  | Multiobjetivo                                                                           |
| **Objetivos**  | (1) minimizar a distância total; (2) minimizar o pedágio total                          |
| **Restrições** | Cada cidade recebe exatamente uma visita; a rota começa e termina na sede               |
| **Algoritmo**  | NSGA-II (Deb et al., 2002)                                                              |

## Estado do projeto (checkpoint de 15/10/2026)

| Etapa                                         | Situação                                                   |
| --------------------------------------------- | ---------------------------------------------------------- |
| Modelagem do problema                         | **Concluída**, em [`docs/MODELAGEM.md`](docs/MODELAGEM.md) |
| Estrutura do repositório e README             | **Concluída** (este arquivo)                               |
| Implementação do NSGA-II (`src/`, `scripts/`) | Planejada, ainda não iniciada                              |
| Testes e validação (`tests/`)                 | Planejados                                                 |
| Instâncias e resultados (`data/`, `results/`) | Planejados                                                 |

---

## 1. Modelagem do problema

A modelagem completa está em **[`docs/MODELAGEM.md`](docs/MODELAGEM.md)**. Resumo:

- **Grafo:** completo e não direcionado. O vértice 0 é a sede; os vértices 1..N são as cidades. Cada aresta tem dois pesos: $d_{ij}$ (km) e $p_{ij}$ (R$).
- **Variáveis:** $x_{ij}\in\{0,1\}$ (o caminhão vai de $i$ direto para $j$) e $u_i$ (ordem de visita, para evitar sub-rotas, formulação MTZ).
- **Objetivos:** $\min f_1=\sum d_{ij}x_{ij}$ e $\min f_2=\sum p_{ij}x_{ij}$.
- **Restrições:** grau de entrada e de saída igual a 1 em todo vértice (cada cidade visitada uma vez) e eliminação de sub-rotas (a rota fecha na sede).
- **Dominância:** a rota A domina a B se não é pior em nenhum objetivo e é melhor em ao menos um. O conjunto das rotas não dominadas é a fronteira de Pareto.
- **Codificação no NSGA-II:** o cromossomo é uma **permutação das N cidades**, com a sede implícita nas pontas. Assim as restrições valem por construção, sem penalidade nem reparo.
- **Operadores:** torneio binário por multidão, cruzamento OX, mutação por inversão (2-opt) ou troca, sobrevivência $(\mu+\mu)$ com ordenação não dominada e distância de multidão.
- **Critério de escolha da rota:** a rota **mais próxima do ponto ideal normalizado** (menor km e menor pedágio da fronteira), com pesos configuráveis (padrão 50/50). Justificativa e alternativas descartadas na seção 7 de `docs/MODELAGEM.md`.

---

## 2. Organização do repositório

```
tsp-multiobjetivo-nsga2/
├── README.md                  ← este arquivo
├── .gitignore
├── docs/
│   └── MODELAGEM.md           ← modelagem completa (matemática, NSGA-II, critério de escolha, validação)
├── src/                       ← código-fonte do NSGA-II (a implementar)
│   └── README.md
├── scripts/                   ← programas de linha de comando (a implementar)
│   └── README.md
├── data/                      ← instâncias de entrada em CSV
│   └── README.md
├── results/                   ← saídas das execuções
│   └── README.md
└── tests/                     ← testes automatizados (a implementar)
    └── README.md
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

### Formato das saídas (previsto)

| Arquivo               | Conteúdo                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------ |
| `pareto.csv`          | **Conjunto de rotas não dominadas**: distância (km), pedágio (R$) e sequência de vértices de cada rota |
| `rota_escolhida.json` | Rota escolhida: critério, pesos, totais e trechos                                                      |
| `pareto.png`          | Fronteira de Pareto (km × R$) com a rota escolhida destacada                                           |
| `rota_escolhida.png`  | Mapa da rota                                                                                           |
| `convergencia.png`    | Hipervolume por geração                                                                                |

---

## 3. Plano para as próximas etapas

1. Implementar o grafo, a avaliação das duas funções-objetivo e o gerador de instâncias sintéticas (seção 8 da modelagem).
2. Implementar ordenação não dominada, distância de multidão e hipervolume.
3. Implementar os operadores (população inicial, OX, mutação) e o laço do NSGA-II.
4. Implementar o critério de escolha da rota.
5. Validar contra a fronteira exata em instâncias com até 9 cidades e repetir com várias sementes.
6. Gerar as instâncias, rodar os experimentos e preencher `results/` e este README com os resultados.

---

## 4. Dados

Não há dados reais no enunciado. A modelagem prevê **instâncias sintéticas** em que trechos pedagiados têm o caminho direto e custam R$/km, enquanto trechos sem pedágio custam zero mas têm o caminho alongado por um fator de desvio (1,25 a 1,70). Detalhes na seção 8 de `docs/MODELAGEM.md`. Dados reais podem ser usados no mesmo formato CSV.

## 5. Limitações

- Distâncias e pedágios simétricos; pedágio fixo por trecho (sem categorias de eixo ou tarifa variável).
- Apenas os dois objetivos pedidos: não há janelas de tempo, capacidade ou vários veículos.
- O NSGA-II devolve uma **aproximação** da fronteira de Pareto, sem garantia de otimalidade para instâncias grandes.

---

## 6. Equipe

Preencher com nome e matrícula dos integrantes do grupo.

| Nome | Matrícula |
| Emanuel Irion da Rosa | 2310100375 |
| | |

## Referência principal

Deb, K.; Pratap, A.; Agarwal, S.; Meyarivan, T. _A fast and elitist multiobjective genetic algorithm: NSGA-II_. IEEE Transactions on Evolutionary Computation, 6(2), 182–197, 2002.

