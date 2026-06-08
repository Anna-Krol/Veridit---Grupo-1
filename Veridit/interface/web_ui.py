# interface/web_ui.py
from fastapi import FastAPI, Form, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware # Importe isto!
from business.models.billing_models import PACOTES_DISPONIVEIS
from infrastructure.repository import UsuarioRepository
from business.user_service import UserService
import os
import sqlite3
import yagmail


# Imports das suas camadas internas de negócio
from persistence.repositories_db import RepositoriesDB
from business.identity_auth_manager import IdentityAuthManager
from interface.database import salvar_usuario, inicializar_db, criar_token_recuperacao, atualizar_senha_por_token, validar_login, buscar_usuario_por_email, registrar_compra_db

app = FastAPI(title="Veridit Platform")
app.add_middleware(SessionMiddleware, secret_key="uma-chave-muito-secreta-e-longa-para-o-projeto-veridit")

# 1. CONFIGURAÇÃO INTELIGENTE DE CAMINHOS (Garante o carregamento do CSS)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Aponta para a pasta 'interface'
ROOT_DIR = os.path.dirname(CURRENT_DIR)                  # Aponta para a raiz 'Veridit'

# Verifica automaticamente se as pastas estão na raiz ou dentro da pasta interface
if os.path.exists(os.path.join(ROOT_DIR, "static")):
    STATIC_PATH = os.path.join(ROOT_DIR, "static")
    TEMPLATES_PATH = os.path.join(ROOT_DIR, "templates")
else:
    STATIC_PATH = os.path.join(CURRENT_DIR, "static")
    TEMPLATES_PATH = os.path.join(CURRENT_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
templates = Jinja2Templates(directory=TEMPLATES_PATH)

# Inicialização das instâncias de negócio do backend
db = RepositoriesDB()
auth_manager = IdentityAuthManager(repositories_db=db)

# Estado de sessão simulado
sessao_atual = {"id": None, "email_usuario": "eduardo.almeida@ufba.br"}
def get_user_service():
    repo = UsuarioRepository()
    return UserService(repo)

# -------------------------------------------------------------------------
# ROTAS DO FRONT-END (GET) - RENDERIZAM OS ARQUIVOS HTML EXTERNOS
# -------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    inicializar_db()

# 1. TELA DE LOGIN (Agora é a primeira página ao entrar no app)
@app.get("/")
async def tela_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",  # Seu arquivo HTML da tela de login
        context={"request": request, "rota_ativa": "login", "user_logado": auth_manager.sessao_ativa}
    )

# 2. TELA DE CADASTRO (A tela com "Usuário Comum" e "Advogado")
@app.get("/cadastro")
async def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",   # Mantém o seu HTML de cadastro atual aqui
        context={"request": request, "rota_ativa": "cadastro", "user_logado": auth_manager.sessao_ativa}
    )

@app.get("/recuperar")
async def pagina_recuperar(request: Request):
    # Processa o template manualmente através do motor Jinja2 do objeto templates
    # Isto ignora o 'TemplateResponse' do FastAPI que está a dar erro
    content = templates.env.get_template("recuperar.html").render(
        request=request, 
        rota_ativa="recuperar"
    )
    return HTMLResponse(content=content)

@app.get("/mudar-senha")
async def pagina_mudar_senha(token: str, request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="nova_senha.html", 
        context={"token": token}
    )

@app.get("/dashboard")
async def exibir_dashboard(
    request: Request,
    user_service: UserService = Depends(get_user_service) # A injeção de dependência entra aqui!
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
    
    # Veja como fica limpo: pedimos os dados (já com os créditos) direto ao serviço!
    dados_usuario = user_service.obter_dados_usuario(usuario_email)
    
    if not dados_usuario:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"usuario": dados_usuario, "registros": []}
    )

@app.get("/sair")
async def sair_do_sistema(request: Request):
    # Remove o usuário logado da sessão (destrói o cookie)
    request.session.pop("usuario_logado", None)
    
    # Redireciona o usuário de volta para a tela de login (/)
    return RedirectResponse(url="/", status_code=303)

