import random
from veiculo import *

TIPOS_CLIMA = [
        {"tipo": "ensolarado", "impacto": 1.0},  # Nenhum impacto
        {"tipo": "chuva", "impacto": 0.7},
        {"tipo": "neve", "impacto": 0.5},
        {"tipo": "tempestade", "impacto": 0.6},  
]

class Clima:
    def __init__(self, zona, tipo, impacto):
        self.zona = zona  # Nome da zona ou instância da classe Zona
        self.tipo = tipo  # Tipo de clima (e.g., "chuva", "neve", "ensolarado")
        self.impacto = impacto  # Percentual de impacto na velocidade (e.g., 0.7 significa 70% da velocidade normal)

def atualizar_clima_para_zonas(zonas):
    # Pesos para a geração de climas (ajuste conforme necessário)
    pesos = [0.8, 0.1, 0.05, 0.05]  # 80% ensolarado, 10% chuva, etc.

    for zona in zonas:
        tipo_clima = random.choices(TIPOS_CLIMA, weights=pesos, k=1)[0]
        zona.clima_atual = Clima(
            zona=zona.getNome(),
            tipo=tipo_clima["tipo"],
            impacto=tipo_clima["impacto"]
        )