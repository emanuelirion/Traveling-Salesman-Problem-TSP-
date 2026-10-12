# Entregas intermunicipais com pedágio — TSP multiobjetivo com NSGA-II

Uma transportadora regional atende várias cidades com **um caminhão** que sai da sede, passa por todas e volta. Cada trecho tem uma **distância (km)** e um **pedágio (R$)**; rodovias pedagiadas costumam ser mais curtas, e estradas sem pedágio alongam o caminho. O gerente de logística precisa conhecer as **melhores trocas entre quilômetros e pedágio** antes de escolher a rota.

Este projeto resolve o problema como um **Traveling Salesman Problem (TSP) bi-objetivo** com o algoritmo **NSGA-II** e entrega:

1. o **conjunto de rotas não dominadas** (aproximação da fronteira de Pareto), com distância e pedágio de cada rota;
2. **uma rota escolhida** desse conjunto, com critério definido e justificado.

| | |
|---|---|
| **Problema** | TSP tradicional: um veículo, grafo completo, cada cidade visitada uma vez, volta à sede |
| **Categoria** | Multiobjetivo |
| **Objetivos** | (1) minimizar a distância total; (2) minimizar o pedágio total |
| **Restrições** | Cada cidade recebe exatamente uma visita; a rota começa e termina na sede |
| **Algoritmo** | NSGA-II (Deb et al., 2002) |

---
