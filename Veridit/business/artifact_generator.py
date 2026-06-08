import zipfile
import threading
import time
import os

class ArtifactGenerator:
    def create_zip_async(self, video_filename, output_zipname, callback=None):
        """Inicia a compactação em uma Thread separada (Assíncrono)."""
        print("📦 Colocando a geração do ZIP na fila de processamento...")
        
        # Cria a thread para não travar o sistema principal
        thread = threading.Thread(
            target=self._compress_file, 
            args=(video_filename, output_zipname, callback)
        )
        thread.start()

    def _compress_file(self, file_to_zip, zip_name, callback):
        """O trabalho pesado que roda escondido do usuário."""
        time.sleep(2) # Simulando o tempo de juntar relatórios PDF, etc.
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(file_to_zip):
                zipf.write(file_to_zip)
                
        print(f"✅ Arquivo ZIP gerado com sucesso: {zip_name}")
        
        # Se houver uma função de aviso (como atualizar o banco), chama ela aqui
        if callback:
            callback()