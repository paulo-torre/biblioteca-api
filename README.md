# Feature: cadastro de usuário no banco de dados

## Reorganização do projeto:

Antes, as funcionalidades estavam todas no arquivo `main.py`, o que deixava o projeto ilegível e de difícil manutenção. Agora cada feature está (e vai ser) separada em diferentes arquivos, que serão organizados em módulos.

### Organização:

* **`app/` (Módulo-pai):** onde está todos os sub-módulos (`models/` e `routers/`) e arquivos python (`database.py`, `dependencies.py` e `main.py`).

* **`database.py`:** conecta com o banco de dados
* **`dependencies.py`:** contém features que são usadas em várias partes do projeto
* **`main.py`:** inicializa a API e as rotas cadastradas em `routers/`


* **`models/`:** onde estará todas as classes
* **`routers/`:** onde estará todas as rotas, incluindo suas delarações e funcionamentos

## Cadastro de usuário:

O cadastro é feito ao chamar a rota _/auth/register_, passando o _username_, _email_ e _password_. O campos de _username_ e _email_ são buscados no banco de dados, para garantir que não haja usuários duplicados. Caso esteja tudo ok, o campo _password_ é criptografado e salvo, junto aos outros campos, no banco de dados.