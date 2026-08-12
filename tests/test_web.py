def test_contratos_lista_planilha_e_permite_cadastro(client, arquivo_qqp):
    resposta = client.get("/contratos")
    assert resposta.status_code == 200
    assert arquivo_qqp.name.encode() in resposta.data

    resposta = client.post(
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

    assert resposta.status_code == 200
    assert b"Contrato Teste" in resposta.data


def test_dashboard_exibe_total_e_curva_planejada_apos_selecao(client, contrato_cadastrado):
    resposta = client.get("/dashboard")

    assert resposta.status_code == 200
    assert "Planejado (Curva S financeira)".encode() in resposta.data
    assert b"Valor or" in resposta.data


def test_dashboard_sem_contrato_ativo_redireciona_para_contratos(client):
    resposta = client.get("/dashboard")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/contratos")
