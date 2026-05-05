"""
Gera texto curto para WhatsApp resumindo o status da obra.

Pré-requisito: forward_pass + backward_pass + analysis_summary já feitos.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from .model import Task, task_by_id


def _fmt_date(d: Optional[date]) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def gen_whatsapp(tasks: list[Task], summary: dict,
                 project_name: str = "Obra") -> str:
    """
    Texto curto para WhatsApp (5-8 linhas).

    Args:
        tasks: lista de tarefas (com cálculos)
        summary: output de analysis_summary()
        project_name: nome para identificar a obra

    Returns:
        String pronta para colar.
    """
    by_id = task_by_id(tasks)

    desvio = summary["desvio_obra_dias"]
    if desvio is None:
        emoji, msg = "⏱️", ""
    elif desvio == 0:
        emoji, msg = "✅", " (no prazo)"
    elif desvio > 0:
        emoji, msg = "⚠️", f" (atraso de {desvio}d)"
    else:
        emoji, msg = "🟢", f" ({-desvio}d adiantado)"

    cp_ids = summary["caminho_critico"]
    cp_str = " → ".join(cp_ids) if cp_ids else "—"

    bloqueadores = summary.get("maiores_bloqueadores", [])
    top_blocker = next(
        (b for b in bloqueadores if b["descendentes_count"] > 0),
        None,
    )

    em_risco_ids = summary.get("tarefas_em_risco", [])

    lines = [
        f"📋 *Status — {project_name}*",
        f"{emoji} Término projetado: *{_fmt_date(summary['data_termino_projetado'])}*{msg}",
    ]

    if cp_ids:
        lines.append(f"🔴 Caminho crítico: {cp_str}")

    if top_blocker:
        lines.append(
            f"🚧 Maior bloqueador: *{top_blocker['contratado']}* "
            f"({top_blocker['id']}) — bloqueia {top_blocker['descendentes_count']} tarefas"
        )

    if em_risco_ids:
        lines.append(f"⚠️ Em risco: {', '.join(em_risco_ids)}")

    return "\n".join(lines)


__all__ = ["gen_whatsapp"]
