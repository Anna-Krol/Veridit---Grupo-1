from integration.capture_engine.state_controller import StateController
from business.artifact_generator import ArtifactGenerator
from persistence.records_repository import RecordsRepository
from integration.notification_adapter import NotificationAdapter

class CaptureOrchestrator:
    def __init__(self):
        self.engine = StateController()
        self.gerador_artefatos = ArtifactGenerator()
        self.banco = RecordsRepository()
        self.notificador = NotificationAdapter()

    def iniciar_fluxo_video(self, captura_id, titulo, data_inicio, usuario, url):
        """
        Inicia o fluxo de vídeo 
        """
        info_dados = "1 vídeo de 10s"
    
        self.banco.salvar_nova_captura(
            captura_id=captura_id, 
            titulo=titulo, 
            data_inicio=data_inicio, 
            tipo="VIDEO",
            info_dados=info_dados,
            usuario_responsavel=usuario,
            url=url
        )
        self.notificador.enviar_notificacao(
            titulo="🔴 Gravação Iniciada", 
            mensagem=f"Capturando evidências de: {titulo}. Não feche o navegador!"
        )
        self.engine.start_video_capture()

    def iniciar_fluxo_foto(self, captura_id, titulo, data_inicio, data_fim, usuario, url):
        """
        Executa o fluxo completo para a captura estática (Foto).
        """
        info_dados = "1 imagem"
        
        # 1. Registra no banco de dados com os parâmetros dinâmicos reais
        self.banco.salvar_nova_captura(
            captura_id=captura_id, 
            titulo=titulo, 
            data_inicio=data_inicio, 
            tipo="FOTO",
            info_dados=info_dados,
            usuario_responsavel=usuario,
            url=url
        )
        self.notificador.enviar_notificacao(
            titulo="📸 Captura de Tela", 
            mensagem="Tirando foto da evidência digital..."
        )
        
        nome_arquivo = f"{captura_id}.png"
        self.engine.capture_single_screen(filename=nome_arquivo)

        # 3. Atualiza o banco instantaneamente para Concluído injetando a data_fim real
        self.banco.atualizar_status(captura_id, "Concluído", data_fim=data_fim)
        print(f"✅ Orquestrador: Fluxo de foto finalizado! Artefato gerado: {nome_arquivo}")

    def obter_todos_os_registros(self):
        """
        Retorna a lista de todas as capturas formatada estritamente com as
        propriedades exigidas pelo Apêndice A.
        """
        lista_formatada = []
        
        for id_rec, dados in self.banco.banco_de_dados.items():
            lista_formatada.append({
                "id": id_rec,
                "titulo": dados.get("titulo"),
                "data_inicio": dados.get("data_inicio", "N/A"), # Modificado para tempo real
                "data_fim": dados.get("data_fim", "Processando..."), # Modificado para tempo real
                "status": dados.get("status"),
                "tipo_dados": dados.get("tipo", "N/A"),
                "info_dados": dados.get("info_dados", "N/A"),
                "usuario_responsavel": dados.get("usuario_responsavel", "N/A"),
                "url": dados.get("url", "N/A")
            })
        return lista_formatada    

    def pausar_fluxo_video(self):
        self.engine.pause_video_capture()

    def finalizar_fluxo_video(self, captura_id, data_fim):
        """
        Para o vídeo e passa a data_fim real colhida na finalização.
        """
        self.engine.stop_video_capture()
        
        # Atualiza para processando enquanto gera o ZIP
        self.banco.atualizar_status(captura_id, "Processando")

        # Atualiza a data de encerramento real do vídeo no banco
        if hasattr(self.banco, 'atualizar_data_fim'): 
            self.banco.atualizar_data_fim(captura_id, data_fim)

        # Executa o gerador assíncrono que acionará o callback ao terminar
        self.gerador_artefatos.create_zip_async(
            video_filename="registro_video.avi", 
            output_zipname=f"{captura_id}.zip",
            callback=lambda: self.banco.atualizar_status(captura_id, "Concluído", data_fim=data_fim)
        )