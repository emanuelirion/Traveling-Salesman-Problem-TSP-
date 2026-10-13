# Modelagem do problema

**Entregas intermunicipais com pedágio** — TSP multiobjetivo (distância × pedágio) resolvido com NSGA-II.

Este documento descreve **como o problema foi modelado**: dados de entrada, formulação matemática, representação das soluções, adaptação do NSGA-II, critério de escolha da rota final, instâncias, plano de validação e premissas. A seção 11 mostra como a modelagem será dividida em módulos na implementação (etapa seguinte do projeto).

---

## 1. Interpretação do enunciado

| Elemento do enunciado                                                         | Como foi interpretado                                                                                                                                      |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Um caminhão que sai da sede, passa por todas as cidades e volta"             | TSP clássico: um único veículo, ciclo hamiltoniano que começa e termina na sede.                                                                           |
| "Grafo completo"                                                              | Existe um trecho direto entre qualquer par de vértices.                                                                                                    |
| "Cada trecho tem distância e custo de pedágio"                                | Cada aresta $\{i,j\}$ carrega **dois pesos**: $d_{ij}$ (km) e $p_{ij}$ (R$).                                                                               |
| "Rodovias pedagiadas são mais curtas; estradas sem pedágio alongam o caminho" | Há conflito entre os objetivos: reduzir km tende a aumentar pedágio e vice-versa. As instâncias serão geradas de modo a reproduzir essa relação (seção 8). |
| "Cada cidade recebe exatamente uma visita"                                    | Restrição de grau/permutação: cada cidade aparece uma única vez na rota.                                                                                   |
| "A rota começa e termina na sede"                                             | A sede é fixa nas pontas do ciclo.                                                                                                                         |
| "Conjunto de rotas não dominadas"                                             | Aproximação da **fronteira de Pareto** dos dois objetivos.                                                                                                 |
| "Uma rota escolhida, com critério definido e justificado"                     | Critério de compromisso: menor distância ao ponto ideal normalizado (seção 7).                                                                             |

---

## 2. Dados de entrada

Grafo completo não direcionado $G = (V, E)$:

- $V = \{0, 1, \dots, N\}$, onde **0 é a sede** e $C = \{1,\dots,N\}$ são as **$N$ cidades**.
- $E$ contém todas as $\binom{N+1}{2}$ arestas.
- $d_{ij} > 0$: distância do trecho $(i,j)$ em km.
- $p_{ij} \ge 0$: pedágio do trecho $(i,j)$ em R$ ($p_{ij}=0$ para estradas sem pedágio).
- **Simetria:** $d_{ij}=d_{ji}$ e $p_{ij}=p_{ji}$ (o pedágio não depende do sentido; ver premissas, seção 9).

Formato em arquivo (`data/instancias/<nome>/`):

- `cidades.csv`: `id, nome, x_km, y_km` (as coordenadas só servem para desenhar a rota).
- `arestas.csv`: `origem, destino, distancia_km, pedagio_rs`, uma linha por aresta ($i<j$). O grafo precisa estar completo: $n(n-1)/2$ arestas.

---

## 3. Formulação matemática

### 3.1 Variáveis de decisão

- $x_{ij}\in\{0,1\}$, para $i\ne j$: vale 1 se o caminhão vai **diretamente de $i$ para $j$**.
- $u_i \in \mathbb{R}$, para $i\in C$: posição da cidade $i$ na rota (eliminação de sub-rotas, formulação de Miller–Tucker–Zemlin).

### 3.2 Objetivos (ambos minimizados)

$$
\min\; f_1(x)=\sum_{i\in V}\sum_{j\in V,\,j\ne i} d_{ij}\,x_{ij}
\qquad\text{(distância total, km)}
$$

$$
\min\; f_2(x)=\sum_{i\in V}\sum_{j\in V,\,j\ne i} p_{ij}\,x_{ij}
\qquad\text{(pedágio total, R\$)}
$$

### 3.3 Restrições

$$
\sum_{j\ne i} x_{ij}=1\quad \forall i\in V
\qquad\text{(sai exatamente uma vez de cada vértice)}
$$

$$
\sum_{i\ne j} x_{ij}=1\quad \forall j\in V
\qquad\text{(chega exatamente uma vez a cada vértice)}
$$

$$
u_i-u_j+N\,x_{ij}\le N-1\quad \forall i,j\in C,\; i\ne j
\qquad\text{(sem sub-rotas)}
$$

$$
1\le u_i\le N\quad\forall i\in C
$$

