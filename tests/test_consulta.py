"""Etapa 1 - cenário 1 e 2 - consulta de cupons (RN3)"""
from datetime import date, timedelta
import pytest


@pytest.mark.positivo
def test_cenario1_consulta_cupom_ativo(client):
    """Cenário 1: a consulta devolve exatamente o cupom solicitado."""
    resp = client.get("/cupons/PROMO10")
    
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "codigo": "PROMO10",
        "percentual": 10,
        "data_validade": (date.today() + timedelta(days=30)).isoformat(),
        "limite_uso": 10,
        "utilizacoes": 0,
        "ativo": True,
    }
    
    
@pytest.mark.positivo
def test_consulta_nao_diferencia_maiusculas_de_minusculas(client):
    """o código é normalizado: 'promo10' e 'PROMO10' são equivalentes"""
    resp = client.get("/cupons/promo10")
    
    assert resp.status_code == 200
    assert resp.json()["codigo"] == "PROMO10"
    
    
@pytest.mark.negativo
def test_cenario2_consulta_cupom_inexistente(client):
    """Cenário 2: a consulta de cupom inexistente devolve erro 404"""
    resp = client.get("/cupons/NAOEXISTE")
    
    assert resp.status_code == 404
    assert "Não encontrado" in resp.json()["detail"].lower()
    
    
@pytest.mark.positivo
def test_listar_cupons_retorna_catalogo_inicial(client):
    """A listagem traz os 4 cupons iniciais, ordenados por Código"""
    resp = client.get("/cupons")
    
    assert resp.status_code == 200
    codigos = [c["codigo"] for c in resp.json()]
    assert codigos == ["ESGOTADO05", "ESGOTADO15", "ESGOTADO20", "PROMO10"]
