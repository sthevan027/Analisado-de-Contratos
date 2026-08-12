from decimal import Decimal

from domain.models import StatusCPU
from readers.cpu import aplicar_cpu, ler_cpu
from readers.qqp import ler_qqp
from tests.helpers import criar_qqp_com_cpu


def test_aplicar_cpu_redistribui_bdi_proporcionalmente_e_marca_item_validado(tmp_path):
    arquivo = criar_qqp_com_cpu(tmp_path / "cpu.xlsx")

    contrato = aplicar_cpu(ler_qqp(arquivo), ler_cpu(arquivo))
    item = contrato.itens[0]

    assert item.status_cpu is StatusCPU.VALIDADO_CPU
    assert {parte.grupo for parte in item.composicao} == {
        "Mão de Obra", "Equipamentos", "Materiais"
    }
    assert sum((parte.valor_planejado for parte in item.composicao), Decimal()) == item.valor_planejado


def test_aplicar_cpu_preserva_item_sem_bloco_como_sem_cpu(tmp_path):
    arquivo = criar_qqp_com_cpu(tmp_path / "cpu_parcial.xlsx")

    contrato = aplicar_cpu(ler_qqp(arquivo), ler_cpu(arquivo))

    assert contrato.itens[1].status_cpu is StatusCPU.SEM_CPU
    assert contrato.itens[1].composicao == ()


def test_aplicar_cpu_marca_item_divergente_e_registra_aviso(tmp_path):
    arquivo = criar_qqp_com_cpu(tmp_path / "cpu_divergente.xlsx", total_geral=150)

    contrato = aplicar_cpu(ler_qqp(arquivo), ler_cpu(arquivo))
    item = contrato.itens[0]

    assert item.status_cpu is StatusCPU.DIVERGENTE_CPU
    assert any("1.1.1" in aviso for aviso in contrato.avisos)
