"""
Gera relatório HTML standalone com tudo embutido (PNG em base64).

O relatório é um arquivo único — abre no navegador, pode ser impresso como PDF,
anexado em e-mail ou compartilhado. Não precisa de print screen.

Pré-requisito: forward_pass + backward_pass + analysis_summary já feitos.
"""

from __future__ import annotations

import base64
import html
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from .gen_email import gen_email
from .gen_whatsapp import gen_whatsapp
from .model import Task, task_by_id


def _fmt_date(d: Optional[date]) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def _situacao_obra(desvio: Optional[int]) -> tuple[str, str]:
    """Retorna (texto, classe CSS)."""
    if desvio is None:
        return ("—", "neutro")
    if desvio == 0:
        return ("No prazo", "ok")
    if desvio > 0:
        return (f"Atraso de {desvio} dia(s)", "atraso")
    return (f"Adiantamento de {-desvio} dia(s)", "ok")


def _png_to_data_uri(png_path: Path) -> str:
    """Embute PNG como data URI base64."""
    if not png_path.exists():
        return ""
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _h(text: object) -> str:
    """Escape HTML."""
    return html.escape(str(text), quote=True)


def gen_report(tasks: list[Task], summary: dict, png_path: Path | str | None,
               output_path: str | Path,
               project_name: str = "Obra",
               author_name: str = "Planejamento") -> Path:
    """
    Gera arquivo HTML completo. Retorna o Path.
    """
    by_id = task_by_id(tasks)
    desvio = summary["desvio_obra_dias"]
    situacao_txt, situacao_cls = _situacao_obra(desvio)

    # Imagem
    png_uri = ""
    if png_path:
        png_uri = _png_to_data_uri(Path(png_path))

    # Caminho crítico
    cp_rows = []
    for tid in summary["caminho_critico"]:
        t = by_id[tid]
        if t.esta_concluida:
            status_txt, status_cls = "Concluída", "ok"
        elif t.esta_em_andamento:
            status_txt, status_cls = "Em andamento", "atencao"
        else:
            status_txt, status_cls = "Pendente", "neutro"
        cp_rows.append(f"""
            <tr>
                <td><strong>{_h(t.id)}</strong></td>
                <td>{_h(t.contratado)}</td>
                <td>{_h(t.escopo)}</td>
                <td>{_h(_fmt_date(t.entrada_projetada))} → {_h(_fmt_date(t.saida_projetada))}</td>
                <td><span class="badge {status_cls}">{_h(status_txt)}</span></td>
            </tr>""")
    cp_html = "".join(cp_rows) or '<tr><td colspan="5" class="vazio">—</td></tr>'

    # Tarefas em risco
    risk_rows = []
    for tid in summary["tarefas_em_risco"]:
        t = by_id[tid]
        desvio_t = t.desvio_dias or 0
        if desvio_t > 0:
            desvio_str = f"<span class='badge atraso'>+{desvio_t}d</span>"
        elif desvio_t < 0:
            desvio_str = f"<span class='badge ok'>{desvio_t}d</span>"
        else:
            desvio_str = "<span class='badge neutro'>0d</span>"
        risk_rows.append(f"""
            <tr>
                <td><strong>{_h(t.id)}</strong></td>
                <td>{_h(t.contratado)}</td>
                <td>{_h(t.escopo)}</td>
                <td>{_h(t.folga)}d</td>
                <td>{desvio_str}</td>
            </tr>""")
    risk_html = "".join(risk_rows) or '<tr><td colspan="5" class="vazio">Nenhuma tarefa em risco.</td></tr>'

    # Bloqueadores
    blocker_rows = []
    for b in summary["maiores_bloqueadores"]:
        if b["descendentes_count"] == 0:
            continue
        critico = '<span class="badge cp">★ no caminho crítico</span>' if b["no_caminho_critico"] else ""
        blocker_rows.append(f"""
            <tr>
                <td><strong>{_h(b['id'])}</strong></td>
                <td>{_h(b['contratado'])}</td>
                <td>{_h(b['escopo'])}</td>
                <td>{_h(b['descendentes_count'])} tarefa(s)</td>
                <td>{critico}</td>
            </tr>""")
    blocker_html = "".join(blocker_rows) or '<tr><td colspan="5" class="vazio">—</td></tr>'

    # Textos para copiar
    whatsapp_texto = gen_whatsapp(tasks, summary, project_name=project_name)
    email_dict = gen_email(tasks, summary, project_name=project_name, author_name=author_name)
    email_texto = f"ASSUNTO: {email_dict['assunto']}\n\n{email_dict['corpo']}"

    img_html = ""
    if png_uri:
        img_html = f'<img src="{png_uri}" alt="Diagrama da obra" />'
    else:
        img_html = '<p class="vazio">Diagrama não disponível.</p>'

    gerado_em = datetime.now().strftime("%d/%m/%Y às %H:%M")

    return _write_html(
        output_path,
        project_name=project_name,
        author_name=author_name,
        gerado_em=gerado_em,
        situacao_txt=situacao_txt,
        situacao_cls=situacao_cls,
        total=summary["total_tarefas"],
        planejado=_fmt_date(summary["data_termino_planejado"]),
        projetado=_fmt_date(summary["data_termino_projetado"]),
        img_html=img_html,
        cp_html=cp_html,
        risk_html=risk_html,
        blocker_html=blocker_html,
        whatsapp_texto=whatsapp_texto,
        email_texto=email_texto,
    )


