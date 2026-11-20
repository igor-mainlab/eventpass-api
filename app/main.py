from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import (
    EventoDTO,
    ComprarIngressoDTO,
    IngressoDTO,
    CheckinDTO,
    CheckinRespostaDTO,
    ErroPadronizadoDTO
)

from app.services import (
    listar_eventos,
    comprar_ingresso,
    realizar_checkin,
    consultar_ingresso
)

app = FastAPI(
    title="EventPass API",
    description="API RESTful para gestão de eventos e ingressos virtuais.",
    version="1.0.0"
)


@app.get("/")
def pagina_inicial():
    """
    Endpoint inicial para verificar o funcionamento da API.
    """
    return {
        "mensagem": "Bem-vindo à EventPass API!",
        "status": "online"
    }

@app.get(
    "/api/v1/eventos",
    response_model=list[EventoDTO],
    status_code=200,
    tags=["Eventos"],
    summary="Listar eventos disponíveis",
    description="Retorna a lista de eventos cadastrados e suas vagas disponíveis.",
    responses={
        500: {
            "model": ErroPadronizadoDTO,
            "description": "Erro interno do servidor."
        }
    }
)
def obter_eventos():
    """Consulta os eventos disponíveis na plataforma."""
    return listar_eventos()


@app.post(
    "/api/v1/ingressos",
    response_model=IngressoDTO,
    status_code=201,
    tags=["Ingressos"],
    summary="Emitir ingresso",
    description="Emite um ingresso para um evento com vagas disponíveis.",
    responses={
        400: {
            "model": ErroPadronizadoDTO,
            "description": "Evento sem vagas disponíveis."
        },
        404: {
            "model": ErroPadronizadoDTO,
            "description": "Evento não encontrado."
        },
        422: {
            "model": ErroPadronizadoDTO,
            "description": "Dados inválidos."
        }
    }
)
def emitir_ingresso(payload: ComprarIngressoDTO):
    """Recebe os dados do comprador e emite um ingresso."""

    try:
        return comprar_ingresso(payload)

    except ValueError as erro:
        codigo = str(erro)

        if codigo == "EVENTO_NAO_ENCONTRADO":
            raise HTTPException(
                status_code=404,
                detail={
                    "codigo_erro": codigo,
                    "mensagem": "O evento informado não foi encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        if codigo == "EVENTO_SEM_VAGAS":
            raise HTTPException(
                status_code=400,
                detail={
                    "codigo_erro": codigo,
                    "mensagem": "Não há vagas disponíveis para este evento.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        raise


@app.post(
    "/api/v1/checkin",
    response_model=CheckinRespostaDTO,
    status_code=200,
    tags=["Check-in"],
    summary="Validar entrada de ingresso",
    description="Valida um ingresso e impede sua reutilização.",
    responses={
        404: {
            "model": ErroPadronizadoDTO,
            "description": "Ingresso não encontrado."
        },
        409: {
            "model": ErroPadronizadoDTO,
            "description": "Ingresso já utilizado ou cancelado."
        },
        422: {
            "model": ErroPadronizadoDTO,
            "description": "Dados inválidos."
        }
    }
)
def validar_entrada(payload: CheckinDTO):
    """Valida o ingresso apresentado na portaria."""

    try:
        return realizar_checkin(payload)

    except ValueError as erro:
        codigo = str(erro)

        mensagens = {
            "INGRESSO_NAO_ENCONTRADO": (
                404,
                "O ingresso informado não foi encontrado."
            ),
            "INGRESSO_JA_UTILIZADO": (
                409,
                "Este ingresso já foi utilizado."
            ),
            "INGRESSO_CANCELADO": (
                409,
                "Este ingresso está cancelado."
            )
        }

        if codigo in mensagens:
            status_http, mensagem = mensagens[codigo]

            raise HTTPException(
                status_code=status_http,
                detail={
                    "codigo_erro": codigo,
                    "mensagem": mensagem,
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat()
                }
            )

        raise


@app.get(
    "/api/v1/ingressos/{id_ingresso}",
    response_model=IngressoDTO,
    status_code=200,
    tags=["Ingressos"],
    summary="Consultar ingresso pelo identificador",
    description="Retorna os dados e o status atual de um ingresso.",
    responses={
        404: {
            "model": ErroPadronizadoDTO,
            "description": "Ingresso não encontrado."
        },
        422: {
            "model": ErroPadronizadoDTO,
            "description": "Dados inválidos."
        }
    }
)
def obter_ingresso(id_ingresso: str):
    """Consulta um ingresso pelo identificador único."""

    try:
        return consultar_ingresso(id_ingresso)

    except ValueError as erro:
        codigo = str(erro)

        if codigo == "INGRESSO_NAO_ENCONTRADO":
            raise HTTPException(
                status_code=404,
                detail={
                    "codigo_erro": codigo,
                    "mensagem": "O ingresso informado não foi encontrado.",
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat()
                }
            )

        raise

@app.exception_handler(HTTPException)
async def tratar_erros_http(
    request: Request,
    exc: HTTPException
):
    """Padroniza as respostas de erros HTTP da aplicação."""

    if isinstance(exc.detail, dict):
        if all(
            campo in exc.detail
            for campo in (
                "codigo_erro",
                "mensagem",
                "timestamp"
            )
        ):
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail,
                headers=exc.headers
            )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "codigo_erro": f"HTTP_{exc.status_code}",
            "mensagem": str(exc.detail),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        },
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def tratar_erros_validacao(
    request: Request,
    exc: RequestValidationError
):
    """Padroniza erros de validação dos dados recebidos."""

    return JSONResponse(
        status_code=422,
        content={
            "codigo_erro": "DADOS_INVALIDOS",
            "mensagem": "Os dados enviados são inválidos.",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )

@app.exception_handler(Exception)
async def tratar_erro_interno(
    request: Request,
    exc: Exception
):
    """Trata falhas internas inesperadas da aplicação."""

    return JSONResponse(
        status_code=500,
        content={
            "codigo_erro": "ERRO_INTERNO",
            "mensagem": (
                "Ocorreu um erro interno no servidor."
            ),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )
