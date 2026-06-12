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
├── config.py            # definição das configurações gerais do app
├── dependencies.py      # middleware de autenticação JWT
├── models/
│   ├── books.py         # modelos Pydantic de validação da rota /api/books/
│   ├── common.py        # modelos Pydantic comuns em todo o projeto
│   └── user.py          # modelos Pydantic de validação da rota /api/user/
├── routers/
│   ├── auth.py          # rotas de autenticação
│   ├── books.py         # rotas de livros
│   └── user.py          # rotas de usuário
├── services/
|   ├── database.py      # conexão com o Supabase
│   └── email.py         # envio de emails transacionais
└── utils/
    ├── pagination.py         # funções helpers para paginação
    └── verification_code.py  # funções helpers para códigos de verificação
tests/
├── __init__.py
├── conftest.py          # fixtures compartilhados entre testes
├── helpers.py           # funções auxiliares para os testes
├── auth/                # testes para a rota auth
│   └── ...
├── books/               # testes para a rota books
│   └── ...
└── user/                # testes para a rota user
    └── ...
pytest.ini               # configuração do pytest
requirements.txt         # dependências do projeto
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
# Database

DB_URL=...
DB_SERVICE_KEY=...

# JWT
JWT_SECRET_KEY=...

# Resend
EMAIL_SERVICE_API_KEY=...

# Configurations
ENVIRONMENT=development
PYTHON_VERSION=3.12.10
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

| Método | Rota                            | Auth | Descrição                                                   |
|--------|---------------------------------|------|-------------------------------------------------------------|
| POST   | `/api/auth/register`            | ❌    | Cadastro de usuário — envia código de verificação por email |
| POST   | `/api/auth/verify-email`        | ❌    | Valida o código de verificação e ativa a conta              |
| POST   | `/api/auth/resend-verification` | ❌    | Reenvia o código de verificação                             |
| POST   | `/api/auth/forgot-password`     | ❌    | Envia código de confirmação para o email                    |
| PUT    | `/api/auth/reset-password`      | ❌    | Valida o código de confirmação e redefine a senha           |
| POST   | `/api/auth/login`               | ❌    | Login — retorna JWT                                         |

### Usuário (`/api/user`)

| Método | Rota                               | Auth | Descrição                                                   |
|--------|------------------------------------|------|-------------------------------------------------------------|
| GET    | `/api/user/me`                     | ✅    | Retorna os dados do usuário logado                          |
| PUT    | `/api/user/me/username`            | ✅    | Altera o username                                           |
| PUT    | `/api/user/me/email`               | ✅    | Solicita troca de email — envia código para o novo endereço |
| POST   | `/api/user/me/verify-email-change` | ✅    | Confirma a troca de email via código                        |
| PUT    | `/api/user/me/password`            | ✅    | Altera a senha — exige senha atual                          |
| POST   | `/api/user/me/request-delete`      | ✅    | Solicita exclusão da conta — envia código por email         |
| DELETE | `/api/user/me`                     | ✅    | Confirma e executa a exclusão da conta                      |

### Livros (`/api/books`)

| Método | Rota                           | Auth | Descrição                                          |
|--------|--------------------------------|------|----------------------------------------------------|
| GET    | `/api/books/search/{query}`    | ❌   | Busca livros na Open Library                       |
| GET    | `/api/books/saved`             | ✅   | Retorna todos os livros salvos pelo usuário logado |
| POST   | `/api/books/saved/{book_id}`   | ✅   | Salva um livro na lista do usuário logado          |
| DELETE | `/api/books/saved/{book_id}`   | ✅   | Deleta o livro da lista do usuário logado          |
| GET    | `/api/books/opinions`          | ✅   | Retorna as opiniões salvas do usuário logado       |
| POST   | `/api/books/opinions`          | ✅   | Salva uma opinião do usuário logado sobre um livro |
| PUT    | `/api/books/opinions`          | ✅   | Edita a opinião do usuário logado sobre um livro   |
| DELETE | `/api/books/opinions`          | ✅   | Deleta a opinião do usuário logado sobre um livro  |
| GET    | `/api/books/reviews`           | ✅   | Retorna as reviews salvas do usuário logado        |
| GET    | `/api/books/reviews/{book_id}` | ❌   | Retorna todas as reviews salvas em um livro        |
| POST   | `/api/books/reviews`           | ✅   | Salva uma review do usuário logado sobre um livro  |
| PUT    | `/api/books/reviews`           | ✅   | Edita a review do usuário logado sobre um livro    |
| DELETE | `/api/books/reviews/{book_id}` | ✅   | Deleta a review do usuário logado sobre um livro   |
| POST   | `/api/books/history/{book_id}` | ✅   | Adiciona um livro ao histórico de visualização     |
| GET    | `/api/books/history`           | ✅   | Retorna o histórico de visualização do usuário     |

## Paginação

Rotas que retornam listas de itens (ex: livros salvos, opiniões, reviews) suportam paginação via query params: `?page=1&size=10`

## Padrão de Responses

### Status code
- **Sucesso:** status code 200 ou 201, com JSON contendo os dados solicitados ou mensagem de sucesso.
- **Erro de validação:** status code 422, com JSON detalhando os erros de validação.
- **Erro de autenticação:** status code 401.
- **Erro de autorização:** status code 403.
- **Erro de recurso não encontrado:** status code 404.
- **Erro de servidor:** status code 500.
- **Erros específicos de negócio:** (ex: email já cadastrado, código de verificação inválido) status code 400 com mensagens descritivas.

### Rotas paginadas

#### Rota `GET /api/books/saved`
```json
{
  "data": [
    {
      "book_id": "OL8080M",
      "saved-at": "2024-06-01T12:00:00Z",
    },
    ...
  ],
  "page": 1,
  "size": 20,
  "total": 100
}
```

#### Rota `GET /api/books/opinions`
```json
{
  "data": [
    {
      "book_id": "OL8080M",
      "opinion": "Gostei muito desse livro, recomendo!",
      "opined_at": "2024-06-01T12:00:00Z"
    },
    ...
  ],
  "page": 1,
  "size": 20,
  "total": 50
}
```

#### Rota `GET /api/books/reviews/{book_id}`
```json
{
  "data": [
    {
      "book_id": "OL8080M",
      "rating": 5,
      "comment": "Excepcional!",
      "username": "pedrocnog",
      "created_at": "2024-06-01T12:00:00Z"
    },
    ...
  ],
  "summary": {
    "average_rating": 4.21,
    "rating_distribution": {
      "1.0": 2,
      "3.0": 1,
      "4.0": 5,
      "4.5": 3,
      "5.0": 10
    }
  },
  "page": 1,
  "size": 20,
  "total": 30
}
```

#### Rota `GET /api/books/reviews`
```json
{
  "data": [
    {
      "book_id": "OL8080M",
      "rating": 5,
      "comment": "Excepcional!",
      "username": "pedrocnog",
      "created_at": "2024-06-01T12:00:00Z"
    },
    ...
  ],
  "page": 1,
  "size": 20,
  "total": 30
}
```

#### Rota `GET /api/books/history`
```json
{
  "data": [
    {
      "book_id": "OL8080M",
      "viewed_at": "2024-06-01T12:00:00Z"
    },
    ...
  ],
  "page": 1,
  "size": 20,
  "total": 100
}
```

## Autenticação

As rotas protegidas exigem o header:

```
Authorization: Bearer <token>
```

O token é retornado no login e tem validade de 24 horas. Rotas que alteram `email` ou `username` retornam um novo token atualizado na resposta.