As duas primeiras garantem **"cada cidade recebe exatamente uma visita"** e que a sede tem uma saída e uma chegada; a terceira impede ciclos que não passem pela sede, o que garante **"a rota começa e termina na sede"**. O modelo é um TSP com duas funções-objetivo, portanto NP-difícil.

### 3.4 Tamanho do espaço de busca

Fixada a sede, cada solução é uma permutação das $N$ cidades: $N!$ rotas. Como as matrizes são simétricas, uma rota e a sua inversa têm os mesmos objetivos, então há $N!/2$ resultados distintos ($N\ge3$). Para $N=20$ são cerca de $1{,}2\times10^{18}$ rotas diferentes, o que inviabiliza enumeração e justifica uma metaheurística.

---

## 4. Conceitos multiobjetivo

Seja $F(r)=(f_1(r),f_2(r))$ o vetor de objetivos da rota $r$.

- **Dominância:** $r_a$ domina $r_b$ ($r_a \prec r_b$) se $f_k(r_a)\le f_k(r_b)$ para $k=1,2$ e $f_k(r_a)<f_k(r_b)$ para ao menos um $k$.
- **Conjunto de Pareto:** rotas viáveis que nenhuma outra rota viável domina.
- **Fronteira de Pareto:** imagem desse conjunto no espaço (km, R$).

Não existe uma "melhor rota" única: a rota de menor distância costuma ser a de maior pedágio, e a de pedágio zero é a mais longa. A fronteira mostra ao gerente **quanto de pedágio cada quilômetro economizado custa**, que é a troca que ele quer conhecer.

---

## 5. Modelagem para o NSGA-II

### 5.1 Representação (cromossomo)

Uma solução é uma **permutação das $N$ cidades** (vetor de inteiros de 1 a $N$). O ciclo completo é `[0] + permutação + [0]`.

Por que essa codificação:

- **As restrições são satisfeitas por construção.** Toda permutação visita cada cidade uma vez e a sede fica fixa nas pontas. Não há penalidade nem reparo.
- **A sede fora do cromossomo** elimina soluções equivalentes por rotação do ciclo e reduz o espaço de busca de $(N+1)!$ para $N!$.

### 5.2 Avaliação

Para um cromossomo $\pi=(\pi_1,\dots,\pi_N)$ com $\pi_0=\pi_{N+1}=0$:

$$
f_1(\pi)=\sum_{k=0}^{N} d_{\pi_k\pi_{k+1}},\qquad
f_2(\pi)=\sum_{k=0}^{N} p_{\pi_k\pi_{k+1}}
$$

Custo $O(N)$ por rota. A avaliação é vetorizada com NumPy para a população inteira.

### 5.3 Fluxo do algoritmo

```
1. P0 ← população inicial (tamanho μ); avaliar
2. para g = 1 … G:
3.     calcular posto (fronteira) e distância de multidão de cada indivíduo de P
4.     selecionar μ pais por torneio binário (comparação por multidão)
5.     gerar μ filhos por cruzamento OX (prob. pc) e mutação (prob. pm); avaliar
6.     R ← P ∪ filhos          (2μ indivíduos, elitismo)
7.     ordenar R em fronteiras F1, F2, … (ordenação não dominada)
8.     P ← preencher fronteira a fronteira até μ;
        na última fronteira que não cabe, ficam os de maior distância de multidão
9. retornar F1 de P (conjunto não dominado)
```

### 5.4 Componentes

| Componente                 | Escolha                                                                                                                           | Justificativa                                                                                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **População inicial**      | Aleatória, com até 11 indivíduos (≤ 20%) gerados pela heurística do _vizinho mais próximo_ com pesos de 0 a 1 entre km e pedágio. | Os extremos da fronteira são difíceis de alcançar por sorteio; as sementes cobrem as pontas e o restante mantém diversidade. |
| **Seleção de pais**        | Torneio binário com _crowded-comparison_: menor posto vence; empate → maior distância de multidão.                                | Operador original do NSGA-II; pressão por convergência e por diversidade.                                                    |
| **Cruzamento**             | _Order Crossover_ (OX), prob. $p_c=0{,}9$.                                                                                        | Preserva a ordem relativa das cidades e sempre gera permutações válidas.                                                     |
| **Mutação**                | Inversão de segmento (equivale a um movimento 2-opt) ou troca de duas cidades, 50% cada; prob. $p_m=0{,}3$ por filho.             | Inversão corrige cruzamentos de arestas; a troca dá variação pontual.                                                        |
| **Ordenação não dominada** | Divide $R$ em fronteiras sucessivas. $O(M\,(2\mu)^2)$ com $M=2$.                                                                  | NSGA-II original.                                                                                                            |
| **Distância de multidão**  | Soma, por objetivo, da distância normalizada entre os vizinhos; extremos recebem $\infty$.                                        | Mantém a fronteira espalhada e preserva as pontas.                                                                           |
| **Sobrevivência**          | $(\mu+\mu)$ com elitismo.                                                                                                         | Nenhuma solução não dominada se perde (o hipervolume nunca diminui, pelo elitismo).                                          |
| **Duplicatas**             | Mantém uma solução por ponto distinto do espaço de objetivos (inclui rotas espelhadas).                                           | Evita que cópias ocupem a população e achatem a fronteira.                                                                   |
| **Parada**                 | Número fixo de gerações $G$.                                                                                                      | Simples e reprodutível; a curva de convergência (hipervolume por geração) permitirá verificar se $G$ foi suficiente.         |

