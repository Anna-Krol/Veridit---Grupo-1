class RecordsRepository:
    def __init__(self):
        
        self.banco_de_dados = {}

    def salvar_nova_captura(self, captura_id, titulo, data_inicio, tipo="N/A"):
        self.banco_de_dados[captura_id] = {
            "titulo": titulo,
            "data_inicio": data_inicio,
            "data_fim": None,
            "status": "Gravando",
            "tipo": tipo
        }
        print(f"💾 BD Capturas: Registro '{titulo}' ({tipo}) salvo")

    def atualizar_status(self, captura_id, status, data_fim=None):
        if captura_id in self.banco_de_dados:
            self.banco_de_dados[captura_id]["status"] = status
            if data_fim:
                self.banco_de_dados[captura_id]["data_fim"] = data_fim
            print(f"💾 BD Capturas: Status do ID {captura_id} atualizado para: {status}")