# interface/web_ui.py
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware # Importe isto!
import os
import sqlite3
import yagmail


# Imports das suas camadas internas de negócio
from persistence.repositories_db import RepositoriesDB
from business.identity_auth_manager import IdentityAuthManager
from interface.database import salvar_usuario, inicializar_db, criar_token_recuperacao, atualizar_senha_por_token, validar_login, buscar_usuario_por_email

# Import para captura
import webbrowser
import uuid
import time
from business.capture_orchestrator import CaptureOrchestrator
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse

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

# Motor de captura
motor_captura = CaptureOrchestrator()

# Estado de sessão simulado
sessao_atual = {"id": None, "email_usuario": "eduardo.almeida@ufba.br"}

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
async def exibir_dashboard(request: Request):
    usuario_email = request.session.get("usuario_logado")
    
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
    
    # Busca os dados REAIS do usuário no SQLite
    dados_banco = buscar_usuario_por_email(usuario_email)
    
    if not dados_banco:
        # Segurança: se o email sumiu do banco por algum motivo, desloga
        return RedirectResponse(url="/", status_code=303)
        
    registros_reais = motor_captura.obter_todos_os_registros()
    
    dados_usuario = {
        "nome": dados_banco["nome"],
        "email": usuario_email,
        "creditos": 45, 
        "total_registros": len(registros_reais), 
        "este_mes": len(registros_reais)
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"usuario": dados_usuario, "registros": registros_reais}
    )

@app.get("/nova-captura")
async def exibir_nova_captura(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="nova_captura.html",
        context={"request": request}
    )

@app.get("/sucessocap")
async def tela_sucessocap(request: Request, id: str):
    return templates.TemplateResponse(
        request=request,
        name="sucessocap.html",
        context={"request": request, "id_captura": id}
    )

@app.get("/registros")
async def exibir_todos_os_registros(request: Request):
    usuario_email = request.session.get("usuario_logado")
    
    if not usuario_email:
        return RedirectResponse(url="/", status_code=303)
    
    dados_banco = buscar_usuario_por_email(usuario_email)
    
    if not dados_banco:
        return RedirectResponse(url="/", status_code=303)
        
    # Puxa o histórico real do seu motor
    registros_reais = motor_captura.obter_todos_os_registros()
    
    dados_usuario = {
        "nome": dados_banco["nome"],
        "email": usuario_email,
        "creditos": 45,
        "total_registros": len(registros_reais),
        "este_mes": len(registros_reais)
    }

    return templates.TemplateResponse(
        request=request,
        name="registros.html", # Renderiza a nova tela que criaremos abaixo
        context={"usuario": dados_usuario, "registros": registros_reais}
    )

@app.get("/api/download/{captura_id}")
async def api_download_arquivo(captura_id: str):
    """
    Busca o arquivo gerado na pasta raiz e força o download no navegador.
    """
    # Primeiro tentamos procurar o ZIP (se foi gerado por vídeo)
    nome_zip = f"{captura_id}.zip"
    if os.path.exists(nome_zip):
        print(f"📦 Entregando artefato ZIP para download: {nome_zip}")
        return FileResponse(path=nome_zip, filename=nome_zip, media_type="application/zip")
        
    # Se não houver ZIP, tentamos procurar o PNG (se foi gerado por foto)
    nome_png = f"{captura_id}.png"
    if os.path.exists(nome_png):
        print(f"📸 Entregando artefato PNG para download: {nome_png}")
        return FileResponse(path=nome_png, filename=nome_png, media_type="image/png")
        
    # Se nenhum arquivo físico existir na máquina
    raise HTTPException(status_code=404, detail="O arquivo desta evidência ainda está sendo processado ou não foi encontrado.")

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

@app.post("/login")
async def rota_login(request: Request, email: str = Form(...), senha: str = Form(...)):
    # Limpa espaços em branco e força letras minúsculas no e-mail recebido
    email_limpo = email.strip().lower()
    senha_limpa = senha.strip()
    
    print(f"DEBUG LOGIN: Tentando logar com email='{email_limpo}'")
    
    # Passamos os dados já limpos para a função de validação
    if validar_login(email_limpo, senha_limpa):
        # Salva o e-mail padronizado (minúsculo) na sessão para buscar no dashboard depois
        request.session["usuario_logado"] = email_limpo
        print("DEBUG LOGIN: Login efetuado com sucesso! Redirecionando...")
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        # Executado estritamente se o e-mail não existir ou a senha estiver incorreta
        print(f"DEBUG LOGIN: Falha nas credenciais para o e-mail '{email_limpo}'")
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

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


# Rota motor de captura
@app.post("/api/iniciar_captura")
async def api_iniciar_captura(
    url_alvo: str = Form(...),
    titulo: str = Form(...),
    tipo_captura: str = Form(...) # Espera receber "FOTO" ou "VIDEO"
):
    print(f"🎬 Recebida requisição de captura: {tipo_captura} para a URL: {url_alvo}")
    
    # 1. Gera um ID único para essa nova evidência
    novo_id = f"REC-{str(uuid.uuid4())[:8].upper()}"

    # 2. Abre a URL solicitada no navegador padrão do usuário
    print(f"🌐 Abrindo navegador na URL: {url_alvo}")
    webbrowser.open(url_alvo)
    
    # Dá um tempo para o navegador abrir e carregar a página (3 segundos)
    time.sleep(3)

    # 3. Direciona para o fluxo correto com base no tipo escolhido
    if tipo_captura == "FOTO":
        # Chama a função de captura única (você precisa garantir que ela existe no Orchestrator)
        motor_captura.iniciar_fluxo_foto(novo_id, titulo)
        print("📸 Tirando foto da tela...")
        
    elif tipo_captura == "VIDEO":
        # Chama o fluxo de vídeo (que você já implementou e testou!)
        motor_captura.iniciar_fluxo_video(captura_id=novo_id, titulo=titulo)
        print("🔴 Gravação de vídeo iniciada. Rodando em segundo plano...")
        
        # Simulação: Como estamos em ambiente local e precisamos finalizar a gravação 
        # automaticamente para gerar o ZIP (já que não criamos o botão "Parar" na interface web ainda):
        # Vamos deixar gravando por 10 segundos e depois parar.
        time.sleep(10)
        motor_captura.finalizar_fluxo_video(captura_id=novo_id)

    return RedirectResponse(url=f"/sucessocap?id={novo_id}", status_code=303)