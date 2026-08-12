from pathlib import Path

from openpyxl import Workbook


def criar_planilha(path: Path, abas: list[str]) -> Path:
    workbook = Workbook()
    workbook.active.title = abas[0]
    for aba in abas[1:]:
        workbook.create_sheet(aba)
    workbook.save(path)
    return path


def criar_qqp_minima(path: Path) -> Path:
    workbook = Workbook()
    aba = workbook.active
    aba.title = "QQP"
    aba.append(["ITEM", "DESCRIÇÃO", "UNID.", "QUANT.", "PREÇOS (R$)"])
    aba.append([None, None, None, None, "UNITÁRIO", "TOTAL"])
    aba.append(["1", "Obras civis", None, None, None, None])
    aba.append(["1.1", "Fundações", None, None, None, None])
    aba.append(["1.1.1", "Escavação", "m3", 5, 5.00, 25.00])
    aba.append(["1.1.2", "Concreto", "m3", 2, 5.00, 10.00])
    workbook.save(path)
    return path


def criar_dados_minimos(path: Path) -> Path:
    workbook = Workbook()
    aba = workbook.active
    aba.title = "Dados"
    aba.append(["ITEM", "DESCRIÇÃO", "UNIDADE", "QUANTIDADE", "VALOR UNITÁRIO", "VALOR TOTAL", "SEÇÃO"])
    aba.append(["2.1", "Serviço legado", "un", 5, 250.00, 1250.00, "Elétrica"])
    workbook.save(path)
    return path
