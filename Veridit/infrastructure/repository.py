import sqlite3

class UsuarioRepository:
    def __init__(self, db_path="usuarios.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def buscar_por_email(self, email: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Certifique-se de adicionar a coluna creditos na busca!
            cursor.execute("SELECT nome, email, senha, tipo, creditos FROM usuarios WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "nome": row[0], 
                    "email": row[1], 
                    "senha": row[2], 
                    "tipo": row[3],
                    "creditos": row[4] if row[4] is not None else 0
                }
            return None
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