from decimal import Decimal

from readers.qqp import ler_qqp
from tests.helpers import criar_qqp_minima


def test_ler_qqp_extrai_apenas_linhas_folha_e_usa_quantidade_vezes_unitario(tmp_path):
    arquivo = criar_qqp_minima(tmp_path / "qqp.xlsx")

    contrato = ler_qqp(arquivo)

    assert [item.codigo for item in contrato.itens] == ["1.1.1", "1.1.2"]
    assert contrato.itens[0].valor_planejado == Decimal("25.00")
    assert contrato.itens[0].area == "Obras civis"
    assert contrato.itens[1].valor_planejado == Decimal("10.00")
