import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

from domain.models import FormatoContrato, MetadadosContrato, StatusCPU
from readers.common import calcular_sha256, detectar_formato, listar_arquivos_excel, peek_sheet_names
from readers.cpu import aplicar_cpu, ler_cpu
from readers.dados import ler_dados
from readers.qqp import ler_qqp
from services.curva_s import gerar_curva_s
from services.orcamento import resumir_orcamento
from storage.contratos import carregar_catalogo, registrar_contrato, salvar_catalogo, selecionar_contrato


class _CodificadorJSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, StatusCPU):
            return o.value
        return super().default(o)


def _formatar_moeda(valor) -> str:
    quantizado = Decimal(valor).quantize(Decimal("0.01"))
    negativo = quantizado < 0
    inteiro, centavos = f"{abs(quantizado):.2f}".split(".")

    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    parte_inteira = ".".join(grupos)

    resultado = f"R$ {parte_inteira},{centavos}"
    return f"-{resultado}" if negativo else resultado


def _possui_aba_cpu(caminho: Path) -> bool:
    return any(nome.strip().upper() == "CPU" for nome in peek_sheet_names(caminho))


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["EXCEL_DIR"] = Path("excel")
    app.config["CATALOGO_PATH"] = Path("data/contratos.json")
    if config:
        app.config.update(config)

    app.jinja_env.filters["moeda"] = _formatar_moeda

    def _pasta_excel() -> Path:
        return Path(app.config["EXCEL_DIR"])

    def _caminho_catalogo() -> Path:
        return Path(app.config["CATALOGO_PATH"])

    @app.get("/")
    def raiz():
        return redirect(url_for("listar_contratos"))

    @app.get("/contratos")
    def listar_contratos():
        catalogo = carregar_catalogo(_caminho_catalogo())
        registros_por_arquivo = {registro["arquivo"]: registro for registro in catalogo["contratos"]}

        arquivos = []
        for caminho in listar_arquivos_excel(_pasta_excel()):
            sha_atual = calcular_sha256(caminho)
            registro = registros_por_arquivo.get(caminho.name)
            arquivos.append(
                {
                    "nome_arquivo": caminho.name,
                    "formato": detectar_formato(caminho),
                    "sha256": sha_atual,
                    "registro": registro,
                    "fonte_alterada": registro is not None and registro["sha256"] != sha_atual,
                    "ativo": registro is not None and registro["id"] == catalogo["contrato_ativo_id"],
                }
            )

        return render_template("contratos.html", arquivos=arquivos, catalogo=catalogo)

    @app.post("/contratos")
    def cadastrar_contrato():
        pasta = _pasta_excel()
        nomes_validos = {caminho.name for caminho in listar_arquivos_excel(pasta)}
        nome_arquivo = request.form.get("arquivo", "")
        if nome_arquivo not in nomes_validos:
            abort(400, "Arquivo não encontrado entre as planilhas disponíveis")

        try:
            inicio = date.fromisoformat(request.form.get("inicio", ""))
        except ValueError:
            abort(400, "Data de início inválida")

        try:
            duracao_meses = int(request.form.get("duracao_meses", ""))
        except ValueError:
            abort(400, "Duração inválida")
        if duracao_meses <= 0:
            abort(400, "Duração deve ser maior que zero")

        metadados = MetadadosContrato(
            id=str(uuid.uuid4()),
            arquivo=nome_arquivo,
            sha256=calcular_sha256(pasta / nome_arquivo),
            nome=request.form.get("nome", "").strip(),
            cliente=request.form.get("cliente", "").strip(),
            obra=request.form.get("obra", "").strip(),
            inicio=inicio,
            duracao_meses=duracao_meses,
            atualizado_em=datetime.now(),
        )

        caminho_catalogo = _caminho_catalogo()
        catalogo = carregar_catalogo(caminho_catalogo)
        catalogo = registrar_contrato(catalogo, metadados)
        catalogo = selecionar_contrato(catalogo, metadados.id)
        salvar_catalogo(caminho_catalogo, catalogo)

        return redirect(url_for("listar_contratos"))

    @app.post("/contratos/<contrato_id>/selecionar")
    def selecionar_contrato_ativo(contrato_id):
        caminho_catalogo = _caminho_catalogo()
        catalogo = carregar_catalogo(caminho_catalogo)
        try:
            catalogo = selecionar_contrato(catalogo, contrato_id)
        except ValueError:
            abort(404)
        salvar_catalogo(caminho_catalogo, catalogo)
        return redirect(url_for("listar_contratos"))

    @app.get("/dashboard")
    def dashboard():
        catalogo = carregar_catalogo(_caminho_catalogo())
        contrato_ativo_id = catalogo["contrato_ativo_id"]
        registro = next(
            (item for item in catalogo["contratos"] if item["id"] == contrato_ativo_id), None
        )
        if contrato_ativo_id is None or registro is None:
            return redirect(url_for("listar_contratos"))

        caminho = _pasta_excel() / registro["arquivo"]
        formato = detectar_formato(caminho)
        if formato is FormatoContrato.QQP:
            contrato = ler_qqp(caminho)
        elif formato is FormatoContrato.DADOS:
            contrato = ler_dados(caminho)
        else:
            abort(400, "Formato de planilha não suportado")

        if _possui_aba_cpu(caminho):
            contrato = aplicar_cpu(contrato, ler_cpu(caminho))

        resumo = resumir_orcamento(contrato)
        inicio = date.fromisoformat(registro["inicio"])
        curva = gerar_curva_s(resumo["total_orcado"], inicio, registro["duracao_meses"])

        dados_grafico = json.dumps({"curvaS": curva}, cls=_CodificadorJSON)

        return render_template(
            "dashboard.html", resumo=resumo, curva=curva, contrato=registro, dados_grafico=dados_grafico
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
