import cv2
import numpy as np
import mss

class VideoEncoder:
    def __init__(self, output_filename="registro_video.avi", fps=20.0):
        self.output_filename = output_filename
        self.fps = fps
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1] 
        self.writer = None

    def start_encoding(self):
        """Prepara o arquivo de vídeo para começar a receber imagens."""
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        width, height = self.monitor["width"], self.monitor["height"]
        self.writer = cv2.VideoWriter(
            self.output_filename, 
            fourcc, 
            self.fps, 
            (width, height)
        )

    def capture_frame(self):
        """Tira print de 1 frame e adiciona ao vídeo em andamento."""
        if self.writer:
            img = np.array(self.sct.grab(self.monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            self.writer.write(frame)

    def take_screenshot(self, filename="evidencia_foto.png"):
        """Tira uma única foto da tela e salva diretamente."""
        caminho = self.sct.shot(mon=1, output=filename)
        return caminho

    def stop_encoding(self):
        """Salva o vídeo final no disco e libera a memória."""
        if self.writer:
            self.writer.release()
            self.writer = None
            