def _write_html(output_path, **ctx) -> Path:
    css = _CSS
    template = _HTML_TEMPLATE.format(css=css, **{k: v for k, v in ctx.items()})
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template, encoding="utf-8")
    return out


_CSS = """
* { box-sizing: border-box; }
body {
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    background: #f8fafc;
    color: #1f2937;
    margin: 0;
    padding: 0;
    line-height: 1.5;
}
.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 24px;
}
header {
    border-bottom: 3px solid #1f2937;
    padding-bottom: 18px;
    margin-bottom: 28px;
}
header h1 {
    margin: 0 0 6px 0;
    font-size: 28px;
    color: #0f172a;
    letter-spacing: -0.3px;
}
header .meta {
    color: #64748b;
    font-size: 14px;
}
section {
    background: #ffffff;
    border-radius: 8px;
    padding: 22px 24px;
    margin-bottom: 22px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    border: 1px solid #e2e8f0;
}
section h2 {
    margin: 0 0 14px 0;
    font-size: 18px;
    color: #0f172a;
}
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin-bottom: 8px;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 14px 16px;
}
.card .label {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.card .value {
    color: #0f172a;
    font-size: 22px;
    font-weight: 600;
}
.card .value.atraso { color: #b91c1c; }
.card .value.ok { color: #166534; }
.card .value.neutro { color: #475569; }
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
th {
    background: #1f2937;
    color: #fff;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
}
td {
    padding: 10px 12px;
    border-top: 1px solid #e2e8f0;
    vertical-align: top;
}
tr:nth-child(even) td { background: #f8fafc; }
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}
.badge.atraso { background: #fee2e2; color: #991b1b; }
.badge.ok { background: #dcfce7; color: #166534; }
.badge.atencao { background: #fef3c7; color: #92400e; }
.badge.neutro { background: #e2e8f0; color: #475569; }
.badge.cp { background: #fee5e5; color: #b91c1c; border: 1px solid #fca5a5; }
.diagrama img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
}
.copia {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 6px;
    padding: 14px 18px;
    font-family: "SF Mono", Consolas, "Courier New", monospace;
    font-size: 13px;
    white-space: pre-wrap;
    overflow-x: auto;
    line-height: 1.5;
}
.tab-titulo {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    margin: 16px 0 6px 0;
}
.vazio {
    color: #94a3b8;
    text-align: center;
    padding: 18px;
    font-style: italic;
}
footer {
    text-align: center;
    color: #64748b;
    font-size: 13px;
    padding: 18px 0;
    margin-top: 12px;
}
footer a { color: #1f2937; }
@media print {
    body { background: #fff; }
    section { box-shadow: none; border: 1px solid #cbd5e1; page-break-inside: avoid; }
    .container { padding: 12px; max-width: none; }
    header { border-bottom-color: #0f172a; }
}
"""


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Relatório — {project_name}</title>
<style>{css}</style>
</head>
<body>
<div class="container">

<header>
    <h1>Relatório de Status — {project_name}</h1>
    <div class="meta">Gerado em {gerado_em} · {author_name} · Ponto de Bloqueio</div>
</header>

<section>
    <h2>Resumo executivo</h2>
    <div class="cards">
        <div class="card"><div class="label">Tarefas</div><div class="value">{total}</div></div>
        <div class="card"><div class="label">Término planejado</div><div class="value">{planejado}</div></div>
        <div class="card"><div class="label">Término projetado</div><div class="value">{projetado}</div></div>
        <div class="card"><div class="label">Situação</div><div class="value {situacao_cls}">{situacao_txt}</div></div>
    </div>
</section>

<section class="diagrama">
    <h2>Mapa de interfaces</h2>
    {img_html}
</section>

<section>
    <h2>Caminho crítico</h2>
    <table>
        <thead><tr><th>ID</th><th>Contratado</th><th>Escopo</th><th>Janela projetada</th><th>Status</th></tr></thead>
        <tbody>{cp_html}</tbody>
    </table>
</section>

<section>
    <h2>Tarefas em risco</h2>
    <table>
        <thead><tr><th>ID</th><th>Contratado</th><th>Escopo</th><th>Folga</th><th>Desvio</th></tr></thead>
        <tbody>{risk_html}</tbody>
    </table>
</section>

<section>
    <h2>Maiores bloqueadores</h2>
    <table>
        <thead><tr><th>ID</th><th>Contratado</th><th>Escopo</th><th>Bloqueia</th><th>Caminho crítico</th></tr></thead>
        <tbody>{blocker_html}</tbody>
    </table>
</section>

<section>
    <h2>Mensagens prontas para enviar</h2>
    <div class="tab-titulo">WhatsApp</div>
    <pre class="copia">{whatsapp_texto}</pre>
    <div class="tab-titulo">E-mail</div>
    <pre class="copia">{email_texto}</pre>
</section>

<footer>
    Relatório gerado por <a href="https://github.com/Fabi-Thome/bravo-skills">Ponto de Bloqueio</a> · BravoCP
</footer>

</div>
</body>
</html>
"""


__all__ = ["gen_report"]
