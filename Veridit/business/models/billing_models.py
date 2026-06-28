# business/models/billing_models.py
from dataclasses import dataclass

@dataclass
class PacoteCredito:
    nome: str
    quantidade_creditos: int
    valor_por_credito: float
    descricao_beneficios: str

# Na primeira versão, os pacotes básico, médio e premium são oferecidos.
PACOTES_DISPONIVEIS = {
    "basico": PacoteCredito("Básico", 10, 5.00, "Acesso padrão a capturas"),
    "medio": PacoteCredito("Médio", 50, 4.50, "Desconto por volume"),
    "premium": PacoteCredito("Premium", 100, 4.00, "Suporte prioritário e menor custo")
}

@dataclass
class DadosFaturamento:
    nome_completo: str
    email: str
    telefone: str
    cpf: str
    cep: str
    endereco: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    estado: str