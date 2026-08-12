from decimal import Decimal

from domain.models import ContratoNormalizado, FormatoContrato, ItemOrcamento, StatusCPU
from services.orcamento import resumir_orcamento


def test_resumo_ordena_grupos_itens_e_separa_valor_sem_cpu():
    contrato = ContratoNormalizado(
        formato=FormatoContrato.QQP,
        itens=(
            ItemOrcamento("1.1", "A", "vb", Decimal("1"), Decimal("70"), Decimal("70"), "Grupo 1"),
            ItemOrcamento("2.1", "B", "t", Decimal("1"), Decimal("30"), Decimal("30"), "Grupo 2", status_cpu=StatusCPU.VALIDADO_CPU),
        ),
    )

    resumo = resumir_orcamento(contrato)

    assert resumo["total_orcado"] == Decimal("100")
    assert resumo["grupos"][0]["nome"] == "Grupo 1"
    assert resumo["valor_sem_cpu"] == Decimal("70")
