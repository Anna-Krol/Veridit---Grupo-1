from plyer import notification

class NotificationAdapter:
    def enviar_notificacao(self, titulo: str, mensagem: str):
        """
        Dispara uma notificação nativa no sistema operacional (Windows/Mac/Linux).
        """
        try:
            notification.notify(
                title=titulo,
                message=mensagem,
                app_name="Veridit RISE Labs",
                timeout=5 # A notificação some sozinha após 5 segundos
            )
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível exibir a notificação nativa. Erro: {e}")