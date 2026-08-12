import json
import os
import tempfile
from pathlib import Path

from domain.models import MetadadosContrato

_SCHEMA_VERSION = 1
_CHAVES_OBRIGATORIAS = {"schema_version", "contrato_ativo_id", "contratos"}


def _catalogo_vazio() -> dict:
    return {"schema_version": _SCHEMA_VERSION, "contrato_ativo_id": None, "contratos": []}


def carregar_catalogo(path: Path) -> dict:
    if not path.exists():
        return _catalogo_vazio()

    try:
        catalogo = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ValueError(f"Catálogo de contratos malformado em {path}") from erro

    if not isinstance(catalogo, dict) or not _CHAVES_OBRIGATORIAS.issubset(catalogo.keys()):
        raise ValueError(f"Catálogo de contratos com esquema inválido em {path}")

    return catalogo


def salvar_catalogo(path: Path, catalogo: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(catalogo, ensure_ascii=False, indent=2)

    descritor, nome_temporario = tempfile.mkstemp(dir=path.parent, prefix=".contratos-", suffix=".tmp")
    try:
        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo_temporario:
            arquivo_temporario.write(conteudo)
            arquivo_temporario.flush()
            os.fsync(arquivo_temporario.fileno())
        os.replace(nome_temporario, path)
    except BaseException:
        if os.path.exists(nome_temporario):
            os.remove(nome_temporario)
        raise


def registrar_contrato(catalogo: dict, metadados: MetadadosContrato) -> dict:
    registro = {
        "id": metadados.id,
        "arquivo": metadados.arquivo,
        "sha256": metadados.sha256,
        "nome": metadados.nome,
        "cliente": metadados.cliente,
        "obra": metadados.obra,
        "inicio": metadados.inicio.isoformat(),
        "duracao_meses": metadados.duracao_meses,
        "atualizado_em": metadados.atualizado_em.isoformat(),
    }

    contratos = [contrato for contrato in catalogo["contratos"] if contrato["id"] != metadados.id]
    contratos.append(registro)

    return {**catalogo, "contratos": contratos}


def selecionar_contrato(catalogo: dict, contrato_id: str) -> dict:
    if not any(contrato["id"] == contrato_id for contrato in catalogo["contratos"]):
        raise ValueError(f"Contrato desconhecido: {contrato_id}")

    return {**catalogo, "contrato_ativo_id": contrato_id}