# -------------------------------------------------------------------------
# PROCESSADORES LÓGICOS (POST) - COMUNICAM COM O BACKEND E REDIRECIONAM
# -------------------------------------------------------------------------

@app.post("/cadastrar")
async def rota_cadastrar(
    nome_completo: str = Form(...),
    email: str = Form(...),
    cpf: str = Form(...),
    senha: str = Form(...),
    tipo: str = Form(...),
    numero_oab: str = Form(None) # OAB pode ser opcional/vazia
):
    # 1. Busca se o email ou cpf já existem no banco
    # (Substitua pelo nome da sua função real de busca se for diferente)
    usuario_existente = buscar_usuario_por_email(email) 
    
    # O CORRETO É: Se encontrar ALGO (se não for None), aí sim dá o erro
    if usuario_existente is not None:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado no sistema!")

    # 2. Se passou pelo IF acima (ou seja, é None/Não existe), aí sim realiza o cadastro
    salvar_usuario(nome_completo, email, cpf, senha, tipo)
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/logar")
async def processar_login(
    request: Request, 
    email: str = Form(...), 
    senha: str = Form(...),
    user_service: UserService = Depends(get_user_service) # A mágica da Inversão de Dependência acontece aqui!
):
    # O Controller pergunta ao Serviço se pode logar
    if user_service.autenticar_usuario(email, senha):
        request.session["usuario_logado"] = email
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse(request=request, name="login.html", context={"erro": "Email ou senha incorretos."})

@app.post("/recuperar")
async def processar_recuperacao(email: str = Form(...)):
    # Adicione este print para ver exatamente o que veio do formulário HTML
    print(f"DEBUG FORMULÁRIO: Recebido e-mail para recuperação: '{email}'")
    
    token = criar_token_recuperacao(email)
    
    if token is None:
        # Se for None, o e-mail não existe no banco de dados
        raise HTTPException(status_code=404, detail="E-mail não encontrado no sistema")
        
    # Se o token foi gerado, continua o processo de envio
    link = f"http://localhost:8000/mudar-senha?token={token}"
    print(f"LINK DE RECUPERAÇÃO GERADO: {link}") # Copie este link do terminal se o e-mail falhar
    
    # ... código de envio do yagmail ...
    return {"status": "sucesso", "mensagem": "Link de recuperação gerado."}

@app.post("/confirmar-mudanca")
async def confirmar_mudanca(token: str = Form(...), nova_senha: str = Form(...)):
    sucesso = atualizar_senha_por_token(token, nova_senha)
    
    if sucesso:
        # Redireciona para o login com uma mensagem de sucesso (ou uma página de confirmação)
        return RedirectResponse(url="/?mensagem=senha_alterada", status_code=303)
    else:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

@app.post("/logout")
async def rota_logout():
    await auth_manager.sair_sistema()
    return RedirectResponse(url="/", status_code=303)


# 2. Rota para exibir o formulário após escolher o plano
@app.get("/faturamento")
async def tela_faturamento(request: Request, pacote: str):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # Busca os dados reais do usuário
    dados_banco = buscar_usuario_por_email(usuario_email)
    dados_usuario = {
        "nome": dados_banco["nome"],
        "creditos": 0
    }

    return templates.TemplateResponse(
        request=request,
        name="faturamento.html",
        context={
            "pacote_escolhido": pacote,
            "usuario": dados_usuario # Enviamos a variável para a tela
        }
    )

