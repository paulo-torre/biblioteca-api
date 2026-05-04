# Contexto do Back-end - Biblioteca Virtual

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | React.js + TypeScript |
| Back-end | Python + FastAPI + Uvicorn |
| Banco de dados | Supabase (PostgreSQL) |
| Hospedagem back-end | Render |
| API externa | Open Library |

## Estrutura do Back-end

```
back-end/
├── app/
│   ├── __init__.py
│   ├── main.py           # inicializa o app e registra os routers
│   ├── database.py       # conexão com o Supabase via service_role key
│   ├── dependencies.py   # get_current_user (autenticação JWT)
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py       # RegisterRequest, LoginRequest, UserResponse (Pydantic)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py       # /api/auth/register, /api/auth/login
│       └── books.py      # /api/books/search
├── .env
├── .gitignore
└── requirements.txt      # Rodar "pip freeze -r requirements.txt" para instalar todas as dependências
```

## Variáveis de Ambiente (`.env`)

```
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SECRET_KEY=...            # usado para assinar os JWTs
```

Essas variáveis também estarão cadastradas no painel do Render em **Environment**.

## Banco de Dados — Tabelas

Todas as tabelas têm **Row Level Security (RLS) ativado** e sem policies,
bloqueando acesso direto via API pública. O back-end acessa via `service_role`,
que bypassa o RLS por design.

### `users`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK, gerado automaticamente |
| email | TEXT | UNIQUE, NOT NULL |
| username | TEXT | UNIQUE, NOT NULL |
| password | TEXT | hash bcrypt |
| embedding | vector(384) | modelo all-MiniLM-L6-v2, NULL por enquanto |
| created_at | TIMESTAMPTZ | gerado automaticamente |

### `saved_books`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK -> users(id) ON DELETE CASCADE |
| book_id | TEXT | ID da Open Library (ex: "OL27516W") |
| saved_at | TIMESTAMPTZ | gerado automaticamente |

Restrição: `UNIQUE (user_id, book_id)`

### `book_ratings`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| book_id | TEXT | |
| rating | TEXT | CHECK: 'loved', 'liked', 'disliked' |
| rated_at | TIMESTAMPTZ | |

Restrição: `UNIQUE (user_id, book_id)`

### `book_reviews`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| book_id | TEXT | |
| rating | NUMERIC(2,1) | 0 a 5, múltiplos de 0.5 |
| comment | TEXT | opcional (nullable) |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | atualizado automaticamente via trigger |

Restrição: `UNIQUE (user_id, book_id)`

> Há um trigger `set_updated_at` associado à função `update_updated_at()`
> que atualiza `updated_at` automaticamente a cada UPDATE. A função é reutilizável
> para outras tabelas no futuro.

### `reading_history`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| book_id | TEXT | |
| viewed_at | TIMESTAMPTZ | |

> Não há limite de registros por usuário — sempre buscar os 20 mais recentes
> com `ORDER BY viewed_at DESC LIMIT 20`. O histórico completo será fundamental para a IA.

### `search_history`
| Campo | Tipo | Detalhe |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| query | TEXT | |
| searched_at | TIMESTAMPTZ | |

## Autenticação

- **Método:** JWT (JSON Web Token) assinado com HS256
- **Biblioteca:** `python-jose`
- **Hash de senha:** `bcrypt`
- **Expiração do token:** 24 horas
- **Payload do JWT:** `sub` (user_id), `email`, `username`, `exp`
- **Header esperado nas rotas protegidas:** `Authorization: Bearer <token>`

O middleware `get_current_user` em `dependencies.py` verifica e decodifica o token.
Uso em qualquer rota protegida:

```python
from app.dependencies import get_current_user
from fastapi import Depends

@router.get("/rota")
async def rota(current_user = Depends(get_current_user)):
    user_id = current_user["id"]
    ...
```

## Endpoints Implementados

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | /api/books/search?query= | ❌ | Busca livros na Open Library |
| POST | /api/auth/register | ❌ | Cadastro de usuário |
| POST | /api/auth/login | ❌ | Login, retorna JWT |

## Validações de Senha (Pydantic + `field_validator`)

- De 8 a 20 caracteres
- Ao menos uma letra
- Ao menos um número
- Ao menos um caractere especial: `@!#$%^&*()/\`
- Apenas caracteres permitidos (letras, números e os especiais acima)

## Plano de IA (Futuro)

- Motor de embeddings: `all-MiniLM-L6-v2` (384 dimensões)
- Cada livro terá um vetor gerado a partir de seus metadados
- Cada usuário terá um vetor (`embedding` na tabela `users`) que representa seu gosto
- Recomendação por similaridade de cosseno entre o vetor do usuário e os vetores dos livros
- Armazenamento e consulta vetorial via extensão `pgvector` do Supabase

## Próximos Passos Sugeridos

**Programador 1 — núcleo de usuário:**
- `GET  /api/user/me` — retorna dados do usuário logado
- `PUT  /api/user/me` — editar perfil
- `PUT  /api/user/me/password` — trocar senha
- `DEL  /api/user/me` — deletar conta

**Programador 2 — funcionalidades de livros:**
- `POST/DELETE/GET /api/books/saved` — gerenciar lista salva
- `POST/DELETE/GET /api/books/ratings` — gerenciar avaliações
- `POST/PUT/GET    /api/books/reviews` — gerenciar reviews
- `POST/GET        /api/books/history` — registrar e buscar histórico
