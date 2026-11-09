"""Etapa 1 e 2 - Cenários 3, 4 e 5 - cadastro de cupons (RN1 E RN2)"""

import pytest

@pytest.mark.positivo
def test_cenario3_cadatro_valido_persiste_dados_enviados(
    client, headers_admin, novo_cupom
):
    """Cenário 3: admin cadastra cupom válido e os dados armazenados
    correspondem aos enviados (verificado por um consulta posterior)."""
    corpo = novo_cupom(codigo="BLACK30", percentual=30, limite_uso=5)
    
    resp = client.post('/cupons', json=corpo, headers=headers_admin)
    
    assert resp.status_code == 201
    criado = resp.json()
    assert criado["codigo"] == "BLACK30"
    assert criado["utilizacoes"] == 0 # cupom nunca usado
    assert criado["id"] == 5 # proximo id após os 4 iniciais
    
    # prova de persistencia: relê o cupom pela API e compara campo a campo
    persistido = client.get(f'/cupons/BLACK30').json()
    for campo, valor in corpo.items():
        assert persistido[campo] == valor, f"Campo '{campo}' divergente"
    assert persistido == criado
    
    
@pytest.mark.positivo
def test_cadastro_normaliza_codigo_para_maiusculas(client, headers_admin, novo_cupom):
    resp = client.post(
        "/cupons", json=novo_cupom(codigo=" verao20 "), headers=headers_admin
    )
    
    assert resp.status_code == 201
    assert resp.json()["codigo"] == "VERAO20"
    
    
@pytest.mark.negativo
def test_cadastro_rejeita_codigo_duplicado(
    client, headers_admin, novo_cupom, snapshot_cupons
    ):
    """Cenário 4: admin tenta cadastrar cupom com código já existente e recebe erro 409
    e o cupom original permanece inalterado."""
    
    antes = snapshot_cupons()
    tentativa = novo_cupom(codigo="PROMO10", percentual=50, limite_uso=999)
    
    resp = client.post("/cupons", json=tentativa, headers=headers_admin)
    
    assert resp.status_code == 409
    assert "Já cadastrado" in resp.json()["detail"]
    assert snapshot_cupons() == antes # nada foi alterado no armazenamento de cupons
    original = client.get("/cupons/PROMO10").json()
    assert original["percentual"] == 10
    assert original["limite_uso"] == 10
    
    
pytest.mark.negativo
def test_cadastro_duplicado_ignora_diferenca_de_caixa(
    client, headers_admin, novo_cupom, snapshot_cupons
):
    """ 'promo10' é o mesmo codigo que 'PROMO10', portanto o cadastro deve ser rejeitado."""
    antes = snapshot_cupons()
    
    resp = client.post(
        "/cupons", json=novo_cupom(codigo="promo10"), headers=headers_admin
    ) 
    
    assert resp.status_code == 409
    assert snapshot_cupons() == antes
    
    
@pytest.mark.negativo
def test_cenario5_percentual_75_rejeitado(
    client, headers_admin, novo_cupom, snapshot_cupons
):
    """Cenário 5: admin tenta cadastrar cupom com percentual de desconto maior que 50%
    e recebe erro 422, sem alterar o armazenamento de cupons."""
    antes = snapshot_cupons()
    
    resp = client.post(
        "/cupons",
        json=novo_cupom(codigo="SUPER75", percentual=75),
        headers=headers_admin,
        )
        
    assert resp.status_code == 422
    campos_com_erro = [e["loc"][-1] for e in resp.json()["detail"]]
    assert "persentual" in campos_com_erro
    assert snapshot_cupons() == antes
    assert client.get("/cupons/SUPER75").status_code == 404
    
    
@pytest.mark.parametrize(
    "percentual", [0, 1, 49, 50])
@pytest.mark.negativo
def test_percentual_fora_da_faixa_rejeitado(
    client, headers_admin, novo_cupom, snapshot_cupons, percentual
):
    """valores logo abaixo/acima dos limites (análise de valor limite)"""
    antes = snapshot_cupons()
    
    resp = client.post(
        "/cupons",
        json=novo_cupom(codigo=f"LIMITE{percentual}", percentual=percentual),
        headers=headers_admin,
    )
    
    assert resp.status_code == 422
    assert snapshot_cupons() == antes
    assert client.get(f"/cupons/TESTE{percentual}").status_code == 404
    

@pytest.mark.parametrize("percentual", [1, 50])
@pytest.mark.positivo
def test_percentual_dentro_da_faixa_aceito(
    client, headers_admin, novo_cupom, snapshot_cupons, percentual
):
    """1% e 50% são aceitos, portanto o cupom é cadastrado com sucesso."""
    antes = snapshot_cupons()
    
    resp = client.post(
        "/cupons",
        json=novo_cupom(codigo=f"LIMITE{percentual}", percentual=percentual),
        headers=headers_admin,
    )
    
    assert resp.status_code == 201
    assert snapshot_cupons() != antes
    assert client.get(f"/cupons/LIMITE{percentual}").status_code == 200