@app.post("/processar-compra")
async def processar_compra(
    request: Request,
    pacote_selecionado: str = Form(...),
    nome_faturamento: str = Form(...),
    cpf_faturamento: str = Form(...),
    telefone: str = Form(...),
    cep: str = Form(...),
    endereco: str = Form(...),
    numero: str = Form(...),
    complemento: str = Form(None),
    bairro: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...)
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        raise HTTPException(status_code=401, detail="Não autorizado")

    pacote = PACOTES_DISPONIVEIS.get(pacote_selecionado)
    if not pacote:
        raise HTTPException(status_code=400, detail="Pacote inválido")

    valor_total = pacote.quantidade_creditos * pacote.valor_por_credito

    # Monta o dicionário para persistência
    dados_compra = {
        "email_usuario": usuario_email,
        "pacote": pacote.nome,
        "qtd": pacote.quantidade_creditos,
        "valor": valor_total,
        "nome": nome_faturamento,
        "cpf": cpf_faturamento,
        "cep": cep,
        "endereco": f"{endereco}, {numero} - {complemento or ''} - {bairro}",
        "cidade": cidade,
        "estado": estado
    }
    
    # Salva no banco de dados
    registrar_compra_db(dados_compra)
    
    # Redireciona para o próximo passo (REQ 06 - Pagamento)
    return RedirectResponse(url=f"/pagamento?pacote={pacote_selecionado}", status_code=303)


@app.get("/pagamento")
async def tela_pagamento(request: Request, pacote: str = "basico"):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # Busca os dados reais do usuário para a barra lateral
    dados_banco = buscar_usuario_por_email(usuario_email)
    dados_usuario = {
        "nome": dados_banco["nome"] if dados_banco else "Usuário",
        "creditos": 0
    }

    # Calcula o valor total com base no pacote selecionado
    pacote_obj = PACOTES_DISPONIVEIS.get(pacote)
    valor = (pacote_obj.quantidade_creditos * pacote_obj.valor_por_credito) if pacote_obj else 0.0

    return templates.TemplateResponse(
        request=request,
        name="pagamento.html",
        context={
            "usuario": dados_usuario,
            "pacote_escolhido": pacote,
            "valor_total": valor
        }
    )

# Rota para simular o pagamento e creditar na conta
@app.post("/simular-pagamento")
async def simular_pagamento(
    request: Request, 
    pacote_selecionado: str = Form(...),
    user_service: UserService = Depends(get_user_service) # Injeção de Dependência
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # O Controller delega a regra de negócio para o Serviço
    user_service.processar_pagamento_aprovado(usuario_email, pacote_selecionado, PACOTES_DISPONIVEIS)
    
    return RedirectResponse(url="/dashboard", status_code=303)

# 1. Rota de Planos

@app.get("/comprar-creditos")
async def tela_comprar_creditos(
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # Pega os dados reais e atualizados do banco
    dados_usuario = user_service.obter_dados_usuario(usuario_email)

   
    return templates.TemplateResponse(
        request=request,
        name="planos.html",
        # O SEGREDO ESTÁ AQUI: Enviando os dados para o HTML
        context={"usuario": dados_usuario} 
    )

# 2. Rota de Faturamento
@app.get("/faturamento")
async def tela_faturamento(
    request: Request, 
    pacote: str,
    user_service: UserService = Depends(get_user_service) # Adicionamos o serviço aqui
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # Pega os dados reais e atualizados do banco
    dados_usuario = user_service.obter_dados_usuario(usuario_email)

    return templates.TemplateResponse(
        request=request,
        name="faturamento.html",
        context={"pacote_escolhido": pacote, "usuario": dados_usuario}
    )

# 3. Rota de Pagamento
@app.get("/pagamento")
async def tela_pagamento(
    request: Request, 
    pacote: str = "basico",
    user_service: UserService = Depends(get_user_service) # Adicionamos o serviço aqui
):
    usuario_email = request.session.get("usuario_logado")
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
        
    # Pega os dados reais e atualizados do banco
    dados_usuario = user_service.obter_dados_usuario(usuario_email)

    pacote_obj = PACOTES_DISPONIVEIS.get(pacote)
    valor = (pacote_obj.quantidade_creditos * pacote_obj.valor_por_credito) if pacote_obj else 0.0

    return templates.TemplateResponse(
        request=request,
        name="pagamento.html",
        context={"usuario": dados_usuario, "pacote_escolhido": pacote, "valor_total": valor}
    )