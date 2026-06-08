# business/user_service.py
from infrastructure.repository import UsuarioRepository

class UserService:
    # DIP (Inversão de Dependência): O serviço não cria o repositório, ele RECEBE o repositório.
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def autenticar_usuario(self, email: str, senha_informada: str) -> bool:
        usuario = self.repository.buscar_por_email(email)
        # Regra de negócio: Verifica se o usuário existe e se a senha bate
        if usuario and usuario["senha"] == senha_informada:
            return True
        return False

    def obter_dados_usuario(self, email: str):
         usuario = self.repository.buscar_por_email(email)
         if not usuario:
             return None
             
         return {
             "nome": usuario["nome"],
             "creditos": usuario.get("creditos", 0), # Pega os créditos reais do banco!
             "total_registros": 0,
             "este_mes": 0
         }
 
    def processar_pagamento_aprovado(self, email: str, pacote_selecionado: str, pacotes_disponiveis: dict) -> bool:
        pacote_obj = pacotes_disponiveis.get(pacote_selecionado)
        if not pacote_obj:
            return False
            
        # O int() força que o valor extraído seja estritamente um número inteiro
        # Verificamos pacote_obj.quantidade_creditos para não somar o valor em R$ sem querer
        creditos_comprados = int(pacote_obj.quantidade_creditos)
        
        self.repository.adicionar_creditos_e_pagar(email, creditos_comprados)
        return True