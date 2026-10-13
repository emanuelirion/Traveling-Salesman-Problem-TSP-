# src/

Código-fonte do NSGA-II. **A implementar** após o checkpoint.

Módulos previstos (ver seção 11 de [`../docs/MODELAGEM.md`](../docs/MODELAGEM.md)):

| Módulo      | Responsabilidade                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------------------- |
| `instance`  | Grafo, matrizes de distância e pedágio, avaliação dos dois objetivos, gerador e leitura de instâncias |
| `pareto`    | Dominância, ordenação não dominada, distância de multidão, hipervolume                                |
| `operators` | População inicial, cruzamento OX, mutação                                                             |
| `nsga2`     | Laço principal, torneio, sobrevivência, parâmetros                                                    |
| `selection` | Critério de escolha da rota (ponto ideal normalizado)                                                 |
| `exact`     | Fronteira exata por enumeração, para validação com até 9 cidades                                      |
| `plotting`  | Gráficos da fronteira, da rota e da convergência                                                      |
