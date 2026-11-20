import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone

from app.database import conectar, inicializar_banco
from app.schemas import (
    EventoDTO,
    ComprarIngressoDTO,
    IngressoDTO,
    CheckinDTO,
    CheckinRespostaDTO
)


def cadastrar_eventos_iniciais():
    """Insere eventos de exemplo, caso ainda não existam."""

    inicializar_banco()

    eventos = [
        (
            "EVT-10",
            "Congresso de TI Ananindeua 2026",
            "2026-12-01T09:00:00Z",
            "Auditório IFPA",
            120,
            50.00
        ),
        (
            "EVT-20",
            "Workshop de Computação em Nuvem",
            "2026-12-10T14:00:00Z",
            "Campus Ananindeua",
            60,
            25.00
        )
    ]

    with conectar() as conexao:
        conexao.executemany(
            """
            INSERT OR IGNORE INTO eventos (
                id_evento,
                nome,
                data,
                local,
                vagas_disponiveis,
                preco_ingresso
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            eventos
        )
        conexao.commit()


def listar_eventos():
    """Retorna os eventos que ainda possuem vagas."""

    with conectar() as conexao:
        registros = conexao.execute(
            """
            SELECT
                id_evento,
                nome,
                data,
                local,
                vagas_disponiveis,
                preco_ingresso
            FROM eventos
            WHERE vagas_disponiveis > 0
            ORDER BY data
            """
        ).fetchall()

    return [
        EventoDTO(**dict(registro))
        for registro in registros
    ]


def comprar_ingresso(payload: ComprarIngressoDTO) -> IngressoDTO:
    """Emite um ingresso e decrementa uma vaga do evento."""

    with conectar() as conexao:
        # Bloqueia outra escrita durante a operação.
        conexao.execute("BEGIN IMMEDIATE")

        evento = conexao.execute(
            "SELECT * FROM eventos WHERE id_evento = ?",
            (payload.evento_id,)
        ).fetchone()

        if evento is None:
            raise ValueError("EVENTO_NAO_ENCONTRADO")

        if evento["vagas_disponiveis"] <= 0:
            raise ValueError("EVENTO_SEM_VAGAS")

        id_ingresso = f"ING-{uuid.uuid4().hex[:12].upper()}"

        # Hash SHA-256 único para identificação do ingresso.
        identificador = uuid.uuid4().hex
        qrcode_hash = hashlib.sha256(
            identificador.encode("utf-8")
        ).hexdigest()

        data_emissao = datetime.now(timezone.utc)

        conexao.execute(
            """
            INSERT INTO ingressos (
                id_ingresso,
                evento_id,
                comprador_nome,
                comprador_cpf,
                comprador_email,
                qrcode_hash,
                status,
                data_emissao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_ingresso,
                payload.evento_id,
                payload.comprador_nome,
                payload.comprador_cpf,
                str(payload.comprador_email),
                qrcode_hash,
                "EMITIDO",
                data_emissao.isoformat()
            )
        )

        conexao.execute(
            """
            UPDATE eventos
            SET vagas_disponiveis = vagas_disponiveis - 1
            WHERE id_evento = ?
            """,
            (payload.evento_id,)
        )

        conexao.commit()

    return IngressoDTO(
        id_ingresso=id_ingresso,
        evento_nome=evento["nome"],
        comprador_nome=payload.comprador_nome,
        qrcode_hash=qrcode_hash,
        status="EMITIDO",
        data_emissao=data_emissao
    )


def realizar_checkin(payload: CheckinDTO) -> CheckinRespostaDTO:
    """Valida um ingresso e registra sua utilização na portaria."""

    with conectar() as conexao:
        # Garante uma transação de escrita.
        conexao.execute("BEGIN IMMEDIATE")

        ingresso = conexao.execute(
            """
            SELECT
                i.id_ingresso,
                i.comprador_nome,
                i.status,
                e.nome AS evento_nome
            FROM ingressos AS i
            JOIN eventos AS e
                ON i.evento_id = e.id_evento
            WHERE i.qrcode_hash = ?
            """,
            (payload.qrcode_hash,)
        ).fetchone()

        if ingresso is None:
            raise ValueError("INGRESSO_NAO_ENCONTRADO")

        if ingresso["status"] == "UTILIZADO":
            raise ValueError("INGRESSO_JA_UTILIZADO")

        if ingresso["status"] == "CANCELADO":
            raise ValueError("INGRESSO_CANCELADO")

        data_hora_checkin = datetime.now(timezone.utc)

        conexao.execute(
            """
            UPDATE ingressos
            SET status = 'UTILIZADO'
            WHERE id_ingresso = ?
            """,
            (ingresso["id_ingresso"],)
        )

        conexao.execute(
            """
            INSERT INTO checkins (
                id_ingresso,
                portaria_id,
                data_hora_checkin
            )
            VALUES (?, ?, ?)
            """,
            (
                ingresso["id_ingresso"],
                payload.portaria_id,
                data_hora_checkin.isoformat()
            )
        )

        conexao.commit()

    return CheckinRespostaDTO(
        status_acesso="LIBERADO",
        comprador_nome=ingresso["comprador_nome"],
        evento_nome=ingresso["evento_nome"],
        data_hora_checkin=data_hora_checkin
    )


def consultar_ingresso(id_ingresso: str) -> IngressoDTO:
    """Consulta um ingresso pelo identificador único."""

    with conectar() as conexao:
        ingresso = conexao.execute(
            """
            SELECT
                i.id_ingresso,
                e.nome AS evento_nome,
                i.comprador_nome,
                i.qrcode_hash,
                i.status,
                i.data_emissao
            FROM ingressos AS i
            JOIN eventos AS e
                ON i.evento_id = e.id_evento
            WHERE i.id_ingresso = ?
            """,
            (id_ingresso,)
        ).fetchone()

    if ingresso is None:
        raise ValueError("INGRESSO_NAO_ENCONTRADO")

    return IngressoDTO(**dict(ingresso))
