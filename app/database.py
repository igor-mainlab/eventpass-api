import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "eventpass.db"

@contextmanager
def conectar():
    """Abre e fecha uma conexão SQLite com segurança."""

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def inicializar_banco():
    """Cria as tabelas necessárias, caso não existam."""

    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id_evento TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                local TEXT NOT NULL,
                vagas_disponiveis INTEGER NOT NULL
                    CHECK (vagas_disponiveis >= 0),
                preco_ingresso REAL NOT NULL
                    CHECK (preco_ingresso >= 0)
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS ingressos (
                id_ingresso TEXT PRIMARY KEY,
                evento_id TEXT NOT NULL,
                comprador_nome TEXT NOT NULL,
                comprador_cpf TEXT NOT NULL,
                comprador_email TEXT NOT NULL,
                qrcode_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'EMITIDO'
                    CHECK (status IN (
                        'EMITIDO', 'UTILIZADO', 'CANCELADO'
                    )),
                data_emissao TEXT NOT NULL,
                FOREIGN KEY (evento_id)
                    REFERENCES eventos(id_evento)
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id_checkin INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ingresso TEXT NOT NULL UNIQUE,
                portaria_id TEXT NOT NULL,
                data_hora_checkin TEXT NOT NULL,
                FOREIGN KEY (id_ingresso)
                    REFERENCES ingressos(id_ingresso)
            )
        """)

        conexao.commit()
