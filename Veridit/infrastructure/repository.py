import sqlite3

class UsuarioRepository:
    def __init__(self, db_path="usuarios.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def buscar_por_email(self, email: str):
        conn = sqlite3.connect('usuarios.db') # Ajuste o caminho se necessário
        cursor = conn.cursor()
        
        # Busca os dados no banco padronizando para minúsculo
        cursor.execute("SELECT nome, email, senha, tipo, creditos FROM usuarios WHERE LOWER(email) = ?", (email.strip().lower(),))
        resultado = cursor.fetchone()
        conn.close()
        
        # 🚨 O PONTO CRÍTICO ESTÁ AQUI:
        # Se o banco retornou None (e-mail não cadastrado), paramos aqui e retornamos None!
        if resultado is None:
            print(f"DEBUG REPOSITORY: O e-mail '{email}' não foi localizado no SQLite.")
            return None
            
        # SE ENCONTROU, aí sim o código continua para criar o dicionário ou o objeto com segurança:
        # (Se a sua equipe usa uma classe chamada Usuario, adapte para: return Usuario(...))
        return {
            "nome": resultado[0],
            "email": resultado[1],
            "senha": resultado[2],
            "tipo": resultado[3],
            "creditos": resultado[4]
        }
    def garantir_coluna_creditos(self):
        # Responsabilidade: Garantir que o banco tem a coluna antes de dar erro
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE usuarios ADD COLUMN creditos INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.OperationalError:
                pass # A coluna já existe, tudo certo!

    def adicionar_creditos_e_pagar(self, email: str, qtd_creditos: int):
        self.garantir_coluna_creditos()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Soma com garantia de COALESCE (se for nulo, vira 0) e forçando ser número Inteiro
            cursor.execute("UPDATE usuarios SET creditos = COALESCE(creditos, 0) + ? WHERE email = ?", (int(qtd_creditos), email))
            
            # Atualiza o status financeiro (ignora erros caso a tabela faturamentos ainda não exista no seu teste)
            try:
                cursor.execute("UPDATE faturamentos SET status_pagamento = 'pago' WHERE usuario_email = ? AND status_pagamento = 'pendente'", (email,))
            except sqlite3.OperationalError:
                pass 
                
            conn.commit()