from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum


class FormatoContrato(StrEnum):
    QQP = "qqp"
    DADOS = "dados"
    DESCONHECIDO = "desconhecido"


class StatusCPU(StrEnum):
    SEM_CPU = "sem_cpu"
    VALIDADO_CPU = "validado_cpu"
    DIVERGENTE_CPU = "divergente_cpu"


@dataclass(frozen=True)
class ComposicaoCusto:
    grupo: str
    subgrupo: str
    nome: str
    valor_planejado: Decimal


@dataclass(frozen=True)
class ItemOrcamento:
    codigo: str
    descricao: str
    unidade: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_planejado: Decimal
    area: str
    composicao: tuple[ComposicaoCusto, ...] = ()
    status_cpu: StatusCPU = StatusCPU.SEM_CPU


@dataclass(frozen=True)
class ContratoNormalizado:
    formato: FormatoContrato
    itens: tuple[ItemOrcamento, ...]
    avisos: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetadadosContrato:
    id: str
    arquivo: str
    sha256: str
    nome: str
    cliente: str
    obra: str
    inicio: date
    duracao_meses: int
    atualizado_em: datetime
