from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient


from dados import CUPONS, reiniciar_dados
from main import app

senhas = {
    "admin": "Admin123",
    "cliente": "Cliente123",
}

@pytest.fixture(autouse=True)
def _estado_inicial():
    """Restaura os cupons iniciais antes de cada teste."""
    reiniciar_dados()
    yield
    reiniciar_dados()
    
    
    @pytest.fixture
    def _client():
        """Fixture para criar um cliente de teste do FastAPI."""
        with TestClient(app) as c:
            yield c
            
            
            
@pytest.fixture
def _login(_client: TestClient, usuario:str) -> dict:
    resp = _client.post(
        "/auth/login",
        data = {"username": usuario, "password": senhas[usuario]},
    )
    assert resp.status_code == 200, f"Falha ao logar como {usuario}: {resp.text}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}



@pytest.fixture
def headers_admin(_client):
    return _login(_client, "admin")


@pytest.fixture
def headers_client(_client):
    return _login(_client, "cliente")


@pytest.fixture
def novo_cupom():
    """Retorna um novo cupom válido para testes."""
    
    def _fabrica(**sobrescrever) -> dict:
        corpo = {
            "codigo": "NOVO25",
            "percentual": 25,
            "data_validade": (date.today() + timedelta(days=15)).isoformat(),
            "limite_uso": 3,
            "ativo": True,
        }
        corpo.update(sobrescrever)
        return corpo
    
    return _fabrica


@pytest.fixture
def cadastrar(_client, headers_admin, novo_cupom):
    """Fixture para cadastrar um cupom e retornar o cupom cadastrado."""
    
    def _cadastrar(**campos) -> dict:
        resp = _client.post("/cupons", json=novo_cupom(**campos), headers=headers_admin)
        assert resp.status_code == 201, f"Falha ao cadastrar cupom: {resp.text}"
        return resp.json()
    
    return _cadastrar


@pytest.fixture
def ontem() -> str:
    """Retorna a data de ontem no formato ISO."""
    return (date.today() - timedelta(days=1)).isoformat()


@pytest.fixture
def snapshot_cupons():
    """Devolve uma função que tira 'foto' independente do catálogo atual.
    
    Útil para provar que operações regeitadas NÃO alteram nenhum registro.
    """
    from copy import deepcopy
    return lambda: deepcopy(CUPONS)