### 5.5 Parâmetros padrão

| Parâmetro                                | Valor inicial |
| ---------------------------------------- | ------------- |
| Tamanho da população $\mu$               | 100           |
| Gerações $G$                             | 300           |
| Prob. de cruzamento $p_c$                | 0,9           |
| Prob. de mutação $p_m$ (por filho)       | 0,3           |
| Semente aleatória                        | 1             |
| Peso da distância no critério de escolha | 0,5           |

---

## 6. Saída: conjunto de rotas não dominadas

Para cada execução, o programa a ser implementado entregará (em `results/<instância>/`):

- `pareto.csv`: uma linha por rota não dominada, com `distancia_km`, `pedagio_rs` e a sequência de vértices.
- `pareto.png`: a fronteira no plano km × R$, com a rota escolhida destacada.

O conjunto é ordenado por distância crescente, portanto o pedágio é decrescente.

---

## 7. Critério de escolha da rota final

### 7.1 Definição

**Rota de compromisso: a mais próxima do ponto ideal, no espaço normalizado.**

1. Normalizar cada objetivo pela amplitude da fronteira:
   $z_k=\dfrac{f_k-\min f_k}{\max f_k-\min f_k}$.
2. O ponto ideal é $(0,0)$: menor distância e menor pedágio já encontrados na fronteira.
3. Escolher a rota que minimiza

$$
\sqrt{w_d\,z_1^2+w_p\,z_2^2},\qquad w_d+w_p=1,\; w_d=w_p=0{,}5\text{ por padrão}
$$

Em caso de empate, vence a rota de menor distância.

### 7.2 Justificativa

- **Não depende das unidades.** Km e reais não são comparáveis diretamente; a normalização evita que o objetivo de maior magnitude domine a escolha.
- **Não exige converter km em reais.** O gerente não precisa informar custo de combustível, motorista ou depreciação por km.
- **Escolhe uma rota equilibrada.** Rotas dos extremos (só km ou só pedágio) têm valor normalizado 1 no objetivo sacrificado e são penalizadas; a escolhida não sacrifica totalmente nenhum dos dois.
- **Um parâmetro interpretável.** O gerente ajusta $w_d$ conforme a política da empresa: $w_d\to1$ prioriza quilometragem (prazo, combustível) e $w_d\to0$ prioriza economia de pedágio. Com $w_d=1$ ou $0$ o critério recai nas pontas da fronteira.
- **Determinístico e auditável.** Mesma fronteira e mesmos pesos dão sempre a mesma rota, e o arquivo de saída da rota escolhida registrará critério, pesos, trechos e totais.

### 7.3 Alternativas consideradas

| Alternativa                                                     | Por que não foi adotada                                                                                                    |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Soma ponderada dos valores brutos ($\alpha\cdot$km $+$ pedágio) | Exige o custo operacional por km, que o enunciado não fornece. Pode ser usada como variante se a empresa tiver esse valor. |
| Ponto de joelho (maior curvatura da fronteira)                  | Sensível a ruído e a fronteiras com vários "joelhos"; não permite expressar preferência.                                   |
| Escolha lexicográfica (menor km, desempate por pedágio)         | Ignora o segundo objetivo e devolve a ponta da fronteira.                                                                  |
| Restrição de orçamento (menor km com pedágio ≤ teto)            | Útil quando há teto de gasto, mas ele não faz parte do enunciado.                                                          |

### 7.4 Limitação

A normalização usa a amplitude da própria fronteira encontrada. Se a fronteira for pouco explorada nas pontas, o ponto ideal normalizado muda ligeiramente. Por isso o plano é semear o NSGA-II com soluções de extremo e conferir o resultado com várias sementes.

---

## 8. Instâncias

