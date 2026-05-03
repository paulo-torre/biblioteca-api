# Feature: rotas de livros

## Rotas adicionadas no arquivo books.py: 

### @router.post("/saved"):

Salva um livro na lista de livros salvos do usuário. Necessita de um usuário cadastrado e de um book_id.

### @router.delete("/saved/{book_id}"):

Deleta um livro da lista de livros salvos do usuário. OBS: aqui, não há verificação de existência da tupla antes de rodar o DELETE, pois não há problema de rodar um delete sem existir.

### @router.get("/saved"):

Retorna a lista de livros salvos do usuário.

### @router.post("/ratings"):

Adiciona uma avaliação às avaliações do usuário. A avaliação deve estar em VALID_RATINGS. Se o livro adicionado já estiver avaliado, roda um UPDATE ao invés de um INSERT. Necessita de um usuário cadastrado e de um book_id.

### @router.delete("/ratings/{book_id}"):

Deleta uma avaliação das avaliações do usuário. OBS: aqui, não há verificação de existência da tupla antes de rodar o DELETE, pois não há problema de rodar um delete sem existir.

### @router.get("/ratings"):

Retorna a lista de avaliações do usuário.