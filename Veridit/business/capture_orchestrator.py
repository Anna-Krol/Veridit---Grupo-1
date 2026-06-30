# business/capture_orchestrator.py
import webbrowser
import time
from datetime import datetime

class CaptureOrchestrator:
    def __init__(self, engine, gerador_artefatos, banco, notificador):
        """
        A classe e o arquivo são 100% puros. 
        Não há NENHUM import de persistência ou integração aqui dentro.
        """
        self.engine = engine
        self.gerador_artefatos = gerador_artefatos
        self.banco = banco
        self.notificador = notificador

    def obter_artefato_para_download(self, captura_id: str):
        """
        Regra de negócio pura: Delega a busca física para a persistência.
        """
        return self.banco.buscar_arquivo_fisico(captura_id)

    def iniciar_fluxo_video(self, captura_id, titulo, data_inicio, usuario, url):
        """
        EVOLUÍDO: Agora este método centraliza todo o fluxo de vídeo.
        A interface apenas o chama e ele governa todo o resto sozinho.
        """
        # 1. Abre o navegador e espera o site carregar
        webbrowser.open(url)
        time.sleep(3)

        # 2. Registra no banco de dados e dispara a notificação nativa
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
        
        # 3. Liga o motor de gravação da camada de integração
        self.engine.start_video_capture()

        # 4. Controla o tempo de gravação (tiramos do web_ui e trouxemos para cá)
        time.sleep(10)
        
        # 5. Finaliza automaticamente chamando a rotina interna abaixo
        tempo_fim_video = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.finalizar_fluxo_video(captura_id, tempo_fim_video)

    def iniciar_fluxo_foto(self, captura_id, titulo, data_inicio, usuario, url):
       
        webbrowser.open(url)
        time.sleep(3) 

        info_dados = "1 imagem"
        data_fim = datetime.now().strftime("%d/%m/%Y %H:%M:%S") # Calcula o fim AQUI
        
        self.banco.salvar_nova_captura(captura_id=captura_id, titulo=titulo, data_inicio=data_inicio, tipo="FOTO", info_dados=info_dados, usuario_responsavel=usuario, url=url)
        self.notificador.enviar_notificacao(titulo="📸 Captura de Tela", mensagem="Tirando foto da evidência digital...")
        
        nome_arquivo = f"{captura_id}.png"
        self.engine.capture_single_screen(filename=nome_arquivo)
        
        self.banco.atualizar_status(captura_id, "Concluído", data_fim=data_fim)

    def obter_todos_os_registros(self):
        lista_formatada = []
        for id_rec, dados in self.banco.banco_de_dados.items():
            lista_formatada.append({
                "id": id_rec, "titulo": dados.get("titulo"), "data_inicio": dados.get("data_inicio"),
                "data_fim": dados.get("data_fim"), "status": dados.get("status"),
                "tipo_dados": dados.get("tipo"), "info_dados": dados.get("info_dados"),
                "usuario_responsavel": dados.get("usuario_responsavel"), "url": dados.get("url")
            })
        return lista_formatada    

    def pausar_fluxo_video(self):
        self.engine.pause_video_capture()

    def finalizar_fluxo_video(self, captura_id, data_fim):
        self.engine.stop_video_capture()
        self.banco.atualizar_status(captura_id, "Processando")
        if hasattr(self.banco, 'atualizar_data_fim'): 
            self.banco.atualizar_data_fim(captura_id, data_fim)
        self.gerador_artefatos.create_zip_async(
            video_filename="registro_video.avi", output_zipname=f"{captura_id}.zip",
            callback=lambda: self.banco.atualizar_status(captura_id, "Concluído", data_fim=data_fim)
        )