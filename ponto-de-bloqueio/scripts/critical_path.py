"""
Backward pass + cálculo de folga + identificação do caminho crítico.

Pré-requisito: forward_pass já foi rodado (entrada/saída projetadas existem).

Algoritmo:
1. Define a data de término da obra = max das saídas projetadas dos sinks.
2. Backward pass: para cada nó (em ordem topológica reversa):
     saida_limite = min(entrada_limite dos sucessores), ou data da obra se for sink
     entrada_limite = saida_limite - duração planejada
3. Folga = saida_limite - saida_projetada (em dias).
4. Caminho crítico = sequência de tarefas com folga zero, conectadas, do início ao fim.
"""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

from .forward_pass import project_completion_date
from .model import Task, task_by_id


def backward_pass(tasks: list[Task], graph: nx.DiGraph) -> list[Task]:
    """
    Calcula entrada_limite, saida_limite e folga para cada tarefa.
    Modifica as tarefas in-place.
    """
    by_id = task_by_id(tasks)
    obra_fim = project_completion_date(tasks, graph)
    if obra_fim is None:
        return tasks

    # Iteração na ordem topológica reversa
    for node_id in reversed(list(nx.topological_sort(graph))):
        t = by_id[node_id]

        sucessores = list(graph.successors(node_id))
        if not sucessores:
            t.saida_limite = obra_fim
        else:
            entradas_limite_sucessores = [
                by_id[s].entrada_limite for s in sucessores
                if by_id[s].entrada_limite is not None
            ]
            if entradas_limite_sucessores:
                t.saida_limite = min(entradas_limite_sucessores)
            else:
                t.saida_limite = obra_fim

        duracao = t.duracao_planejada
        t.entrada_limite = t.saida_limite - timedelta(days=duracao)

        # Folga em dias (positiva = gordura, zero = crítico, negativa = comprometido)
        if t.saida_projetada is not None:
            t.folga = (t.saida_limite - t.saida_projetada).days
        else:
            t.folga = None

    return tasks


def critical_path_ids(tasks: list[Task], graph: nx.DiGraph) -> list[str]:
    """
    Retorna os IDs das tarefas no caminho crítico, em ordem topológica.
    Caminho crítico = todas as tarefas com folga zero, ordenadas.
    """
    by_id = task_by_id(tasks)
    criticos = [n for n in nx.topological_sort(graph) if by_id[n].folga == 0]
    return criticos


def longest_path_ids(tasks: list[Task], graph: nx.DiGraph) -> list[str]:
    """
    Caminho mais longo no grafo (em duração projetada). Equivalente ao caminho crítico
    quando o grafo é "limpo". Útil quando o caminho crítico tem ramificações.
    """
    by_id = task_by_id(tasks)

    # Pesos = duração projetada de cada nó (a saída projetada do nó - entrada projetada)
    G_weighted = graph.copy()
    for node in G_weighted.nodes:
        t = by_id[node]
        if t.entrada_projetada and t.saida_projetada:
            duracao = (t.saida_projetada - t.entrada_projetada).days
        else:
            duracao = t.duracao_planejada
        G_weighted.nodes[node]["duration"] = max(duracao, 0)

    return nx.dag_longest_path(G_weighted, weight="duration")


def biggest_blockers(tasks: list[Task], graph: nx.DiGraph, top_n: int = 5) -> list[dict]:
    """
    Ranking dos contratados/tarefas que mais bloqueiam outras.
    Métrica: nº de descendentes (transitive closure).

    Retorna lista de dicts com {id, contratado, escopo, descendentes_count, no_caminho_critico}.
    """
    by_id = task_by_id(tasks)
    rankings = []

    for node in graph.nodes:
        descendentes = nx.descendants(graph, node)
        t = by_id[node]
        rankings.append({
            "id": t.id,
            "contratado": t.contratado,
            "escopo": t.escopo,
            "descendentes_count": len(descendentes),
            "no_caminho_critico": t.folga == 0 if t.folga is not None else False,
        })

    rankings.sort(key=lambda r: (r["descendentes_count"], r["no_caminho_critico"]), reverse=True)
    return rankings[:top_n]


def tasks_at_risk(tasks: list[Task], folga_limite_dias: int = 3) -> list[Task]:
    """
    Tarefas em risco: folga ≤ folga_limite_dias OU já com desvio positivo (atraso).
    """
    em_risco = []
    for t in tasks:
        if t.esta_concluida:
            continue
        if t.folga is not None and t.folga <= folga_limite_dias:
            em_risco.append(t)
            continue
        if t.desvio_dias is not None and t.desvio_dias > 0:
            em_risco.append(t)
    return em_risco


def analysis_summary(tasks: list[Task], graph: nx.DiGraph) -> dict:
    """
    Resumo completo da análise para apresentação ao usuário.
    """
    by_id = task_by_id(tasks)
    obra_fim = project_completion_date(tasks, graph)
    criticos = critical_path_ids(tasks, graph)

    # data planejada de término = maior saida_planejada das finais
    finais = [n for n in graph.nodes if graph.out_degree(n) == 0]
    saidas_planejadas = [by_id[n].saida_planejada for n in finais if by_id[n].saida_planejada]
    obra_fim_planejado = max(saidas_planejadas) if saidas_planejadas else None

    desvio_obra = None
    if obra_fim and obra_fim_planejado:
        desvio_obra = (obra_fim - obra_fim_planejado).days

    return {
        "total_tarefas": len(tasks),
        "data_termino_planejado": obra_fim_planejado,
        "data_termino_projetado": obra_fim,
        "desvio_obra_dias": desvio_obra,
        "caminho_critico": criticos,
        "tarefas_em_risco": [t.id for t in tasks_at_risk(tasks)],
        "maiores_bloqueadores": biggest_blockers(tasks, graph),
    }


__all__ = [
    "backward_pass",
    "critical_path_ids",
    "longest_path_ids",
    "biggest_blockers",
    "tasks_at_risk",
    "analysis_summary",
]
