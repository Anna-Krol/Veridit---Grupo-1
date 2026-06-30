import sqlite3
import os

class RecordsRepository:
    def __init__(self):
       
        self.db_path = "capturas.db"
        self._inicializar_tabela()

    def _conectar(self):
        """Abre uma conexão segura com o banco de dados SQLite."""
        return sqlite3.connect(self.db_path)

    def _inicializar_tabela(self):
        """Cria a tabela de capturas caso ela ainda não exista no arquivo .db."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capturas (
                id TEXT PRIMARY KEY,
                titulo TEXT,
                data_inicio TEXT,
                data_fim TEXT,
                status TEXT,
                tipo TEXT,
                info_dados TEXT,
                usuario_responsavel TEXT,
                url TEXT
            )
        """)
        
        conexao.commit()
        conexao.close()

    def salvar_nova_captura(self, captura_id, titulo, data_inicio, tipo, info_dados="N/A", usuario_responsavel="N/A", url="N/A"):
        """Grava permanentemente a nova captura no banco de dados."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        cursor.execute("""
            INSERT INTO capturas (id, titulo, data_inicio, data_fim, status, tipo, info_dados, usuario_responsavel, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (captura_id, titulo, data_inicio, "Processando...", "Processando", tipo, info_dados, usuario_responsavel, url))
        
        conexao.commit()
        conexao.close()

    def atualizar_status(self, captura_id, status, data_fim=None):
        """Atualiza o status e opcionalmente a data de término no banco."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        if data_fim:
            cursor.execute("""
                UPDATE capturas 
                SET status = ?, data_fim = ? 
                WHERE id = ?
            """, (status, data_fim, captura_id))
        else:
            cursor.execute("""
                UPDATE capturas 
                SET status = ? 
                WHERE id = ?
            """, (status, captura_id))
            
        conexao.commit()
        conexao.close()
                
    def atualizar_data_fim(self, captura_id, data_fim):
        """Atualiza especificamente a data de término."""
        conexao = self._conectar()
        cursor = conexao.cursor()
        
        cursor.execute("""
            UPDATE capturas 
            SET data_fim = ? 
            WHERE id = ?
        """, (data_fim, captura_id))
        
        conexao.commit()
        conexao.close()

    def buscar_arquivo_fisico(self, captura_id: str):
        """
        Responsabilidade exclusiva da Persistência: vasculhar o HD.
        """
        nome_zip = f"{captura_id}.zip"
        if os.path.exists(nome_zip):
            return nome_zip, "application/zip"

        nome_png = f"{captura_id}.png"
        if os.path.exists(nome_png):
            return nome_png, "image/png"

        return None, None

    @property
    def banco_de_dados(self):
        """
        Esta propriedade simula o antigo dicionário que o seu CaptureOrchestrator usava!
        Lendo diretamente do SQLite e montando o formato esperado pelo resto do sistema.
        """
        conexao = self._conectar()
        
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        
        cursor.execute("SELECT * FROM capturas")
        linhas = cursor.fetchall()
        conexao.close()
        
        # Reconstrói a estrutura de dicionário para manter a compatibilidade perfeita
        dicionario_legado = {}
        for linha in linhas:
            dicionario_legado[linha["id"]] = {
                "titulo": linha["titulo"],
                "data_inicio": linha["data_inicio"],
                "data_fim": linha["data_fim"],
                "status": linha["status"],
                "tipo": linha["tipo"],
                "info_dados": linha["info_dados"],
                "usuario_responsavel": linha["usuario_responsavel"],
                "url": linha["url"]
            }
            
        return dicionario_legado