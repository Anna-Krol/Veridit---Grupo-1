#!/bin/bash

echo "🚀 Iniciando o Veridit..."

# Verifica se o ambiente virtual existe. Se não existir, ele cria.
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python -m venv .venv
fi

# Ativa o ambiente virtual
echo "🔄 Ativando ambiente..."
source .venv/Scripts/activate || source .venv/bin/activate

# Instala/Atualiza as dependências silenciosamente
echo "📚 Checando dependências..."
pip install fastapi uvicorn jinja2 yagmail --quiet

# Roda o servidor
echo "✅ Servidor rodando! Acesse: http://localhost:8000"
uvicorn interface.web_ui:app --reload