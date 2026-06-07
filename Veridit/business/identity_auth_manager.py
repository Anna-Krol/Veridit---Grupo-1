# business/identity_auth_manager.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Estruturas de Dados conformes ao Apêndice A do Documento de Requisitos
@dataclass
class UsuarioComum:
    nome_completo: str
    email: str
    senha: str
    cpf: str
    tipo: str = "comum"

@dataclass
class Advogado:
    nome_completo: str
    email: str
    senha: str
    cpf: str
    numero_oab: str
    tipo: str = "advogado"

class IdentityAuthManager:
    def __init__(self, repositories_db):
        self.db = repositories_db
        # Mantém a sessão simulada ativa no back-end (REQ03 / REQ04)
        self.sessao_ativa: Optional[Dict[str, Any]] = None

    async def cadastrar_usuario(self, dados: Dict[str, str]) -> str:
        """
        Implementa o REQ 01 - Cadastrar Usuário.
        Valida a Decisão D1 (Advogados vs Usuários Comuns) e os campos do Apêndice A.
        """
        email = dados.get("email")
        if not email or "@" not in email:
            raise ValueError("E-mail inválido para registo.")

        # Validação de Unicidade
        if self.db.buscar_usuario_por_email(email):
            raise ValueError("Este e-mail já está registado no sistema.")

        tipo_usuario = dados.get("tipo")
        
        if tipo_usuario == "advogado":
            if not dados.get("numero_oab"):
                raise ValueError("O perfil de Advogado exige o preenchimento da OAB (Apêndice A).")
            
            usuario = Advogado(
                nome_completo=dados["nome_completo"],
                email=dados["email"],
                senha=dados["senha"],  # Numa aplicação real, aplicar hash de segurança
                cpf=dados["cpf"],
                numero_oab=dados["numero_oab"]
            )
        elif tipo_usuario == "comum":
            usuario = UsuarioComum(
                nome_completo=dados["nome_completo"],
                email=dados["email"],
                senha=dados["senha"],
                cpf=dados["cpf"]
            )
        else:
            raise ValueError("Tipo de utilizador inválido para esta versão (Decisão D1).")

        # Grava os dados na camada de persistência
        self.db.salvar_usuario(usuario)
        return f"Utilizador '{usuario.nome_completo}' ({usuario.tipo.upper()}) registado com sucesso!"

    async def logar_sistema(self, email: str, senha: str) -> Dict[str, Any]:
        """Implementa o REQ 03 - Logar no Sistema"""
        usuario = self.db.buscar_usuario_por_email(email)
        if not usuario or usuario.senha != senha:
            raise ValueError("Credenciais incorretas (E-mail ou Senha inválidos).")
        
        self.sessao_ativa = {
            "email": usuario.email,
            "nome": usuario.nome_completo,
            "tipo": usuario.tipo,
            "oab": getattr(usuario, "numero_oab", "Não aplicável")
        }
        return self.sessao_ativa

    async def sair_sistema(self) -> str:
        """Implementa o REQ 04 - Sair do Sistema"""
        if not self.sessao_ativa:
            return "Nenhuma sessão ativa encontrada."
        nome = self.sessao_ativa["nome"]
        self.sessao_ativa = None
        return f"Sessão encerrada com sucesso para {nome}."

    async def recuperar_senha(self, email: str) -> str:
        """Implementa o REQ 02 - Recuperar Senha"""
        usuario = self.db.buscar_usuario_por_email(email)
        if not usuario:
            raise ValueError("E-mail não encontrado no sistema Veridit.")
        return f"Instruções para recuperação de acesso enviadas para {email}."