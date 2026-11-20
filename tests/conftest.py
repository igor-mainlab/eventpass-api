
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import database
from app.services import cadastrar_eventos_iniciais


@pytest.fixture(autouse=True)
def banco_temporario(monkeypatch):
    """
    Cria um banco temporário isolado para cada teste.
    """

    with TemporaryDirectory() as diretorio:
        caminho = Path(diretorio) / "eventpass_test.db"

        # Redireciona as conexões para o banco temporário.
        monkeypatch.setattr(
            database,
            "DB_PATH",
            caminho
        )

        # Cria as tabelas e popula os eventos de exemplo.
        database.inicializar_banco()
        cadastrar_eventos_iniciais()

        yield caminho
