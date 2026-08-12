from datetime import date
from decimal import Decimal

import pytest

from services.curva_s import gerar_curva_s


def test_curva_s_termina_no_total_e_tem_soma_mensal_exata():
    curva = gerar_curva_s(Decimal("100.00"), date(2026, 9, 1), 3)

    assert len(curva) == 3
    assert curva[-1]["acumulado"] == Decimal("100.00")
    assert sum((ponto["mensal"] for ponto in curva), Decimal()) == Decimal("100.00")
    assert [ponto["competencia"] for ponto in curva] == ["2026-09", "2026-10", "2026-11"]


def test_curva_s_rejeita_duracao_zero():
    with pytest.raises(ValueError):
        gerar_curva_s(Decimal("100.00"), date(2026, 9, 1), 0)
