from datetime import date, datetime

import pytest

from domain.models import MetadadosContrato
from storage.contratos import carregar_catalogo, registrar_contrato, salvar_catalogo, selecionar_contrato


def test_catalogo_salva_e_reabre_contrato_ativo(tmp_path):
    caminho = tmp_path / "data" / "contratos.json"
    registro = MetadadosContrato(
        id="id-1", arquivo="anexo.xlsx", sha256="hash-1", nome="Anexo I",
        cliente="Cliente", obra="Obra", inicio=date(2026, 9, 1),
        duracao_meses=12, atualizado_em=datetime(2026, 8, 12, 12, 0),
    )

    catalogo = selecionar_contrato(registrar_contrato(carregar_catalogo(caminho), registro), "id-1")
    salvar_catalogo(caminho, catalogo)

    reaberto = carregar_catalogo(caminho)
    assert reaberto["contrato_ativo_id"] == "id-1"
    assert reaberto["contratos"][0]["nome"] == "Anexo I"


def test_registrar_contrato_preserva_metadados_quando_hash_muda(tmp_path):
    catalogo = carregar_catalogo(tmp_path / "contratos.json")
    antigo = MetadadosContrato("id-1", "anexo.xlsx", "hash-1", "Anexo I", "Cliente", "Obra", date(2026, 9, 1), 12, datetime(2026, 8, 12))
    novo = MetadadosContrato("id-1", "anexo.xlsx", "hash-2", "Anexo I", "Cliente", "Obra", date(2026, 9, 1), 12, datetime(2026, 8, 13))

    resultado = registrar_contrato(registrar_contrato(catalogo, antigo), novo)

    assert resultado["contratos"][0]["sha256"] == "hash-2"
    assert resultado["contratos"][0]["cliente"] == "Cliente"


def test_carregar_catalogo_rejeita_json_malformado(tmp_path):
    caminho = tmp_path / "contratos.json"
    caminho.write_text("{invalido", encoding="utf-8")

    with pytest.raises(ValueError):
        carregar_catalogo(caminho)


def test_selecionar_contrato_rejeita_id_desconhecido(tmp_path):
    catalogo = carregar_catalogo(tmp_path / "contratos.json")

    with pytest.raises(ValueError):
        selecionar_contrato(catalogo, "id-inexistente")
