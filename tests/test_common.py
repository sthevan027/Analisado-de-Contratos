from domain.models import FormatoContrato
from readers.common import calcular_sha256, detectar_formato, listar_arquivos_excel
from tests.helpers import criar_planilha


def test_listar_arquivos_excel_ignora_temporario_e_extensao_invalida(tmp_path):
    criar_planilha(tmp_path / "QQP.xlsx", ["QQP"])
    criar_planilha(tmp_path / "~$QQP.xlsx", ["QQP"])
    (tmp_path / "contrato.xls").write_text("não é xlsx", encoding="utf-8")

    assert [path.name for path in listar_arquivos_excel(tmp_path)] == ["QQP.xlsx"]


def test_detectar_qqp_ld_dados_e_desconhecido(tmp_path):
    qqp = criar_planilha(tmp_path / "q.xlsx", ["F. Rosto", "QQP", "CPU"])
    ld = criar_planilha(tmp_path / "ld.xlsx", ["LD3", "CPU"])
    dados = criar_planilha(tmp_path / "d.xlsx", ["Dados"])
    outro = criar_planilha(tmp_path / "o.xlsx", ["CMS", "MC Serv. Extraordinários"])

    assert detectar_formato(qqp) is FormatoContrato.QQP
    assert detectar_formato(ld) is FormatoContrato.QQP
    assert detectar_formato(dados) is FormatoContrato.DADOS
    assert detectar_formato(outro) is FormatoContrato.DESCONHECIDO


def test_calcular_sha256_muda_quando_conteudo_muda(tmp_path):
    arquivo = tmp_path / "fonte.bin"
    arquivo.write_bytes(b"A")
    primeiro = calcular_sha256(arquivo)
    arquivo.write_bytes(b"B")
    assert calcular_sha256(arquivo) != primeiro
