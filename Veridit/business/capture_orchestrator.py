from integration.capture_engine.state_controller import StateController
from business.artifact_generator import ArtifactGenerator
from persistence.records_repository import RecordsRepository

class CaptureOrchestrator:
    def __init__(self):
        self.engine = StateController()
        self.gerador_artefatos = ArtifactGenerator()
        self.banco = RecordsRepository()

    def iniciar_fluxo_video(self, captura_id, titulo):
        self.banco.salvar_nova_captura(captura_id, titulo, data_inicio="agora", tipo="VÍDEO")
        self.engine.start_video_capture()

    def iniciar_fluxo_foto(self, captura_id, titulo):
        """
        Executa o fluxo completo para o serviço de 1 crédito (Foto).
        Como tirar foto é instantâneo, não precisamos de threads em segundo plano.
        """
        # 1. Registra no banco de dados
        self.banco.salvar_nova_captura(captura_id, titulo, data_inicio="agora", tipo="FOTO")
        
        # 2. Manda a integração tirar o print e salvar com o ID da evidência
        nome_arquivo = f"{captura_id}.png"
        self.engine.capture_single_screen(filename=nome_arquivo)
        
        # 3. Atualiza o banco instantaneamente para Concluído
        self.banco.atualizar_status(captura_id, "Concluído", data_fim="agora")
        print(f"✅ Orquestrador: Fluxo de foto finalizado! Artefato gerado: {nome_arquivo}")

    def obter_todos_os_registros(self):
        """
        Retorna a lista de todas as capturas formatada para o Jinja2 (HTML).
        """
        lista_formatada = []
        for id_rec, dados in self.banco.banco_de_dados.items():
            lista_formatada.append({
                "id": id_rec,
                "titulo": dados["titulo"],
                "data": "08/06/2026", # Uma data fixa ou simulada para o design
                "status": dados["status"],
                "tipo": dados.get("tipo","N/A")
            })
        return lista_formatada    

    def pausar_fluxo_video(self):
        self.engine.pause_video_capture()

    def finalizar_fluxo_video(self, captura_id):
        self.engine.stop_video_capture()
        self.banco.atualizar_status(captura_id, "Processando")
        
        # Agora usando a classe com a nomenclatura fiel ao diagrama
        self.gerador_artefatos.create_zip_async(
            video_filename="registro_video.avi", 
            output_zipname=f"{captura_id}.zip",
            callback=lambda: self.banco.atualizar_status(captura_id, "Concluído")
        )