# 🛡️ Veridit Platform

O **Veridit** é uma plataforma moderna e segura para captura, registro e validação de evidências digitais. O sistema permite que usuários comuns e advogados gerenciem seus registros através de um painel intuitivo, com um sistema integrado de compra de créditos.

## ✨ Funcionalidades (MVP)

- **🔐 Autenticação Segura:** Cadastro e login diferenciado para Usuários Comuns e Advogados (validação OAB).
- **📊 Dashboard Interativo:** Painel de controle com resumo de créditos, registros do mês e atalhos rápidos.
- **💳 Sistema de Créditos e Faturamento:** Fluxo completo de compra de pacotes de créditos (Básico, Médio e Premium), com simulação de checkout e geração de código PIX (Copia e Cola/QR Code).
- **🔒 Arquitetura Robusta:** Sistema refatorado aplicando princípios **SOLID** (Responsabilidade Única e Inversão de Dependência), garantindo um código limpo, testável e escalável.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2 Templates
- **Banco de Dados:** SQLite (com abstração via Repository Pattern para fácil migração)
- **Design Pattern:** Injeção de Dependências (DI), MVC Adaptado (Router -> Service -> Repository)

## 📂 Estrutura do Projeto

```text
Veridit/
├── business/               # Regras de negócio e Serviços (UserService, Billing, etc.)
├── infrastructure/         # Comunicação com o banco de dados (Repository)
├── interface/              # Camada de apresentação
│   ├── templates/          # Arquivos HTML (Dashboard, Login, Faturamento)
│   ├── static/             # Arquivos CSS, JS e Imagens
│   └── web_ui.py           # Rotas principais da aplicação web (FastAPI)
├── persistence/            # Modelagem de dados
├── usuarios.db             # Banco de dados local (ignorado no git)
└── README.md
```

## ⚙️ Pré-requisitos e Instalação

Para rodar o projeto localmente, você precisará apenas do **Python 3.8+** e do **Git** instalados na sua máquina.

### ⚙️ Como Executar o Projeto Localmente

**1. Clone este repositório** para o seu computador e acesse a pasta do projeto:
```bash
git clone [https://github.com/Anna-Krol/Veridit---Grupo-1.git](https://github.com/Anna-Krol/Veridit---Grupo-1.git)
cd Veridit---Grupo-1
```
Execute no teminal o comando:
```
bash run.sh
```
Acesse a plataforma:
```
http://localhost:8000
