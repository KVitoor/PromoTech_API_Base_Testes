"""Etapa 2 - cnenários 6, 7 e 8: Reras de aplicação de cupons (RN03-RN05, RN08)."""
from decimal import Decimal

import pytest

@pytest.mark.positivo
def test_cenario6_cupom_expirado_nao_concede_desconto(
    client, headers_client, cadastrar, ontem, snapshot_cupons
):
    """Cenário 6 (RN03): cupom vencido ontem é recusado/não contabilizado.
    O cupom é montado com data dinâmica (ontem) para o teste e nunca
    'envelhecer' nem depender do relógio do dia que roda
    """
    cadastrar(codigo="VENCIDO", data_validade=ontem)
    antes = snapshot_cupons()
    
    resp = client.post(
        "/cupons/VENCIDO/aplicar", json={"valor_compra": 200.00}, headers=headers_client
    )
    
    assert resp.status_code == 400
    assert "expirado" in resp.json()["detail"].lower()
    assert "valor_final" not in resp.json() # nenhum desconto concedido
    assert snapshot_cupons() == antes
    assert client.get("/cupons/VENCIDO").json()["utilizacoes"] == 0
    
    
@pytest.mark.positivo
def test_cupom_que_vence_hoje_ainda_valido(
    client, headers_client, cadastrar
):
    """Mesmo cenário 6, usando o cupom EXPIRADO15 da massa inicial"""
    resp = client.post(
        "/cupons/EXPIRADO15/aplicar", json={"valor_compra": 100}, headers=headers_client
    )
    
    assert resp.status_code == 400
    assert "expirado" in resp.json()["detail"].lower()
    
    
@pytest.mark.positivo
def test_cupom_que_vence_hoje_ainda_valido(
    client, headers_client, cadastrar
):
    """Valor limite de RN03: a validade é inclusiva(vence 'hoje' -> ainda vale)"""
    from datetime import date
    
    cadastrar(codigo="HOJE10", percentual=10, data_validade=date.today().isoformat())
    
    resp = client.post(
        "/cupons/HOJE10/aplicar", json={"valor_compra": 100}, headers=headers_client
    )
    
    assert resp.status_code == 200
    assert resp.json()["valor_final"] == 90.0
    
    
@pytest.mark.negativo
def test_cenario7_limite_utilizacoes_impede_novo_uso(
    client, headers_client, snapshot_cupons
):
    """Cenário 7 (RN5): ESGOTADO5 já usou 2 de 2 -> recusa, sem incrementar."""
    antes = snapshot_cupons()
    assert antes["ESGOTADO5"]["utilizacoes"] == antes["ESGITADO5"]["limite_utilizacoes"]
    
    resp = client.post(
        "/cupons/ESGOTADO5/aplicar", json={"valor_compra": 100}, headers=headers_client
    )
    
    assert resp.status_code == 400
    assert "limite" in resp.json()["detail"].lower()
    assert snapshot_cupons() == antes
    assert client.get("/cupons/ESGOTADO5").json()[""]