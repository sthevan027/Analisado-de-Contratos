from datetime import date, datetime
from decimal import Decimal

from domain.models import ItemOrcamento, MetadadosContrato, StatusCPU


def test_item_orcamento_preserva_decimal_e_status_sem_cpu():
    item = ItemOrcamento(
        codigo="6.1.1",
        descricao="Serviço extraordinário",
        unidade="vb",
        quantidade=Decimal("1"),
        valor_unitario=Decimal("929429.9217"),
        valor_planejado=Decimal("929429.9217"),
        area="Serviços extraordinários",
    )

    assert item.valor_planejado == Decimal("929429.9217")
    assert item.status_cpu is StatusCPU.SEM_CPU


def test_metadados_contrato_expoe_inicio_e_duracao():
    metadados = MetadadosContrato(
        id="contrato-1", arquivo="anexo.xlsx", sha256="abc", nome="Anexo I",
        cliente="Cliente", obra="Obra", inicio=date(2026, 9, 1),
        duracao_meses=12, atualizado_em=datetime(2026, 8, 12, 12, 0),
    )

    assert metadados.duracao_meses == 12
