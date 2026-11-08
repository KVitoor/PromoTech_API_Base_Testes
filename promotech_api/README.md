# PromoTech — API-base para testes automatizados

Esta API é o **sistema sob teste** da atividade individual da Aula 12. Ela está implementada e não contém os testes: os alunos devem criá-los.

## 1. Instalação

Requer Python 3.10+.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Execução

Na pasta do projeto:

```bash
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para acessar o Swagger.

## 3. Usuários de demonstração

**Somente para o laboratório:**

| Login | Senha | Perfil |
|---|---|---|
| `admin` | `Admin@123` | administrador |
| `cliente` | `Cliente@123` | cliente |

O `POST /auth/login` recebe **formulário** (`application/x-www-form-urlencoded`) com campos `username` e `password`, não JSON. Retorna um `access_token`, a ser enviado como `Authorization: Bearer <token>`. No Swagger, use o botão **Authorize**.

O cadastro de usuários não faz parte desta API-base. As senhas de demonstração são verificadas por derivação PBKDF2; não são guardadas em texto puro dentro do dicionário de usuários.

## 4. Endpoints

| Método | Rota | Acesso | Resposta esperada |
|---|---|---|---|
| POST | `/auth/login` | público | token ou 401 |
| GET | `/auth/me` | autenticado | usuário atual ou 401 |
| GET | `/cupons` | público | lista de cupons |
| GET | `/cupons/{codigo}` | público | cupom ou 404 |
| POST | `/cupons` | administrador | 201, 403, 409 ou 422 |
| PUT | `/cupons/{codigo}` | administrador | 200, 400, 403, 404 ou 422 |
| DELETE | `/cupons/{codigo}` | administrador | 204, 403 ou 404 |
| POST | `/cupons/{codigo}/aplicar` | autenticado | cálculo do desconto; erros 400, 401, 404 ou 422 |

### Exemplo de criação (`POST /cupons`)

```json
{
  "codigo": "DESCONTO12",
  "percentual": 12,
  "data_validade": "2099-12-31",
  "limite_utilizacoes": 5,
  "ativo": true
}
```

### Exemplo de atualização (`PUT /cupons/DESCONTO12`)

```json
{
  "percentual": 15,
  "data_validade": "2099-12-31",
  "limite_utilizacoes": 6,
  "ativo": true
}
```

### Exemplo de aplicação (`POST /cupons/PROMO10/aplicar`)

```json
{"valor_compra": 200.00}
```

Resposta esperada, antes de outras utilizações:

```json
{
  "codigo": "PROMO10",
  "valor_original": 200.0,
  "percentual": 10,
  "desconto": 20.0,
  "valor_final": 180.0,
  "utilizacoes": 1
}
```

## 5. Cupons disponíveis inicialmente

| Código | Situação | Finalidade didática |
|---|---|---|
| `PROMO10` | válido, ativo, 10%, limite de 10 utilizações | aplicação e cálculo |
| `EXPIRADO15` | data vencida | regra de expiração |
| `INATIVO20` | desativado | regra de ativação |
| `ESGOTADO05` | limite já alcançado | regra de uso máximo |

Regras: código único (comparação sem distinção de maiúsculas/minúsculas); percentual de 1 a 50%; limite positivo; não aplicar cupom vencido, inativo ou esgotado; somente administradores alteram o catálogo; aplicação exige usuário autenticado.

## 6. Orientações para testes

A API usa um **dicionário em memória**, sem banco de dados, para concentrar a atividade na automação. Os dados voltam ao estado inicial ao reiniciar o processo.

A função `reiniciar_dados()` em `dados.py` restaura os cupons iniciais e **pode ser chamada pela configuração de testes**. Ela não é disponibilizada por HTTP.

O professor pode pedir aos alunos que criem a pasta `tests/` com os arquivos desejados. Execute os testes com:

```bash
pytest -v
```

O repositório-base **não inclui testes nem gabarito**.

## 7. Avisos

- Esta aplicação é exclusivamente didática: não possui banco, rate limiting, gestão real de usuários, auditoria nem outras proteções necessárias em produção.
- O segredo JWT padrão e as contas de demonstração são somente para uso local. Para outro ambiente, configure `JWT_SECRET_KEY` com valor próprio e seguro.
- A data `2099-12-31` serve apenas para manter cupons válidos nos exercícios.
