import calendar
from datetime import date
from decimal import Decimal

_CENTAVOS = Decimal("0.01")


def _somar_meses(inicio: date, deslocamento: int) -> date:
    total_meses = inicio.month - 1 + deslocamento
    ano = inicio.year + total_meses // 12
    mes = total_meses % 12 + 1
    ultimo_dia_do_mes = calendar.monthrange(ano, mes)[1]
    dia = min(inicio.day, ultimo_dia_do_mes)
    return date(ano, mes, dia)


def gerar_curva_s(total: Decimal, inicio: date, duracao_meses: int) -> list[dict]:
    if duracao_meses <= 0:
        raise ValueError("duracao_meses deve ser maior que zero")

    pontos: list[dict] = []
    acumulado_anterior = Decimal("0")

    for indice in range(1, duracao_meses + 1):
        if indice == duracao_meses:
            acumulado = total.quantize(_CENTAVOS)
        else:
            x = Decimal(indice) / Decimal(duracao_meses)
            fracao = 3 * x * x - 2 * x * x * x
            acumulado = (total * fracao).quantize(_CENTAVOS)

        mensal = acumulado - acumulado_anterior
        competencia = _somar_meses(inicio, indice - 1)

        pontos.append(
            {
                "competencia": competencia.strftime("%Y-%m"),
                "acumulado": acumulado,
                "mensal": mensal,
            }
        )
        acumulado_anterior = acumulado

    return pontos
