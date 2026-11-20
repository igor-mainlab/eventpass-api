
# EventPass API

API RESTful desenvolvida para o domínio de Gestão de Eventos,
como parte da disciplina Computação em Nuvem e Arquitetura
Orientada a Serviços (SOA), do curso de Ciência da Computação
do IFPA — Campus Ananindeua.

## 1. Objetivo

A EventPass API permite consultar eventos disponíveis,
emitir ingressos virtuais, realizar check-in na portaria
e consultar informações de ingressos emitidos.

O projeto utiliza Python, FastAPI, Pydantic e SQLite,
seguindo uma arquitetura em camadas.

## 2. Funcionalidades

- Listagem de eventos com vagas disponíveis.
- Emissão de ingressos com identificador único.
- Geração de hash SHA-256 para validação.
- Controle automático de vagas.
- Check-in com bloqueio de reutilização.
- Consulta de ingressos pelo identificador.
- Tratamento padronizado de erros HTTP.
- Documentação interativa com Swagger UI.

## 3. Tecnologias utilizadas

- Python 3.10
- FastAPI
- Pydantic
- Uvicorn
- SQLite
- Pytest
- HTTPX

## 4. Estrutura do projeto

```text
projeto_eventos/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── services.py
│   └── database.py
├── tests/
│   ├── conftest.py
│   ├── test_eventos.py
│   ├── test_ingressos.py
│   └── test_checkin.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 5. Endpoints RESTful

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/v1/eventos | Listar eventos disponíveis |
| POST | /api/v1/ingressos | Emitir ingresso |
| POST | /api/v1/checkin | Validar entrada |
| GET | /api/v1/ingressos/{id_ingresso} | Consultar ingresso |

## 6. Instalação e execução

### 6.1. Criar o ambiente virtual

```powershell
python -m venv .venv
```

### 6.2. Ativar o ambiente virtual (Windows)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 6.3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 6.4. Inicializar o banco de dados

```powershell
python -c "from app.database import inicializar_banco; inicializar_banco()"
```

### 6.5. Cadastrar eventos de exemplo

```powershell
python -c "from app.services import cadastrar_eventos_iniciais; cadastrar_eventos_iniciais()"
```

### 6.6. Executar a API

```powershell
python -m uvicorn app.main:app --reload
```

A API estará disponível em:

http://127.0.0.1:8000

Documentação Swagger UI:

http://127.0.0.1:8000/docs

## 7. Testes automatizados

Para executar todos os testes:

```powershell
python -m pytest -v
```

Os testes utilizam um banco SQLite temporário e verificam:

- Listagem de eventos.
- Emissão de ingressos.
- Tratamento de eventos inexistentes.
- Validação de e-mails.
- Indisponibilidade de vagas.
- Check-in e bloqueio de reutilização.
- Rejeição de hashes inexistentes.
- Rejeição de ingressos cancelados.

## 8. Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | Requisição realizada com sucesso |
| 201 | Recurso criado |
| 400 | Regra de negócio inválida |
| 404 | Recurso não encontrado |
| 409 | Conflito de estado do ingresso |
| 422 | Dados inválidos |
| 500 | Erro interno do servidor |

## 9. Arquitetura

A aplicação está organizada em camadas:

- main.py: rotas HTTP e tratamento de exceções.
- schemas.py: DTOs de entrada e saída.
- services.py: regras de negócio.
- database.py: persistência SQLite.

Essa separação facilita a manutenção, os testes
e a evolução da aplicação.

## 10. Contexto acadêmico

Instituição: Instituto Federal do Pará (IFPA)
Campus: Ananindeua
Curso: Bacharelado em Ciência da Computação
Disciplina: Computação em Nuvem e Arquitetura Orientada
a Serviços (SOA)
Professor: M.Sc. Fábio Ferreira

Projeto: Build Your Own API
Domínio 5: Gestão de Eventos
Marco 1: Core RESTful, DTOs e Swagger UI