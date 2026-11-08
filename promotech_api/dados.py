"""Armazenamento em memoria para o exercicio de testes automatizados.

A funcao reiniciar_dados() permite deixar os testes independentes.
"""

from copy import deepcopy
from threading import RLock

TRAVA = RLock()

_DADOS_INICIAIS = {
    "PROMO10": {
        "id": 1,
        "codigo": "PROMO10",
        "percentual": 10,
        "data_validade": "2099-12-31",
        "limite_utilizacoes": 10,
        "utilizacoes": 0,
        "ativo": True,
    },
    "EXPIRADO15": {
        "id": 2,
        "codigo": "EXPIRADO15",
        "percentual": 15,
        "data_validade": "2020-01-01",
        "limite_utilizacoes": 10,
        "utilizacoes": 0,
        "ativo": True,
    },
    "INATIVO20": {
        "id": 3,
        "codigo": "INATIVO20",
        "percentual": 20,
        "data_validade": "2099-12-31",
        "limite_utilizacoes": 10,
        "utilizacoes": 0,
        "ativo": False,
    },
    "ESGOTADO05": {
        "id": 4,
        "codigo": "ESGOTADO05",
        "percentual": 5,
        "data_validade": "2099-12-31",
        "limite_utilizacoes": 2,
        "utilizacoes": 2,
        "ativo": True,
    },
}

CUPONS: dict[str, dict] = {}
_PROXIMO_ID = 1


def reiniciar_dados() -> None:
    """Restaura dados iniciais. Uso exclusivamente local/testes, sem endpoint HTTP."""
    global _PROXIMO_ID
    with TRAVA:
        CUPONS.clear()
        CUPONS.update(deepcopy(_DADOS_INICIAIS))
        _PROXIMO_ID = 5


def gerar_id() -> int:
    global _PROXIMO_ID
    with TRAVA:
        atual = _PROXIMO_ID
        _PROXIMO_ID += 1
        return atual


reiniciar_dados()
