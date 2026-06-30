#!/bin/bash

echo "🚀 Iniciando o Veridit..."

# Verifica se o ambiente virtual existe. Se não existir, ele cria usando python3.
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativa o ambiente virtual
echo "🔄 Ativando ambiente..."
source .venv/bin/activate

# Instala/Atualiza as dependências silenciosamente usando o pip de dentro do ambiente
echo "📚 Checando dependências..."
pip install fastapi uvicorn jinja2 yagmail itsdangerous python-multipart opencv-python numpy mss plyer --quiet

# Roda o servidor usando o python do ambiente virtual
echo "✅ Servidor rodando! Acesse: http://localhost:8000"
python3 -m uvicorn interface.web_ui:app --reload
