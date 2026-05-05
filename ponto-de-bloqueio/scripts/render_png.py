"""
Renderiza o grafo da obra como imagem PNG via matplotlib.

A imagem destina-se a ser anexada em e-mails ou enviada em WhatsApp.

Pré-requisito: forward_pass + backward_pass já rodados.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from .critical_path import tasks_at_risk
from .model import Task, task_by_id


COLOR_CRITICAL = "#fee5e5"
COLOR_DONE = "#dcf5dc"
COLOR_RISK = "#fff3c4"
COLOR_NORMAL = "#f0f0f0"

EDGE_COLOR_CRITICAL = "#c00000"
EDGE_COLOR_NORMAL = "#888888"


def _node_color(t: Task, em_risco_ids: set[str]) -> str:
    if t.esta_concluida:
        return COLOR_DONE
    if t.folga is not None and t.folga == 0:
        return COLOR_CRITICAL
    if t.id in em_risco_ids:
        return COLOR_RISK
    return COLOR_NORMAL


def render_png(tasks: list[Task], graph: nx.DiGraph, output_path: str | Path,
               figsize: tuple[float, float] = (13, 7), dpi: int = 140) -> Path:
    """
    Salva PNG do grafo no caminho indicado e retorna o Path.
    """
    by_id = task_by_id(tasks)
    em_risco = {t.id for t in tasks_at_risk(tasks)}

    # Layout: tenta usar layout hierárquico (graphviz) se disponível, senão spring
    try:
        from networkx.drawing.nx_agraph import graphviz_layout
        pos = graphviz_layout(graph, prog="dot")
    except (ImportError, Exception):
        # Layout custom: posiciona por "geração" topológica para parecer um DAG
        pos = _layered_layout(graph)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_facecolor("#ffffff")

    # Cores e edges separados em críticas e normais
    node_colors = [_node_color(by_id[n], em_risco) for n in graph.nodes()]
    critical_edges = [(u, v) for u, v in graph.edges()
                      if by_id[u].folga == 0 and by_id[v].folga == 0]
    normal_edges = [e for e in graph.edges() if e not in critical_edges]

    # Desenha
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=3500,
                            edgecolors="#444444", linewidths=1.2, ax=ax)
    nx.draw_networkx_edges(graph, pos, edgelist=normal_edges, edge_color=EDGE_COLOR_NORMAL,
                            width=1.2, arrows=True, arrowstyle="-|>", arrowsize=22,
                            node_size=3500, ax=ax)
    nx.draw_networkx_edges(graph, pos, edgelist=critical_edges, edge_color=EDGE_COLOR_CRITICAL,
                            width=2.6, arrows=True, arrowstyle="-|>", arrowsize=26,
                            node_size=3500, ax=ax)

    # Labels: ID na cabeça, nome do contratado embaixo
    labels = {n: f"{by_id[n].id}\n{by_id[n].contratado}" for n in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8,
                            font_family="sans-serif", ax=ax)

    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLOR_CRITICAL, edgecolor="#c00000", label="Caminho crítico"),
        Patch(facecolor=COLOR_DONE, edgecolor="#2a8a2a", label="Concluída"),
        Patch(facecolor=COLOR_RISK, edgecolor="#b78700", label="Em risco"),
        Patch(facecolor=COLOR_NORMAL, edgecolor="#888", label="Folga"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.95, fontsize=9)

    ax.axis("off")
    ax.set_title("Mapa de Interfaces — Ponto de Bloqueio",
                 fontsize=14, color="#222", pad=14)

    plt.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, format="png", facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    return out


def _layered_layout(graph: nx.DiGraph) -> dict:
    """
    Layout custom: organiza por "níveis" topológicos.
    Nós com mesma profundidade ficam na mesma coluna (LR).
    """
    levels: dict[str, int] = {}
    for node in nx.topological_sort(graph):
        preds = list(graph.predecessors(node))
        if not preds:
            levels[node] = 0
        else:
            levels[node] = max(levels[p] for p in preds) + 1

    # Agrupa por nível
    by_level: dict[int, list[str]] = {}
    for n, lvl in levels.items():
        by_level.setdefault(lvl, []).append(n)

    pos = {}
    x_step = 2.5
    y_step = 1.5
    for lvl, nodes in by_level.items():
        nodes.sort()  # ordem estável
        n_nodes = len(nodes)
        for i, node in enumerate(nodes):
            y = (i - (n_nodes - 1) / 2) * y_step
            pos[node] = (lvl * x_step, -y)
    return pos


__all__ = ["render_png"]
