"""
Pipeline orquestrador — recebe um Excel, devolve análise completa.

Para o usuário humano: ferramenta CLI auditável (`python -m scripts.analyze obra.xlsx`).
Para o Gem: referência de fluxo. O Gem gera código Python equivalente em runtime.

Uso:
    python -m scripts.analyze caminho/para/obra.xlsx [--projeto "Nome da Obra"]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .critical_path import analysis_summary, backward_pass
from .forward_pass import forward_pass
from .gen_email import gen_email
from .gen_report import gen_report
from .gen_whatsapp import gen_whatsapp
from .model import load_tasks_from_excel, task_by_id
from .render_mermaid import to_mermaid
from .render_png import render_png
from .validate_dag import validate


def analyze(excel_path: str | Path, output_dir: str | Path,
            project_name: str = "Obra", author_name: str = "Planejamento"):
    """
    Executa o pipeline completo. Salva artefatos no output_dir.

    Returns:
        dict com {summary, mermaid, png_path, whatsapp, email}
    """
    excel_path = Path(excel_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Carregar e validar
    tasks = load_tasks_from_excel(excel_path)
    G = validate(tasks)

    # 2. Cálculos
    forward_pass(tasks, G)
    backward_pass(tasks, G)
    summary = analysis_summary(tasks, G)

    # 3. Visualizações
    mermaid_str = to_mermaid(tasks, G)
    (output_dir / "grafo.md").write_text(mermaid_str, encoding="utf-8")

    png_path = render_png(tasks, G, output_dir / "grafo.png")

    # 4. Comunicação
    whatsapp = gen_whatsapp(tasks, summary, project_name=project_name)
    (output_dir / "whatsapp.txt").write_text(whatsapp, encoding="utf-8")

    email = gen_email(tasks, summary, project_name=project_name, author_name=author_name)
    email_text = f"ASSUNTO: {email['assunto']}\n\n{email['corpo']}"
    (output_dir / "email.txt").write_text(email_text, encoding="utf-8")

    # 5. Relatório HTML standalone
    report_path = gen_report(
        tasks, summary, png_path, output_dir / "relatorio.html",
        project_name=project_name, author_name=author_name,
    )

    return {
        "tasks": tasks,
        "graph": G,
        "summary": summary,
        "mermaid": mermaid_str,
        "png_path": png_path,
        "whatsapp": whatsapp,
        "email": email,
        "report_path": report_path,
    }


def _print_summary(result: dict, project_name: str) -> None:
    summary = result["summary"]
    by_id = task_by_id(result["tasks"])

    print("=" * 70)
    print(f"  ANÁLISE — {project_name}")
    print("=" * 70)
    print(f"  Tarefas:              {summary['total_tarefas']}")
    print(f"  Término planejado:    {summary['data_termino_planejado']}")
    print(f"  Término projetado:    {summary['data_termino_projetado']}")
    desvio = summary["desvio_obra_dias"]
    if desvio is None:
        situacao = "—"
    elif desvio == 0:
        situacao = "no prazo"
    elif desvio > 0:
        situacao = f"atraso de {desvio} dia(s)"
    else:
        situacao = f"adiantamento de {-desvio} dia(s)"
    print(f"  Situação:             {situacao}")
    print()
    print(f"  Caminho crítico:")
    for tid in summary["caminho_critico"]:
        t = by_id[tid]
        marker = "✓" if t.esta_concluida else ("→" if t.esta_em_andamento else "·")
        print(f"    {marker} {tid:8s} {t.contratado:14s} {t.escopo}")
    print()

    if summary["tarefas_em_risco"]:
        print(f"  Tarefas em risco:")
        for tid in summary["tarefas_em_risco"]:
            t = by_id[tid]
            print(f"    • {tid:8s} folga={t.folga}d desvio={t.desvio_dias}d  {t.escopo}")
        print()

    print("  Maiores bloqueadores:")
    for b in summary["maiores_bloqueadores"]:
        if b["descendentes_count"] == 0:
            continue
        cp = " ★" if b["no_caminho_critico"] else ""
        print(f"    • {b['id']:8s} {b['contratado']:14s} bloqueia {b['descendentes_count']} tarefa(s){cp}")


def _cli():
    parser = argparse.ArgumentParser(description="Ponto de Bloqueio — pipeline de análise")
    parser.add_argument("excel", type=Path, help="Caminho do Excel da obra")
    parser.add_argument("--projeto", default="Obra", help="Nome da obra para os outputs")
    parser.add_argument("--autor", default="Planejamento", help="Assinatura do e-mail")
    parser.add_argument("--out", type=Path, default=Path("output"),
                        help="Pasta de saída")
    args = parser.parse_args()

    result = analyze(args.excel, args.out, project_name=args.projeto, author_name=args.autor)
    _print_summary(result, args.projeto)
    print()
    print("=" * 70)
    print(f"  Artefatos salvos em: {args.out.resolve()}")
    print("=" * 70)
    print(f"    grafo.md         Mermaid (cole no GitHub/VSCode para renderizar)")
    print(f"    grafo.png        Imagem para anexar em e-mail/WhatsApp")
    print(f"    whatsapp.txt     Texto pronto para colar no WhatsApp")
    print(f"    email.txt        Assunto + corpo de e-mail")
    print(f"    relatorio.html   Relatório completo (abrir no navegador)")


if __name__ == "__main__":
    _cli()
