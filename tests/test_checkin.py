
from fastapi.testclient import TestClient

from app.main import app
from app.database import conectar

client = TestClient(app)


def test_checkin_ingresso():
    """
    Verifica se um ingresso pode ser utilizado
    apenas uma vez.
    """

    # Primeiro, emite um ingresso válido.
    dados_compra = {
        "evento_id": "EVT-10",
        "comprador_nome": "Comprador Check-in",
        "comprador_cpf": "12345678909",
        "comprador_email": "checkin@example.com"
    }

    resposta_compra = client.post(
        "/api/v1/ingressos",
        json=dados_compra
    )

    assert resposta_compra.status_code == 201

    ingresso = resposta_compra.json()
    qrcode_hash = ingresso["qrcode_hash"]

    dados_checkin = {
        "qrcode_hash": qrcode_hash,
        "portaria_id": "PORTAL-TESTE"
    }

    # Primeiro check-in: acesso liberado.
    primeira_resposta = client.post(
        "/api/v1/checkin",
        json=dados_checkin
    )

    assert primeira_resposta.status_code == 200

    resultado = primeira_resposta.json()

    assert resultado["status_acesso"] == "LIBERADO"
    assert resultado["comprador_nome"] == "Comprador Check-in"
    assert "data_hora_checkin" in resultado

    # Segundo check-in: acesso negado.
    segunda_resposta = client.post(
        "/api/v1/checkin",
        json=dados_checkin
    )

    assert segunda_resposta.status_code == 409

    erro = segunda_resposta.json()

    assert erro["codigo_erro"] == "INGRESSO_JA_UTILIZADO"
    assert "mensagem" in erro
    assert "timestamp" in erro

def test_checkin_hash_inexistente():
    """
    Verifica se a API rejeita o check-in
    de um ingresso com hash inexistente.
    """

    dados_checkin = {
        "qrcode_hash": "HASH-INEXISTENTE",
        "portaria_id": "PORTAL-TESTE"
    }

    resposta = client.post(
        "/api/v1/checkin",
        json=dados_checkin
    )

    assert resposta.status_code == 404

    erro = resposta.json()

    assert erro["codigo_erro"] == "INGRESSO_NAO_ENCONTRADO"
    assert "mensagem" in erro
    assert "timestamp" in erro

def test_checkin_ingresso_cancelado():
    """
    Verifica se um ingresso cancelado
    não permite a entrada no evento.
    """

    # Emite um ingresso válido.
    dados_compra = {
        "evento_id": "EVT-10",
        "comprador_nome": "Comprador Cancelado",
        "comprador_cpf": "12345678909",
        "comprador_email": "cancelado@example.com"
    }

    resposta_compra = client.post(
        "/api/v1/ingressos",
        json=dados_compra
    )

    assert resposta_compra.status_code == 201

    ingresso = resposta_compra.json()

    # Simula o cancelamento no banco temporário.
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE ingressos
            SET status = 'CANCELADO'
            WHERE id_ingresso = ?
            """,
            (ingresso["id_ingresso"],)
        )

    # Tenta realizar o check-in.
    resposta = client.post(
        "/api/v1/checkin",
        json={
            "qrcode_hash": ingresso["qrcode_hash"],
            "portaria_id": "PORTAL-TESTE"
        }
    )

    assert resposta.status_code == 409

    erro = resposta.json()

    assert erro["codigo_erro"] == "INGRESSO_CANCELADO"
    assert "mensagem" in erro
    assert "timestamp" in erro
