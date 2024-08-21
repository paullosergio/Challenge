# Challenge

Uma aplicação de gerenciamento de tarefas (To-dos) construída com FastAPI e SQLAlchemy. A aplicação permite a autenticação de usuários, criação, leitura, atualização e exclusão de tarefas, além de suporte a logs e monitoramento.

## Sumário

- [Recursos](#recursos)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Como Executar](#como-executar)
- [Como Testar](#como-testar)
- [Estrutura do Projeto](#estrutura-do-projeto)


## Recursos

- Autenticação de usuário com tokens JWT.
- Criação, leitura, atualização e exclusão de usuários.
- Criação, leitura, atualização e exclusão de tarefas.
- Suporte a filtragem e paginação de tarefas.
- Logs para monitoramento e depuração.

## Pré-requisitos

É neccessário:

- Docker
- Docker Compose
- Python 3.12
- Poetry (opcional, se você não usar o Docker)

## Configuração do Ambiente

### Clone o repositório:

```bash
git clone https://github.com/paullosergio/Challenge
cd Challenge
```

## Como Executar

### Usando Docker


**Construir e iniciar os containers:**

```bash
docker-compose up --build
```

Isso iniciará os serviços definidos no docker-compose.yml, incluindo o banco de dados PostgreSQL e a aplicação FastAPI.

### Usando o Poetry

```bash
task run
```

- Localização da API: http://localhost:9999
- Interface do Swagger: http://localhost:9999/docs
- Interface do ReDoc: http://localhost:9999/redoc

## Como Testar

Para garantir que a aplicação está funcionando corretamente, você pode executar os testes automatizados. Siga os passos abaixo para testar o projeto:

  ```bash
  task test
  ```

## Estrutura do Projeto

- **`app/`**: Contém o código fonte da aplicação.
  - **`models.py`**: Definições dos modelos SQLAlchemy.
  - **`schemas.py`**: Definições dos schemas Pydantic.
  - **`security.py`**: Funções de segurança e autenticação.
  - **`app.py`**: Ponto de entrada da aplicação FastAPI.
  - **`logging_config.py`**: Configuração de logging.
  - **`database.py`**: Configuração do banco de dados e gerenciador de sessão.
  - `routers/`: Contém os routers da aplicação.
    - `users.py`: Roteador para operações relacionadas a usuários.
    - `todo.py`: Roteador para operações relacionadas a tarefas.
    - `auth.py`: Roteador para operações de autenticação.
- `tests/`: Contém os testes da aplicação.
  - `test_users.py`: Testes para operações relacionadas a usuários.
  - `test_todos.py`: Testes para operações relacionadas a tarefas.
  - `test_auth.py`: Testes para operações de autenticação.
  - `test_security.py`: Testes para funções de segurança e autenticação.
  - `conftest.py`: Configurações e fixtures para os testes.
- `poetry.lock`: Arquivo de bloqueio de dependências gerado pelo Poetry.
- `pyproject.toml`: Arquivo de configuração do Poetry, que inclui dependências e configurações do projeto.
- **`docker-compose.yml`**: Configuração dos serviços Docker.

- **`Dockerfile`**: Imagem Docker para a aplicação FastAPI.

- **`entrypoint.sh`**: Script de inicialização do container.

- **`nginx.conf`**: Configuração do Nginx.

