# infrastructure/dependencies.py

# 1. Imports de todas as camadas para fazer a fiação do sistema
from persistence.records_repository import RecordsRepository
from integration.capture_engine.state_controller import StateController
from integration.notification_adapter import NotificationAdapter
from business.artifact_generator import ArtifactGenerator
from business.capture_orchestrator import CaptureOrchestrator
from business.user_service import UserService
from integration.email_adapter import EmailAdapter
from infrastructure.repository import UsuarioRepository


# 2. Criação das instâncias isoladas em nível de infraestrutura
_banco = RecordsRepository()
_engine = StateController()
_notificador = NotificationAdapter()
_artefatos = ArtifactGenerator()
_banco_usuarios = UsuarioRepository()
_email_adapter = EmailAdapter()

def get_motor_captura() -> CaptureOrchestrator:
    """
    Fábrica responsável por injetar as dependências.
    Quem chama essa função recebe o Orquestrador pronto sem saber como ele foi feito.
    """
    return CaptureOrchestrator(
        engine=_engine,
        gerador_artefatos=_artefatos,
        banco=_banco,
        notificador=_notificador
    )
def get_user_service() -> UserService:
    return UserService(
        repository=_banco_usuarios,
        email_adapter=_email_adapter
    )