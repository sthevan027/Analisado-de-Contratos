from decimal import Decimal

from readers.dados import ler_dados
from tests.helpers import criar_dados_minimos


def test_ler_dados_normaliza_item_legado(tmp_path):
    contrato = ler_dados(criar_dados_minimos(tmp_path / "dados.xlsx"))

    assert contrato.itens[0].codigo == "2.1"
    assert contrato.itens[0].valor_planejado == Decimal("1250.00")
