#!/bin/sh

echo "Executando as migrações do banco de dados..."
poetry run alembic upgrade head

echo "Iniciando a aplicação em modo produção..."
poetry run fastapi run app/app.py