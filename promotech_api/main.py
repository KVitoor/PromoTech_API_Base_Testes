"""API PromoTech para a atividade individual de testes automatizados.

Esta API ja vem implementada; cabe aos alunos escrever e executar os testes.
Os cupons ficam em memoria, sem banco de dados, para facilitar o isolamento.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from dados import CUPONS, TRAVA, gerar_id
from schemas import (
    AplicarCupomRequest,
    AplicarCupomResponse,
    CupomCreate,
    CupomResponse,
    CupomUpdate,
    TokenResponse,
)
from seguranca import apenas_administrador, autenticar, gerar_token, usuario_atual

app = FastAPI(
    title="API PromoTech — Cupons Promocionais",
    description="API-base para atividade individual de testes automatizados.",
    version="1.0.0",
)


def _localizar_cupom(codigo: str) -> dict:
    cupom = CUPONS.get(codigo.strip().upper())
    if cupom is None:
        raise HTTPException(status_code=404, detail="Cupom nao encontrado")
    return cupom


@app.get("/", tags=["Sistema"])
def inicio():
    return {"mensagem": "API PromoTech em execucao"}


@app.post("/auth/login", response_model=TokenResponse, tags=["Autenticacao"])
def login(form: OAuth2PasswordRequestForm = Depends()):
    conta = autenticar(form.username, form.password)
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha invalidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": gerar_token(conta["usuario"]), "token_type": "bearer"}


@app.get("/auth/me", tags=["Autenticacao"])
def meus_dados(conta: dict = Depends(usuario_atual)):
    return conta


@app.get("/cupons", response_model=list[CupomResponse], tags=["Cupons"])
def listar_cupons():
    with TRAVA:
        return [CUPONS[codigo].copy() for codigo in sorted(CUPONS)]


@app.get("/cupons/{codigo}", response_model=CupomResponse, tags=["Cupons"])
def buscar_cupom(codigo: str):
    with TRAVA:
        return _localizar_cupom(codigo).copy()


@app.post(
    "/cupons",
    response_model=CupomResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Cupons"],
)
def cadastrar_cupom(dados: CupomCreate, _: dict = Depends(apenas_administrador)):
    with TRAVA:
        if dados.codigo in CUPONS:
            raise HTTPException(status_code=409, detail="Codigo promocional ja cadastrado")
        cupom = {"id": gerar_id(), **dados.model_dump(mode="json"), "utilizacoes": 0}
        CUPONS[dados.codigo] = cupom
        return cupom.copy()


@app.put("/cupons/{codigo}", response_model=CupomResponse, tags=["Cupons"])
def atualizar_cupom(
    codigo: str, dados: CupomUpdate, _: dict = Depends(apenas_administrador)
):
    with TRAVA:
        cupom = _localizar_cupom(codigo)
        if dados.limite_utilizacoes < cupom["utilizacoes"]:
            raise HTTPException(
                status_code=400,
                detail="Limite nao pode ser menor que o numero de utilizacoes existentes",
            )
        cupom.update(dados.model_dump(mode="json"))
        return cupom.copy()


@app.delete("/cupons/{codigo}", status_code=204, tags=["Cupons"])
def excluir_cupom(codigo: str, _: dict = Depends(apenas_administrador)):
    with TRAVA:
        cupom = _localizar_cupom(codigo)
        del CUPONS[cupom["codigo"]]
    return Response(status_code=204)


@app.post(
    "/cupons/{codigo}/aplicar",
    response_model=AplicarCupomResponse,
    tags=["Cupons"],
)
def aplicar_cupom(
    codigo: str, dados: AplicarCupomRequest, _: dict = Depends(usuario_atual)
):
    with TRAVA:
        cupom = _localizar_cupom(codigo)
        if not cupom["ativo"]:
            raise HTTPException(status_code=400, detail="Cupom inativo")
        if date.fromisoformat(cupom["data_validade"]) < date.today():
            raise HTTPException(status_code=400, detail="Cupom expirado")
        if cupom["utilizacoes"] >= cupom["limite_utilizacoes"]:
            raise HTTPException(status_code=400, detail="Limite de utilizacoes atingido")

        valor = dados.valor_compra
        desconto = (valor * Decimal(cupom["percentual"]) / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total = valor - desconto
        cupom["utilizacoes"] += 1
        return {
            "codigo": cupom["codigo"],
            "valor_original": float(valor),
            "percentual": cupom["percentual"],
            "desconto": float(desconto),
            "valor_final": float(total),
            "utilizacoes": cupom["utilizacoes"],
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
