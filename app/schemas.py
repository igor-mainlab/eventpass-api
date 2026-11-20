
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EventoDTO(BaseModel):
    """Representa um evento disponível na plataforma."""

    model_config = ConfigDict(extra="forbid")

    id_evento: str
    nome: str
    data: datetime
    local: str
    vagas_disponiveis: int = Field(ge=0)
    preco_ingresso: float = Field(ge=0)


class ComprarIngressoDTO(BaseModel):
    """Dados necessários para emitir um ingresso."""

    model_config = ConfigDict(extra="forbid")

    evento_id: str = Field(min_length=1)
    comprador_nome: str = Field(min_length=1)
    comprador_cpf: str = Field(min_length=1)
    comprador_email: EmailStr


class IngressoDTO(BaseModel):
    """Dados públicos de um ingresso emitido."""

    model_config = ConfigDict(extra="forbid")

    id_ingresso: str
    evento_nome: str
    comprador_nome: str
    qrcode_hash: str
    status: Literal["EMITIDO", "UTILIZADO", "CANCELADO"]
    data_emissao: datetime


class CheckinDTO(BaseModel):
    """Dados enviados pela portaria para validar o ingresso."""

    model_config = ConfigDict(extra="forbid")

    qrcode_hash: str = Field(min_length=1)
    portaria_id: str = Field(min_length=1)


class CheckinRespostaDTO(BaseModel):
    """Resposta de uma validação de entrada bem-sucedida."""

    model_config = ConfigDict(extra="forbid")

    status_acesso: Literal["LIBERADO"]
    comprador_nome: str
    evento_nome: str
    data_hora_checkin: datetime


class ErroPadronizadoDTO(BaseModel):
    """Formato obrigatório para respostas de erro da API."""

    codigo_erro: str
    mensagem: str
    timestamp: datetime
