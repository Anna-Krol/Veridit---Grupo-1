class RepositoriesDB:
    """Camada de Persistência: Banco de dados central de registros"""
    def __init__(self):
        self._banco_em_memoria = {}

    def salvar_registro(self, id_registro: str, dados: dict) -> None:
        self._banco_em_memoria[id_registro] = dados
        print(f"[Persistence] Dados persistidos no BD para o ID: {id_registro}")

    def __init__(self):
        # Simulação de tabelas do Banco de Dados
        self._usuarios = {}
        self._capturas = {}
        self._faturamentos = {}
        
        # Cria um utilizador inicial padrão para testes imediatos
        self._inicializar_dados_teste()

    def _inicializar_dados_teste(self):
        # Cria uma classe anónima rápida para simular um Advogado já registado
        class AdvogadoFake:
            nome_completo = "Eduardo Almeida"
            email = "eduardo.almeida@ufba.br"
            senha = "123"
            cpf = "12345678901"
            tipo = "advogado"
            numero_oab = "OAB-BA12345"
            
        self._usuarios["eduardo.almeida@ufba.br"] = AdvogadoFake()

    def salvar_usuario(self, usuario):
        self._usuarios[usuario.email] = usuario
        print(f"[Persistence DB] Novo utilizador {usuario.email} persistido com sucesso.")

    def buscar_usuario_por_email(self, email: str):
        return self._usuarios.get(email)
