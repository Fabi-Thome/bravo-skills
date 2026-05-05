"""
Gera string Mermaid (flowchart) do grafo da obra.

Mermaid renderiza nativamente no GitHub, no Gemini (quando o Gem inclui em sua
resposta) e em qualquer Markdown viewer moderno. Não exige imagem binária.

Cores:
- caminho crítico: vermelho
- concluída (saída real preenchida): verde
- em risco (folga ≤ 3 ou desvio > 0): amarelo
- normal: cinza claro

Pré-requisito: forward_pass + backward_pass já rodados.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable

import networkx as nx

from .critical_path import tasks_at_risk
from .model import Task, task_by_id


def _safe_id(task_id: str) -> str:
    """
    Mermaid aceita hífens em IDs, mas para máxima compatibilidade
    convertemos para underscore no handle interno (mantemos hífen no label).
    """
    return task_id.replace("-", "_")


def _format_date(d: date | None) -> str:
    if d is None:
        return "—"
    return d.strftime("%d/%m")


def _classify(t: Task, em_risco_ids: set[str]) -> str:
    if t.esta_concluida:
        return "done"
    if t.folga is not None and t.folga == 0:
        return "critical"
    if t.id in em_risco_ids:
        return "risk"
    return "normal"


def to_mermaid(tasks: list[Task], graph: nx.DiGraph,
               direction: str = "LR",
               include_dates: bool = True) -> str:
    """
    Gera string Mermaid completa, pronta para colar em markdown.

    Args:
        tasks: lista de tarefas (com cálculos já feitos)
        graph: grafo NetworkX
        direction: "LR" (left-to-right) ou "TB" (top-to-bottom)
        include_dates: se True, inclui datas projetadas no rótulo

    Returns:
        String Mermaid começando com ```mermaid e terminando com ```
    """
    by_id = task_by_id(tasks)
    em_risco = {t.id for t in tasks_at_risk(tasks)}

    lines: list[str] = []
    lines.append("```mermaid")
    lines.append(f"flowchart {direction}")

    # Nós
    for t in tasks:
        handle = _safe_id(t.id)
        label_lines = [t.id, t.contratado, t.escopo]
        if include_dates and t.entrada_projetada and t.saida_projetada:
            label_lines.append(
                f"{_format_date(t.entrada_projetada)} → {_format_date(t.saida_projetada)}"
            )
        label = "<br/>".join(label_lines)
        klass = _classify(t, em_risco)
        lines.append(f'    {handle}["{label}"]:::{klass}')

    lines.append("")

    # Arestas
    for t in tasks:
        for pred in t.entra_apos:
            lines.append(f"    {_safe_id(pred)} --> {_safe_id(t.id)}")

    lines.append("")

    # Estilos
    lines.append("    classDef critical fill:#fee5e5,stroke:#c00000,stroke-width:2px,color:#000")
    lines.append("    classDef done fill:#dcf5dc,stroke:#2a8a2a,color:#000")
    lines.append("    classDef risk fill:#fff3c4,stroke:#b78700,color:#000")
    lines.append("    classDef normal fill:#f0f0f0,stroke:#888,color:#000")
    lines.append("```")

    return "\n".join(lines)


__all__ = ["to_mermaid"]
