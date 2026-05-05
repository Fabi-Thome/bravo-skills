"""
Forward pass: calcula entrada/saída projetada de cada tarefa.

Regras:
1. Se a tarefa tem entrada_real, usa entrada_real como ponto de partida.
2. Senão, entrada_projetada = max(entrada_planejada, max(saída projetada dos predecessores)).
3. Se a tarefa tem saida_real, usa saida_real (a tarefa terminou).
4. Senão, saida_projetada = entrada_projetada + duração planejada original.

A duração planejada (saida_planejada - entrada_planejada) é preservada.
"""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

from .model import Task, task_by_id


def forward_pass(tasks: list[Task], graph: nx.DiGraph) -> list[Task]:
    """
    Calcula entrada_projetada e saida_projetada para cada tarefa.
    Modifica as tarefas in-place e devolve a mesma lista.

    Pré-requisito: graph é um DAG (use validate primeiro).
    """
    by_id = task_by_id(tasks)

    for node_id in nx.topological_sort(graph):
        t = by_id[node_id]

        # Determinar entrada projetada
        candidatos = []

        # Início mais cedo possível pela data planejada
        if t.entrada_planejada is not None:
            candidatos.append(t.entrada_planejada)

        # Início pelos predecessores
        for pred_id in graph.predecessors(node_id):
            pred = by_id[pred_id]
            saida_pred = pred.saida_projetada or pred.saida_real or pred.saida_planejada
            if saida_pred is not None:
                candidatos.append(saida_pred)

        if t.entrada_real is not None:
            t.entrada_projetada = t.entrada_real
        elif candidatos:
            t.entrada_projetada = max(candidatos)
        else:
            t.entrada_projetada = t.entrada_planejada

        # Determinar saída projetada
        if t.saida_real is not None:
            t.saida_projetada = t.saida_real
        elif t.entrada_projetada is not None:
            duracao = t.duracao_planejada
            t.saida_projetada = t.entrada_projetada + timedelta(days=duracao)

    return tasks


def project_completion_date(tasks: list[Task], graph: nx.DiGraph):
    """
    Data projetada de término da obra: maior saída projetada entre as tarefas finais
    (sem sucessores no grafo).
    """
    by_id = task_by_id(tasks)
    finais = [n for n in graph.nodes if graph.out_degree(n) == 0]
    saidas = [by_id[n].saida_projetada for n in finais if by_id[n].saida_projetada]
    return max(saidas) if saidas else None


__all__ = ["forward_pass", "project_completion_date"]