Não há dados reais no enunciado, então o plano é usar um **gerador de instâncias sintéticas** que reproduza a relação km × pedágio descrita:

1. Sorteia as coordenadas da sede e das cidades em uma área quadrada (padrão 300 × 300 km).
2. Calcula a distância em linha reta $e_{ij}$ entre cada par.
3. Com probabilidade $p_{toll}=0{,}5$ o trecho é **rodovia pedagiada**: $d_{ij}=e_{ij}$ e $p_{ij}=e_{ij}\cdot\tau$, com $\tau\sim U(0{,}30;\,0{,}80)$ R$/km.
4. Caso contrário é **estrada sem pedágio**: $p_{ij}=0$ e $d_{ij}=e_{ij}\cdot\delta$, com $\delta\sim U(1{,}25;\,1{,}70)$ (desvio que alonga o caminho).

Resultado: trechos pagos são mais curtos e trechos gratuitos são mais longos, o que cria o conflito entre os objetivos. Os parâmetros serão ajustáveis e uma semente garantirá reprodutibilidade. Dados reais podem ser usados desde que estejam no formato CSV da seção 2.

Observação: esse gerador não impõe a desigualdade triangular, o que é coerente com rodovias reais, em que o trecho direto pode ser mais longo que uma passagem por outra cidade.

---

## 9. Premissas e limitações

- **Distâncias e pedágios simétricos.** Na prática o pedágio pode variar com o sentido ou o horário. Para tratar o caso assimétrico, seria preciso trocar as matrizes por valores direcionais; a representação e o algoritmo não mudam.
- **Pedágio por trecho, valor fixo.** Não se modelam categorias de eixos, desconto por frequência ou tarifas variáveis.
- **Pedágio e distância são os únicos custos.** Não há janelas de tempo, capacidade do caminhão, demanda por cidade nem múltiplos veículos, pois o enunciado define o TSP tradicional.
- **Grafo completo.** O trecho direto entre qualquer par existe, mesmo que na prática passe por outras cidades.
- **Aproximação.** O NSGA-II é uma metaheurística: devolve uma aproximação da fronteira de Pareto, sem garantia de otimalidade para $N$ grande.

---

## 10. Plano de validação e métricas

**Corretude** (testes automatizados previstos em `tests/`):

- operadores sempre geram permutações válidas;
- ordenação não dominada, distância de multidão e hipervolume conferidos com valores calculados à mão;
- objetivos reportados batem com uma reavaliação independente, e nenhuma rota do conjunto domina outra;
- a mesma semente produz o mesmo resultado.

**Qualidade da aproximação:**

- **Comparação com a fronteira exata.** Para $N\le9$ a fronteira verdadeira pode ser calculada por força bruta ($9!=362\,880$ permutações) e comparada com a obtida pelo NSGA-II.
- **Hipervolume.** Mede convergência e diversidade em um só número (maior é melhor), acompanhado por geração.
- **Várias sementes.** Repetir a execução e reportar média e desvio do hipervolume com um ponto de referência comum.

---

## 11. Módulos previstos para a implementação

| Elemento da modelagem                                                                 | Módulo previsto |
| ------------------------------------------------------------------------------------- | --------------- |
| Grafo, matrizes $d$ e $p$, avaliação $f_1,f_2$, gerador de instâncias, leitura de CSV | `src/instance`  |
| Dominância, ordenação não dominada, distância de multidão, hipervolume                | `src/pareto`    |
| Inicialização, cruzamento OX, mutação                                                 | `src/operators` |
| Laço do NSGA-II, torneio, sobrevivência, parâmetros                                   | `src/nsga2`     |
| Critério de escolha da rota (seção 7)                                                 | `src/selection` |
| Fronteira exata por enumeração (validação)                                            | `src/exact`     |
| Gráficos                                                                              | `src/plotting`  |

---

## Referências

- Deb, K.; Pratap, A.; Agarwal, S.; Meyarivan, T. _A fast and elitist multiobjective genetic algorithm: NSGA-II_. IEEE Transactions on Evolutionary Computation, 6(2), 182–197, 2002.
- Miller, C. E.; Tucker, A. W.; Zemlin, R. A. _Integer programming formulation of traveling salesman problems_. Journal of the ACM, 7(4), 326–329, 1960.
- Davis, L. _Applying adaptive algorithms to epistatic domains_. IJCAI, 1985 (Order Crossover).
- Zitzler, E.; Thiele, L. _Multiobjective evolutionary algorithms: a comparative case study and the strength Pareto approach_. IEEE Transactions on Evolutionary Computation, 3(4), 257–271, 1999 (hipervolume).
