"""Contratos da API PromoTech (Pydantic v2)."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CupomCreate(BaseModel):
    codigo: str = Field(min_length=3, max_length=30, description="Codigo promocional unico")
    percentual: int = Field(ge=1, le=50)
    data_validade: date
    limite_utilizacoes: int = Field(gt=0)
    ativo: bool = True

    @field_validator("codigo")
    @classmethod
    def normalizar_codigo(cls, valor: str) -> str:
        codigo = valor.strip().upper()
        if len(codigo) < 3:
            raise ValueError("O codigo deve possuir pelo menos 3 caracteres.")
        return codigo


class CupomUpdate(BaseModel):
    percentual: int = Field(ge=1, le=50)
    data_validade: date
    limite_utilizacoes: int = Field(gt=0)
    ativo: bool


class CupomResponse(BaseModel):
    id: int
    codigo: str
    percentual: int
    data_validade: date
    limite_utilizacoes: int
    utilizacoes: int
    ativo: bool


class AplicarCupomRequest(BaseModel):
    valor_compra: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AplicarCupomResponse(BaseModel):
    codigo: str
    valor_original: float
    percentual: int
    desconto: float
    valor_final: float
    utilizacoes: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
