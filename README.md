# Biblioteca Virtual — Back-end

API REST desenvolvida com FastAPI para uma aplicação de biblioteca virtual com sistema de recomendação de livros por IA.

## Stack

- **Python** + **FastAPI** + **Uvicorn**
- **Supabase** (PostgreSQL) como banco de dados
- **python-jose** para geração e verificação de JWT
- **bcrypt** para hash de senhas
- **Resend** para envio de emails transacionais

## Estrutura do projeto

```
app/
├── main.py              # inicialização do app e registro de routers
├── database.py          # conexão com o Supabase
├── dependencies.py      # middleware de autenticação JWT
├── utils.py             # funções utilitárias (geração de código de verificação)
├── models/
│   └── user.py          # modelos Pydantic de validação
├── routers/
│   ├── auth.py          # rotas de autenticação
│   ├── books.py         # rotas de livros
│   └── user.py          # rotas de usuário
└── services/
    └── email.py         # envio de emails transacionais
tests/
├── __init__.py
└── test_auth_n_user.py  # testes de integração
conftest.py              # fixtures compartilhados entre testes
pytest.ini               # configuração do pytest
```

## Instalação

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SECRET_KEY=...
RESEND_API_KEY=...
ENVIRONMENT=development
```

## Rodando o servidor

```bash
uvicorn app.main:app --reload
```

## Rodando os testes

```bash
pytest tests/ -v
```

## Endpoints

### Autenticação (`/api/auth`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/api/auth/register` | ❌ | Cadastro de usuário — envia código de verificação por email |
| POST | `/api/auth/verify-email` | ❌ | Valida o código de verificação e ativa a conta |
| POST | `/api/auth/resend-verification` | ❌ | Reenvia o código de verificação |
| POST | `/api/auth/login` | ❌ | Login — retorna JWT |

### Usuário (`/api/user`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/api/user/me` | ✅ | Retorna os dados do usuário logado |
| PUT | `/api/user/me/username` | ✅ | Altera o username |
| PUT | `/api/user/me/email` | ✅ | Solicita troca de email — envia código para o novo endereço |
| POST | `/api/user/me/verify-email-change` | ✅ | Confirma a troca de email via código |
| PUT | `/api/user/me/password` | ✅ | Altera a senha — exige senha atual |
| POST | `/api/user/me/request-delete` | ✅ | Solicita exclusão da conta — envia código por email |
| DELETE | `/api/user/me` | ✅ | Confirma e executa a exclusão da conta |

### Livros (`/api/books`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/api/books/search` | ❌ | Busca livros na Open Library |

## Autenticação

As rotas protegidas exigem o header:

```
Authorization: Bearer <token>
```

O token é retornado no login e tem validade de 24 horas. Rotas que alteram `email` ou `username` retornam um novo token atualizado na resposta.