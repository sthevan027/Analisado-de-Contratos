import hashlib
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from domain.models import FormatoContrato

_TAMANHO_BLOCO = 1024 * 1024
_PADRAO_LD = re.compile(r"^LD\d+$")


def _normalizar(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


def listar_arquivos_excel(pasta: Path) -> list[Path]:
    arquivos = [
        caminho
        for caminho in pasta.iterdir()
        if caminho.is_file()
        and caminho.suffix.lower() == ".xlsx"
        and not caminho.name.startswith("~$")
    ]
    return sorted(arquivos, key=lambda caminho: caminho.name.lower())


def peek_sheet_names(path: Path) -> tuple[str, ...]:
    with zipfile.ZipFile(path) as arquivo_zip:
        with arquivo_zip.open("xl/workbook.xml") as workbook_xml:
            arvore = ElementTree.parse(workbook_xml)
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    elementos = arvore.getroot().findall(".//main:sheets/main:sheet", namespace)
    return tuple(elemento.attrib["name"] for elemento in elementos)


def detectar_formato(path: Path) -> FormatoContrato:
    nomes_normalizados = [_normalizar(nome) for nome in peek_sheet_names(path)]

    if "QQP" in nomes_normalizados or any(_PADRAO_LD.match(nome) for nome in nomes_normalizados):
        return FormatoContrato.QQP
    if "DADOS" in nomes_normalizados:
        return FormatoContrato.DADOS
    return FormatoContrato.DESCONHECIDO


def calcular_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(_TAMANHO_BLOCO), b""):
            digest.update(bloco)
    return digest.hexdigest()
