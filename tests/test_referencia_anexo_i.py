from pathlib import Path

from domain.models import StatusCPU
from readers.cpu import aplicar_cpu, ler_cpu
from readers.qqp import ler_qqp

REFERENCIA = Path("excel/Anexo_I_-_PQ-8001PZ-G-11007_Rev.ALT_REV08 (1).xlsx")


def test_anexo_i_qqp_cpu_normaliza_itens_e_cobertura_parcial():
    contrato = aplicar_cpu(ler_qqp(REFERENCIA), ler_cpu(REFERENCIA))

    assert len(contrato.itens) == 51
    assert sum(item.status_cpu is StatusCPU.SEM_CPU for item in contrato.itens) == 1
    assert next(item for item in contrato.itens if item.codigo == "6.1.1").status_cpu is StatusCPU.SEM_CPU
