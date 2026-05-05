"""
Valida que o grafo da obra é um DAG (sem ciclos) e que todas as referências
em "Entra após" apontam para IDs existentes.

Pode ser usado como módulo (validate(tasks)) ou como CLI:

    python validate_dag.py caminho/para/obra.xlsx
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

from .model import Task, build_graph, load_tasks_from_excel, task_by_id


class GraphValidationError(Exception):
    """Levantada quando o grafo não passa nas validações."""


def validate(tasks: list[Task]) -> nx.DiGraph:
    """
    Valida e devolve o grafo construído.

    Verifica:
    - IDs únicos
    - Predecessores referenciam IDs existentes
    - Grafo é DAG (sem ciclos)
    """
    # 1) IDs únicos
    seen: dict[str, int] = {}
    for t in tasks:
        seen[t.id] = seen.get(t.id, 0) + 1
    duplicates = [tid for tid, n in seen.items() if n > 1]
    if duplicates:
        raise GraphValidationError(f"IDs duplicados: {duplicates}")

    # 2) Predecessores existem
    valid_ids = set(seen.keys())
    for t in tasks:
        for pred in t.entra_apos:
            if pred not in valid_ids:
                raise GraphValidationError(
                    f"Tarefa {t.id} tem predecessor inexistente: {pred!r}"
                )

    # 3) DAG (sem ciclos)
    G = build_graph(tasks)
    if not nx.is_directed_acyclic_graph(G):
        cycles = list(nx.simple_cycles(G))
        raise GraphValidationError(
            f"Grafo contém ciclo(s): {cycles}. "
            f"Revise a coluna 'Entra após' — uma tarefa não pode depender, "
            f"direta ou indiretamente, de si mesma."
        )

    return G


def summary(tasks: list[Task]) -> dict:
    """
    Retorna um dicionário-resumo da validação para apresentação ao usuário.
    """
    by_id = task_by_id(tasks)
    raizes = [t.id for t in tasks if not t.entra_apos]
    folhas = [t.id for t in tasks if not any(t.id in other.entra_apos for other in tasks)]

    return {
        "total_tarefas": len(tasks),
        "tarefas_raiz": raizes,
        "tarefas_finais": folhas,
        "contratados_unicos": sorted(set(t.contratado for t in tasks)),
    }


def _cli():
    if len(sys.argv) < 2:
        print("Uso: python validate_dag.py caminho/para/obra.xlsx")
        sys.exit(1)
    path = Path(sys.argv[1])
    tasks = load_tasks_from_excel(path)
    G = validate(tasks)
    info = summary(tasks)
    print("✅ Grafo válido.")
    print(f"  Tarefas: {info['total_tarefas']}")
    print(f"  Raízes:  {info['tarefas_raiz']}")
    print(f"  Finais:  {info['tarefas_finais']}")
    print(f"  Contratados ({len(info['contratados_unicos'])}): "
          f"{info['contratados_unicos']}")
    print(f"  Arestas: {G.number_of_edges()}")


if __name__ == "__main__":
    _cli()
