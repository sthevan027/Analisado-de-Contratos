import pytest

from app import create_app
from tests.helpers import criar_qqp_minima


@pytest.fixture
def excel_dir(tmp_path):
    pasta = tmp_path / "excel"
    pasta.mkdir()
    return pasta


@pytest.fixture
def app(tmp_path, excel_dir):
    return create_app(
        {
            "TESTING": True,
            "EXCEL_DIR": excel_dir,
            "CATALOGO_PATH": tmp_path / "data" / "contratos.json",
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def arquivo_qqp(excel_dir):
    return criar_qqp_minima(excel_dir / "QQP.xlsx")


@pytest.fixture
def contrato_cadastrado(client, arquivo_qqp):
    client.post(
        "/contratos",
        data={
            "arquivo": arquivo_qqp.name,
            "nome": "Contrato Teste",
            "cliente": "Cliente",
            "obra": "Obra",
            "inicio": "2026-09-01",
            "duracao_meses": "12",
        },
        follow_redirects=True,
    )
    return arquivo_qqp
