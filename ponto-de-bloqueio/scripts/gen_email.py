"""
Gera assunto + corpo de e-mail formal resumindo o status da obra.

Pré-requisito: forward_pass + backward_pass + analysis_summary já feitos.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from .model import Task, task_by_id


def _fmt_date(d: Optional[date]) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def gen_email(tasks: list[Task], summary: dict,
              project_name: str = "Obra",
              author_name: str = "Planejamento") -> dict:
    """
    Retorna dict com {assunto, corpo}.

    Args:
        tasks: lista de tarefas (com cálculos)
        summary: output de analysis_summary()
        project_name: nome da obra
        author_name: nome ou área que assina o e-mail

    Returns:
        {"assunto": str, "corpo": str}
    """
    by_id = task_by_id(tasks)
    today = _fmt_date(date.today())

    slip = summary["slip_obra_dias"]
    if slip is None:
        slip_label = "Sem dados de planejamento"
    elif slip == 0:
        slip_label = "no prazo"
    elif slip > 0:
        slip_label = f"atraso de {slip} dia(s)"
    else:
        slip_label = f"adiantada em {-slip} dia(s)"

    assunto = f"Status — {project_name} — {today}"

    cp_ids = summary["caminho_critico"]
    cp_lines = []
    for tid in cp_ids:
        t = by_id[tid]
        marker = "✓" if t.esta_concluida else ("→" if t.esta_em_andamento else "·")
        cp_lines.append(
            f"  {marker} {t.id} — {t.contratado} ({t.escopo}): "
            f"{_fmt_date(t.entrada_projetada)} → {_fmt_date(t.saida_projetada)}"
        )

    em_risco_ids = summary.get("tarefas_em_risco", [])
    risco_lines = []
    for tid in em_risco_ids:
        t = by_id[tid]
        slip_t = t.slip_dias
        slip_str = f", atraso projetado de {slip_t} dia(s)" if slip_t and slip_t > 0 else ""
        risco_lines.append(
            f"  • {t.id} — {t.contratado} ({t.escopo}): "
            f"folga {t.folga} dia(s){slip_str}"
        )

    bloqueadores = summary.get("maiores_bloqueadores", [])
    top_blockers = [b for b in bloqueadores if b["descendentes_count"] > 0][:3]
    blockers_lines = []
    for b in top_blockers:
        critico_marker = " (no caminho crítico)" if b["no_caminho_critico"] else ""
        blockers_lines.append(
            f"  • {b['contratado']} — {b['id']} ({b['escopo']}): "
            f"bloqueia {b['descendentes_count']} tarefa(s){critico_marker}"
        )

    corpo_partes = [
        "Prezados,",
        "",
        f"Segue atualização do status da obra **{project_name}**, com base no estado mais recente "
        "das interfaces entre contratados.",
        "",
        "**RESUMO**",
        f"  Total de tarefas: {summary['total_tarefas']}",
        f"  Término planejado: {_fmt_date(summary['data_termino_planejado'])}",
        f"  Término projetado: {_fmt_date(summary['data_termino_projetado'])}",
        f"  Situação: {slip_label}",
        "",
    ]

    if cp_lines:
        corpo_partes.extend([
            "**CAMINHO CRÍTICO**",
            *cp_lines,
            "",
        ])

    if risco_lines:
        corpo_partes.extend([
            "**TAREFAS EM RISCO**",
            *risco_lines,
            "",
        ])

    if blockers_lines:
        corpo_partes.extend([
            "**MAIORES BLOQUEADORES**",
            *blockers_lines,
            "",
        ])

    corpo_partes.extend([
        "Permaneço à disposição para esclarecimentos.",
        "",
        "Atenciosamente,",
        author_name,
    ])

    corpo = "\n".join(corpo_partes)
    return {"assunto": assunto, "corpo": corpo}


__all__ = ["gen_email"]
