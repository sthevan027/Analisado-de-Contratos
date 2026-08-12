from pathlib import Path

from openpyxl import Workbook


def criar_planilha(path: Path, abas: list[str]) -> Path:
    workbook = Workbook()
    workbook.active.title = abas[0]
    for aba in abas[1:]:
        workbook.create_sheet(aba)
    workbook.save(path)
    return path
