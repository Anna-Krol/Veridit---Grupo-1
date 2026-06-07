import sqlite3
import uuid

def inicializar_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Cria a tabela de usuários se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_usuario(nome, email, cpf, senha, tipo):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, cpf, senha, tipo) VALUES (?, ?, ?, ?, ?)",
            (nome.strip(), email.strip().lower(), cpf.strip(), senha.strip(), tipo)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Email ou CPF já existem
    finally:
        conn.close()

def validar_login(email, senha):
    # Trata os dados digitados para evitar erros invisíveis de digitação
    email_limpo = email.strip().lower()
    senha_limpa = senha.strip()
    
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    # Buscamos usando LOWER(email) para ignorar se o usuário digitou maiúsculas/minúsculas
    cursor.execute("SELECT senha, nome, tipo FROM usuarios WHERE LOWER(email) = ?", (email_limpo,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    # 1. Verifica se o e-mail existe
    if resultado is None:
        print(f"DEBUG LOGIN: E-mail '{email_limpo}' não encontrado no banco.")
        return False
    
    # 2. Se o e-mail existe, verifica a senha de forma limpa
    senha_salva = resultado[0]
    if senha_salva == senha_limpa:
        print(f"DEBUG LOGIN: Sucesso para '{email_limpo}' (Perfil: {resultado[2]})")
        return True
    else:
        print(f"DEBUG LOGIN: Senha incorreta para '{email_limpo}'.")
        return False
    
    

def criar_token_recuperacao(email):
    email_limpo = email.strip().lower() # Remove espaços e força minúsculas
    
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    # 1. Primeiro, vamos VERIFICAR se o e-mail realmente existe na tabela
    cursor.execute("SELECT email FROM usuarios WHERE LOWER(email) = ?", (email_limpo,))
    usuario_existe = cursor.fetchone()
    
    if not usuario_existe:
        conn.close()
        print(f"DEBUG RECUPERAÇÃO: O e-mail '{email_limpo}' NÃO foi encontrado no banco.")
        return None # Retorna None para avisar a rota que o e-mail não existe
        
    # 2. Se existe, gera o token e atualiza
    token = str(uuid.uuid4())
    cursor.execute("UPDATE usuarios SET token_recuperacao = ? WHERE LOWER(email) = ?", (token, email_limpo))
    conn.commit()
    conn.close()
    
    print(f"DEBUG RECUPERAÇÃO: Token gerado com sucesso para {email_limpo}: {token}")
    return token

def atualizar_senha_por_token(token, nova_senha):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    # Procura o usuário que tem esse token
    cursor.execute("SELECT email FROM usuarios WHERE token_recuperacao = ?", (token,))
    resultado = cursor.fetchone()
    
    if resultado:
        # Atualiza a senha e limpa o token (para que ele não seja usado duas vezes)
        cursor.execute("UPDATE usuarios SET senha = ?, token_recuperacao = NULL WHERE token_recuperacao = ?", (nova_senha, token))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def buscar_usuario_por_email(email):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    # Puxa o nome, tipo e outras infos baseado no email da sessão
    cursor.execute("SELECT nome, tipo FROM usuarios WHERE LOWER(email) = ?", (email.strip().lower(),))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            "nome": resultado[0],
            "tipo": resultado[1]
        }
    return None
