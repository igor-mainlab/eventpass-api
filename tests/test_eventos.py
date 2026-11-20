
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_listar_eventos():
    """
    Verifica se a API retorna corretamente
    a lista de eventos cadastrados.
    """

    resposta = client.get("/api/v1/eventos")

    assert resposta.status_code == 200

    dados = resposta.json()

    assert isinstance(dados, list)

    assert len(dados) > 0

    for evento in dados:
        assert "id_evento" in evento
        assert "nome" in evento
        assert "data" in evento
        assert "local" in evento
        assert "vagas_disponiveis" in evento
        assert "preco_ingresso" in evento
