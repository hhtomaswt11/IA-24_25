# Inteligência Artificial - Universidade do Minho

(Ano letivo 2024/2025)  
### Projeto Final - Resolução de Problemas com Algoritmos de Procura

#### Avaliação Final: 15/20

---
*Grupo 07*

- Pedro Vieira - A104352
- Tomás Melo - A104529  
- Pedro Pinto - A104176
- Marco Brito - A104187

Projeto desenvolvido no âmbito da unidade curricular de **Inteligência Artificial**, no 1.º semestre do 3.º ano da Licenciatura em Engenharia Informática.

---

## Objetivo do Trabalho Prático

Este projeto tem como objetivo o desenvolvimento de **algoritmos de procura**, com aplicação à **distribuição otimizada de recursos (como alimentos, água e medicamentos)** em zonas afetadas por uma catástrofe natural. 

O sistema deve garantir a entrega eficiente e rápida dos suprimentos, respeitando as limitações dos veículos, as prioridades das zonas e as condições ambientais em constante mudança.

---

## Descrição Geral

Durante uma situação de emergência, diferentes veículos (drones, camiões, barcos, etc.) são utilizados para entregar recursos a zonas com diferentes graus de necessidade. O sistema desenvolvido visa:

- Maximizar o número de pessoas assistidas.
- Minimizar o desperdício de recursos.
- Lidar com limitações de carga, combustível e tempo.
- Priorizar zonas mais críticas com base na gravidade da situação.

---

## Tarefas Realizadas

- **Formulação do problema como um problema de procura**, incluindo estado inicial, operadores, teste objetivo e função de custo.
- **Modelação do cenário como um grafo**, representando zonas e rotas possíveis.
- **Implementação e comparação de algoritmos de procura informada e não informada**, com e sem condições variáveis.
- **Simulação de obstáculos dinâmicos**, como mudanças meteorológicas ou bloqueios de rotas.
- **Gestão de prioridades e janelas de tempo críticas** por zona.
- **Otimização do uso de combustível e carga dos veículos**.

---

## Ferramentas e Tecnologias

- Linguagem: Python  
- Biblioteca(s): `networkx`, `matplotlib`, `heapq`, etc.  
- Simulação de ambiente dinâmico baseada em alterações de grafos e heurísticas.

