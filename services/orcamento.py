from decimal import Decimal

from domain.models import ContratoNormalizado, StatusCPU

_CENTAVOS = Decimal("0.01")
_MAXIMO_ITENS_MAIOR_PESO = 10


def resumir_orcamento(contrato: ContratoNormalizado) -> dict:
    itens = contrato.itens
    total_orcado = sum((item.valor_planejado for item in itens), Decimal("0"))

    valores_por_grupo: dict[str, Decimal] = {}
    itens_por_grupo: dict[str, int] = {}
    for item in itens:
        valores_por_grupo[item.area] = valores_por_grupo.get(item.area, Decimal("0")) + item.valor_planejado
        itens_por_grupo[item.area] = itens_por_grupo.get(item.area, 0) + 1

    grupos = sorted(
        (
            {"nome": nome, "valor": valor, "quantidade_itens": itens_por_grupo[nome]}
            for nome, valor in valores_por_grupo.items()
        ),
        key=lambda grupo: grupo["valor"],
        reverse=True,
    )

    itens_ordenados = sorted(itens, key=lambda item: item.valor_planejado, reverse=True)
    itens_maior_peso = [
        {
            "codigo": item.codigo,
            "descricao": item.descricao,
            "area": item.area,
            "valor": item.valor_planejado,
            "status_cpu": item.status_cpu,
        }
        for item in itens_ordenados[:_MAXIMO_ITENS_MAIOR_PESO]
    ]

    valores_por_composicao: dict[str, Decimal] = {}
    for item in itens:
        for parte in item.composicao:
            valores_por_composicao[parte.grupo] = (
                valores_por_composicao.get(parte.grupo, Decimal("0")) + parte.valor_planejado
            )
    composicao_cpu = sorted(
        ({"grupo": grupo, "valor": valor} for grupo, valor in valores_por_composicao.items()),
        key=lambda parte: parte["valor"],
        reverse=True,
    )

    valor_sem_cpu = sum(
        (item.valor_planejado for item in itens if item.status_cpu is StatusCPU.SEM_CPU), Decimal("0")
    )
    valor_com_cpu = total_orcado - valor_sem_cpu
    cobertura_cpu_pct = (
        (valor_com_cpu / total_orcado * 100).quantize(_CENTAVOS) if total_orcado > 0 else Decimal("0.00")
    )

    return {
        "total_orcado": total_orcado,
        "quantidade_itens": len(itens),
        "quantidade_grupos": len(grupos),
        "grupos": grupos,
        "itens_maior_peso": itens_maior_peso,
        "composicao_cpu": composicao_cpu,
        "valor_com_cpu": valor_com_cpu,
        "valor_sem_cpu": valor_sem_cpu,
        "cobertura_cpu_pct": cobertura_cpu_pct,
        "avisos": list(contrato.avisos),
    }
