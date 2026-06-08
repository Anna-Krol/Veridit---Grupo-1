import threading
import time
from .video_encoder import VideoEncoder  # Importa o operário que acabamos de criar

class StateController:
    def __init__(self):
        self.encoder = VideoEncoder()
        self.is_recording = False
        self.is_paused = False
        self.thread = None

    def capture_single_screen(self, filename="evidencia_foto.png"):
        """Função para o serviço de 1 crédito (Apenas a foto)."""
        print("📸 Iniciando captura de tela única...")
        self.encoder.take_screenshot(filename)
        print("✅ Captura finalizada.")

    def start_video_capture(self):
        """Função para o serviço de 3 créditos (Vídeo)."""
        if self.is_recording:
            return

        self.encoder.start_encoding()
        self.is_recording = True
        self.is_paused = False
        
        # Inicia o operário em segundo plano
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()
        print("🔴 Gravação de vídeo iniciada.")

    def _record_loop(self):
        """O loop invisível que dita o ritmo da gravação."""
        sleep_time = 1.0 / self.encoder.fps

        while self.is_recording:
            start_time = time.time()

            if not self.is_paused:
                self.encoder.capture_frame()

            elapsed = time.time() - start_time
            time.sleep(max(0, sleep_time - elapsed))

    def pause_video_capture(self):
        """Altera o estado de pausa do vídeo."""
        if self.is_recording:
            self.is_paused = not self.is_paused
            print("⏸️ Vídeo pausado." if self.is_paused else "▶️ Vídeo retomado.")

    def stop_video_capture(self):
        """Mata o processo de gravação com segurança."""
        if not self.is_recording:
            return

        self.is_recording = False
        if self.thread:
            self.thread.join()

        self.encoder.stop_encoding()
        print("⏹️ Vídeo finalizado com sucesso.")