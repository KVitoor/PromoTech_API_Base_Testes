"""Autenticacao demonstrativa via JWT e senhas derivadas com PBKDF2.

Credenciais ficticias para a atividade; nao utilizar essas contas em producao.
"""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

_CHAVE = os.getenv("JWT_SECRET_KEY", "chave-local-apenas-para-exercicios-nao-usar-em-producao")
_ALGORITMO = "HS256"
_EXPIRACAO_MINUTOS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
_OAUTH2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _hash_senha(senha: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 250_000)


def _criar_conta(usuario: str, senha: str, perfil: str) -> dict:
    salt = secrets.token_bytes(16)
    return {
        "usuario": usuario,
        "perfil": perfil,
        "salt": salt,
        "hash": _hash_senha(senha, salt),
    }


USUARIOS = {
    "admin": _criar_conta("admin", "Admin@123", "administrador"),
    "cliente": _criar_conta("cliente", "Cliente@123", "cliente"),
}


def autenticar(usuario: str, senha: str) -> dict | None:
    conta = USUARIOS.get(usuario)
    if not conta:
        return None
    tentativa = _hash_senha(senha, conta["salt"])
    if not hmac.compare_digest(tentativa, conta["hash"]):
        return None
    return conta


def gerar_token(usuario: str) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": usuario,
        "iat": agora,
        "exp": agora + timedelta(minutes=_EXPIRACAO_MINUTOS),
    }
    return jwt.encode(payload, _CHAVE, algorithm=_ALGORITMO)


def usuario_atual(token: str = Depends(_OAUTH2)) -> dict:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _CHAVE, algorithms=[_ALGORITMO])
        usuario = payload.get("sub")
        if not isinstance(usuario, str):
            raise erro
    except jwt.PyJWTError as exc:
        raise erro from exc
    conta = USUARIOS.get(usuario)
    if conta is None:
        raise erro
    return {"usuario": conta["usuario"], "perfil": conta["perfil"]}


def apenas_administrador(conta: dict = Depends(usuario_atual)) -> dict:
    if conta["perfil"] != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operacao permitida apenas para administradores",
        )
    return conta
