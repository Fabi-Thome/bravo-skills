"""
Gera o arquivo `exemplos/obra-exemplo-completa.xlsx` programaticamente.

Cenário modelado: Armazém Graneleiro em Sorriso/MT.
14 tarefas em 6 contratados, com diferentes profundidades, algumas tarefas
concluídas, outras em andamento, atrasos propagando, convergência crítica.

Uso (de dentro de ponto-de-bloqueio/):
    python -m scripts.generate_example
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


HEADER_FILL = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)

DONE_FILL = PatternFill(start_color="DCF5DC", end_color="DCF5DC", fill_type="solid")
INPROG_FILL = PatternFill(start_color="FFF3C4", end_color="FFF3C4", fill_type="solid")

THIN = Side(border_style="thin", color="CBD5E1")
BORDER = Border(top=THIN, left=THIN, right=THIN, bottom=THIN)


COLUMNS = [
    ("ID", 12),
    ("Contratado", 18),
    ("Escopo", 38),
    ("Entra após", 16),
    ("Entrada planejada", 18),
    ("Saída planejada", 18),
    ("Entrada real", 14),
    ("Saída real", 14),
]


# Cenário: obra de armazém graneleiro
# Atrasos reais gerados em cascata: SOU-02 atrasou 3 dias → TRI-01 entrou atrasado.
TASKS = [
    # Civil (Souza Rabelo) — todas concluídas ou em andamento
    ("SOU-01", "Souza Rabelo", "Terraplanagem e drenagem",            "",
     date(2026, 3, 1),   date(2026, 3, 31),  date(2026, 3, 1),   date(2026, 3, 30)),
    ("SOU-02", "Souza Rabelo", "Fundações dos silos",                 "SOU-01",
     date(2026, 4, 1),   date(2026, 4, 30),  date(2026, 4, 1),   date(2026, 5, 3)),   # +3d desvio
    ("SOU-03", "Souza Rabelo", "Fundações do galpão de expedição",    "SOU-01",
     date(2026, 4, 5),   date(2026, 4, 25),  date(2026, 4, 6),   date(2026, 4, 28)),  # +3d
    ("SOU-04", "Souza Rabelo", "Pavimentação interna",                "SOU-01",
     date(2026, 4, 15),  date(2026, 4, 30),  date(2026, 4, 15),  None),               # in progress

    # Estrutura metálica (Triade)
    ("TRI-01", "Triade",       "Estrutura metálica dos silos",        "SOU-02",
     date(2026, 5, 1),   date(2026, 6, 15),  date(2026, 5, 4),   None),               # in progress, atrasou
    ("TRI-02", "Triade",       "Estrutura metálica do galpão",        "SOU-03",
     date(2026, 5, 1),   date(2026, 5, 30),  date(2026, 5, 2),   None),               # in progress

    # Subestação (Eletrofase)
    ("ELE-01", "Eletrofase",   "Subestação de média tensão",          "SOU-04",
     date(2026, 5, 5),   date(2026, 5, 30),  None,               None),

    # Cobertura e equipamentos (Saur)
    ("SAU-01", "Saur",         "Cobertura dos silos",                 "TRI-01",
     date(2026, 6, 16),  date(2026, 7, 15),  None,               None),
    ("SAU-02", "Saur",         "Cobertura do galpão",                 "TRI-02",
     date(2026, 5, 31),  date(2026, 6, 25),  None,               None),
    ("SAU-03", "Saur",         "Instalação do tombador",              "SOU-02, ELE-01",
     date(2026, 5, 31),  date(2026, 6, 30),  None,               None),
    ("SAU-04", "Saur",         "Elevadores e transportadores",        "TRI-01, SAU-01",
     date(2026, 7, 16),  date(2026, 8, 15),  None,               None),

    # Elétrica BT e automação (Alpha)
    ("ALP-01", "Alpha",        "Elétrica de baixa tensão",            "SAU-02, ELE-01",
     date(2026, 6, 26),  date(2026, 7, 31),  None,               None),
    ("ALP-02", "Alpha",        "Automação e instrumentação",          "SAU-04, ALP-01",
     date(2026, 8, 1),   date(2026, 8, 30),  None,               None),

    # Comissionamento (BravoCP)
    ("BCP-01", "BravoCP",      "Comissionamento e startup",           "ALP-02, SAU-03",
     date(2026, 8, 31),  date(2026, 9, 25),  None,               None),
]


def generate(output_path: str | Path) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Obra"

    # Cabeçalhos
    for col_idx, (name, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=name)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = BORDER
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Dados
    for row_idx, task in enumerate(TASKS, start=2):
        is_done = task[7] is not None
        is_inprog = task[6] is not None and task[7] is None

        for col_idx, value in enumerate(task, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = BORDER
            if isinstance(value, date):
                cell.number_format = "DD/MM/YYYY"
            if is_done:
                cell.fill = DONE_FILL
            elif is_inprog:
                cell.fill = INPROG_FILL

    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 24

    # Aba meta com descrição da obra
    meta = wb.create_sheet("Sobre esta obra")
    meta.column_dimensions["A"].width = 110
    body = Font(size=11, color="333333")
    title = Font(bold=True, size=14, color="1F2937")
    section = Font(bold=True, size=11, color="1F2937")
    rows = [
        ("Sobre esta obra-exemplo", title),
        ("", body),
        ("Cenário: Armazém Graneleiro em Sorriso/MT", section),
        ("Construção de um complexo de armazenamento e expedição de grãos com:", body),
        ("  • bateria de silos com tombador integrado;", body),
        ("  • galpão de expedição;", body),
        ("  • subestação de média tensão e elétrica de baixa tensão;", body),
        ("  • automação e comissionamento.", body),
        ("", body),
        ("Como ler este exemplo", section),
        ("• Linhas em verde: tarefas concluídas (saída real preenchida)", body),
        ("• Linhas em amarelo: tarefas em andamento (entrada real preenchida, saída não)", body),
        ("• Linhas brancas: tarefas ainda não iniciadas", body),
        ("", body),
        ("• SOU-02 (fundações dos silos) atrasou 3 dias, propagando para TRI-01 e tudo downstream.", body),
        ("• BCP-01 (comissionamento) tem convergência crítica: depende de ALP-02 e SAU-03.", body),
        ("", body),
        ("Use a aba 'Obra' para experimentar mudanças e fazer upload no Ponto de Bloqueio.", body),
    ]
    for i, (text, font) in enumerate(rows, start=1):
        c = meta.cell(row=i, column=1, value=text)
        c.font = font
        c.alignment = Alignment(wrap_text=True, vertical="top")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def _cli():
    out = Path(__file__).parent.parent / "exemplos" / "obra-exemplo-completa.xlsx"
    path = generate(out)
    print(f"✅ Exemplo gerado em: {path}")
    print(f"   Tarefas: {len(TASKS)}")
    print(f"   Contratados: {len(set(t[1] for t in TASKS))}")


if __name__ == "__main__":
    _cli()
