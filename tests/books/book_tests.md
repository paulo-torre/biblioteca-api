# Criação dos testes das rotas Books
## Padrões obrigatórios a seguir:

- Cada teste cria e limpa seu próprio estado — sem depender de outros testes
- Limpeza feita via fixture com yield, garantindo cleanup mesmo em caso de falha
- Funções auxiliares reutilizáveis vão em tests/helpers.py
- Fixtures de escopo de módulo quando o mesmo usuário/estado é compartilhado entre vários testes do mesmo arquivo
- Usar client.request("DELETE", ...) para requisições DELETE com body
- Importar supabase de app.database para consultas diretas ao banco quando necessário
- Importar helpers de tests.helpers

## Contexto do projeto:

Todo o contexto está no arquivo `README.md`

## Rotas a testar:
### Search (/api/books/search)
- GET /api/books/search/{query} — busca um livro na API da Open Library (não requer auth, body: {query})

### Saved (/api/books/saved):

- POST /api/books/saved — salvar livro (requer auth, body: {book_id})
- DELETE /api/books/saved/{book_id} — remover da lista (requer auth)
- GET /api/books/saved — listar livros salvos (requer auth)

### Opinions (/api/books/opinions):

- POST /api/books/opinions — avaliar livro (requer auth, body: {book_id, opinion}, valores válidos: liked, loved, disliked)
- PUT /api/books/opinions — editar avaliação do livro (requer auth, body: {book_id, opinion}, mesmos valores válido)
- DELETE /api/books/opinions/{book_id} — remover avaliação (requer auth)
- GET /api/books/opinions — listar avaliações do usuário (requer auth)

### Reviews (/api/books/reviews):

- GET /api/books/reviews/{book_id} — buscar reviews de um livro (não requer auth)
- GET /api/books/reviews — buscar reviews salvas de um usuário (requer auth)
- POST /api/books/reviews — criar review (requer auth, body: {book_id, rating, comment}, rating de 0 a 5 em múltiplos de 0.5, comment opcional, mas até 499 caracteres)
- PUT /api/books/reviews — editar review, seguindo as mesmas regras anteriores (requer auth)
- DELETE /api/books/reviews/{book_id} — deleta a review de um usuário sobre um livro (requer auth)

## Para cada rota, cubra:

- Caso de sucesso
- Ausência de autenticação (quando aplicável) → 401
- Dados inválidos → 422
- Duplicatas quando aplicável → 409
- Recurso não encontrado quando aplicável → 404

## Estrutura de arquivos a criar:
```
tests/
└── books/
    ├── __init__.py
    ├── test_saved.py
    ├── test_opinions.py
    ├── test_search.py
    └── test_reviews.py
```
Se precisar de novas funções auxiliares (ex: save_book(client, token, book_id), create_review(client, token, book_id, rating, comment)), adicione-as em tests/helpers.py seguindo o mesmo estilo das funções já existentes.