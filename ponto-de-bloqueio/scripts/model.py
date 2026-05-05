"""
Estruturas de dados centrais e leitura do Excel.

Este módulo é a fundação dos demais scripts. Define:
- A dataclass Task (uma tarefa do grafo)
- O grafo de tarefas (NetworkX DiGraph)
- Leitura do Excel padrão da skill (uma planilha por obra)

A planilha esperada tem as colunas (em português, na aba "Obra"):
    ID | Contratado | Escopo | Entra após | Entrada planejada | Saída planejada
                                          | Entrada real | Saída real

"Entra após" pode conter múltiplos IDs separados por vírgula. Vazio = tarefa raiz.
Datas reais são opcionais.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import networkx as nx
import pandas as pd


COLUMN_MAP = {
    "ID": "id",
    "Contratado": "contratado",
    "Escopo": "escopo",
    "Entra após": "entra_apos",
    "Entrada planejada": "entrada_planejada",
    "Saída planejada": "saida_planejada",
    "Entrada real": "entrada_real",
    "Saída real": "saida_real",
}

REQUIRED_COLUMNS = ["ID", "Contratado", "Escopo", "Entra após",
                    "Entrada planejada", "Saída planejada"]


@dataclass
class Task:
    id: str
    contratado: str
    escopo: str
    entra_apos: list[str] = field(default_factory=list)
    entrada_planejada: Optional[date] = None
    saida_planejada: Optional[date] = None
    entrada_real: Optional[date] = None
    saida_real: Optional[date] = None

    # Calculados pelos algoritmos
    entrada_projetada: Optional[date] = None
    saida_projetada: Optional[date] = None
    entrada_limite: Optional[date] = None
    saida_limite: Optional[date] = None
    folga: Optional[int] = None  # em dias

    @property
    def duracao_planejada(self) -> int:
        """Duração planejada em dias corridos."""
        if self.entrada_planejada is None or self.saida_planejada is None:
            return 0
        return (self.saida_planejada - self.entrada_planejada).days

    @property
    def desvio_dias(self) -> Optional[int]:
        """
        Desvio projetado em relação ao planejado (em dias).
        Positivo = atraso. Negativo = adiantamento. Zero = no prazo.
        """
        if self.saida_projetada is None or self.saida_planejada is None:
            return None
        return (self.saida_projetada - self.saida_planejada).days

    @property
    def esta_no_caminho_critico(self) -> bool:
        return self.folga == 0

    @property
    def esta_concluida(self) -> bool:
        return self.saida_real is not None

    @property
    def esta_em_andamento(self) -> bool:
        return self.entrada_real is not None and self.saida_real is None


def _parse_date(value) -> Optional[date]:
    """Converte valor da planilha em date. Retorna None se vazio."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Data não reconhecida: {value!r}")
    raise ValueError(f"Tipo de data não suportado: {type(value).__name__}")


def _parse_predecessors(value) -> list[str]:
    """Converte string de predecessores (separados por vírgula ou ;) em lista."""
    if value is None or pd.isna(value):
        return []
    if isinstance(value, str):
        s = value.strip()
        if not s or s == "—" or s == "-":
            return []
        return [p.strip() for p in s.replace(";", ",").split(",") if p.strip()]
    return []


def load_tasks_from_excel(path: str | Path, sheet_name: str = "Obra") -> list[Task]:
    """
    Lê a planilha da obra e devolve a lista de tarefas.

    Args:
        path: caminho para o arquivo .xlsx
        sheet_name: nome da aba (default "Obra")

    Returns:
        Lista de Task

    Raises:
        ValueError se faltar coluna obrigatória.
    """
    df = pd.read_excel(path, sheet_name=sheet_name)
    return load_tasks_from_dataframe(df)


def load_tasks_from_dataframe(df: pd.DataFrame) -> list[Task]:
    """Mesma coisa que load_tasks_from_excel mas a partir de um DataFrame."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    tasks: list[Task] = []
    for idx, row in df.iterrows():
        # Pula linhas totalmente vazias
        if pd.isna(row["ID"]) or str(row["ID"]).strip() == "":
            continue

        task_id = str(row["ID"]).strip()
        try:
            tasks.append(
                Task(
                    id=task_id,
                    contratado=str(row["Contratado"]).strip(),
                    escopo=str(row["Escopo"]).strip(),
                    entra_apos=_parse_predecessors(row["Entra após"]),
                    entrada_planejada=_parse_date(row["Entrada planejada"]),
                    saida_planejada=_parse_date(row["Saída planejada"]),
                    entrada_real=_parse_date(row.get("Entrada real")),
                    saida_real=_parse_date(row.get("Saída real")),
                )
            )
        except Exception as exc:
            raise ValueError(f"Erro na linha {idx + 2} (ID={task_id}): {exc}") from exc

    return tasks


def build_graph(tasks: list[Task]) -> nx.DiGraph:
    """
    Constrói um DiGraph do NetworkX com as tarefas.
    Não valida ciclos — para isso ver validate_dag.

    Cada nó tem o atributo "task" apontando para a Task original.
    """
    G = nx.DiGraph()
    for t in tasks:
        G.add_node(t.id, task=t)
    for t in tasks:
        for pred in t.entra_apos:
            G.add_edge(pred, t.id)
    return G


def task_by_id(tasks: list[Task]) -> dict[str, Task]:
    """Indexa lista de tarefas por ID."""
    return {t.id: t for t in tasks}


__all__ = [
    "Task",
    "load_tasks_from_excel",
    "load_tasks_from_dataframe",
    "build_graph",
    "task_by_id",
    "COLUMN_MAP",
    "REQUIRED_COLUMNS",
]
