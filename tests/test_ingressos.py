
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import conectar


client = TestClient(app)


def test_emitir_ingresso():
    """
    Verifica a emissão de um ingresso para
    um evento de teste com vagas disponíveis.
    """

    id_evento = f"TEST-{uuid4().hex[:12]}"

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO eventos (
                id_evento,
                nome,
                data,
                local,
                vagas_disponiveis,
                preco_ingresso
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                id_evento,
                "Evento de Teste Automatizado",
                "2026-12-20T10:00:00Z",
                "Ambiente de Testes",
                10,
                25.0
            )
        )

    dados = {
        "evento_id": id_evento,
        "comprador_nome": "Comprador Automatizado",
        "comprador_cpf": "12345678909",
        "comprador_email": "teste@example.com"
    }

    resposta = client.post(
        "/api/v1/ingressos",
        json=dados
    )

    assert resposta.status_code == 201

    ingresso = resposta.json()

    assert "id_ingresso" in ingresso
    assert ingresso["evento_nome"] == "Evento de Teste Automatizado"
    assert ingresso["comprador_nome"] == "Comprador Automatizado"
    assert ingresso["status"] == "EMITIDO"
    assert "qrcode_hash" in ingresso

def test_emitir_ingresso_evento_inexistente():
    """
    Verifica se a API impede a emissão
    de ingressos para eventos inexistentes.
    """

    dados = {
        "evento_id": "EVT-INEXISTENTE",
        "comprador_nome": "Comprador Teste",
        "comprador_cpf": "12345678909",
        "comprador_email": "teste@example.com"
    }

    resposta = client.post(
        "/api/v1/ingressos",
        json=dados
    )

    assert resposta.status_code == 404

    erro = resposta.json()

    assert erro["codigo_erro"] == "EVENTO_NAO_ENCONTRADO"

    assert "mensagem" in erro
    assert "timestamp" in erro

def test_emitir_ingresso_email_invalido():
    """
    Verifica se a API rejeita a emissão
    de ingressos com e-mail inválido.
    """

    dados = {
        "evento_id": "EVT-10",
        "comprador_nome": "Comprador Teste",
        "comprador_cpf": "12345678909",
        "comprador_email": "email-invalido"
    }

    resposta = client.post(
        "/api/v1/ingressos",
        json=dados
    )

    assert resposta.status_code == 422

    erro = resposta.json()

    assert erro["codigo_erro"] == "DADOS_INVALIDOS"

    assert "mensagem" in erro
    assert "timestamp" in erro

def test_emitir_ingresso_evento_sem_vagas():
    """
    Verifica se a API impede a emissão
    de ingressos para eventos sem vagas.
    """

    id_evento = f"TEST-LOTADO-{uuid4().hex[:8]}"

    # Cadastra um evento sem vagas disponíveis.
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO eventos (
                id_evento,
                nome,
                data,
                local,
                vagas_disponiveis,
                preco_ingresso
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                id_evento,
                "Evento Lotado",
                "2026-12-20T10:00:00Z",
                "Ambiente de Testes",
                0,
                50.0
            )
        )

    dados = {
        "evento_id": id_evento,
        "comprador_nome": "Comprador Teste",
        "comprador_cpf": "12345678909",
        "comprador_email": "teste@example.com"
    }

    resposta = client.post(
        "/api/v1/ingressos",
        json=dados
    )

    assert resposta.status_code == 400

    erro = resposta.json()

    assert erro["codigo_erro"] == "EVENTO_SEM_VAGAS"
    assert "mensagem" in erro
    assert "timestamp" in erro
