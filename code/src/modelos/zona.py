import json
import math
import random
from typing import Dict, List, Optional


class Zona:

    def __init__(self, nome: str, populacao: int, x : float, y : float, isBase : bool):
        self.nome = nome
        self.populacao = populacao
        self.x = x #latitude
        self.y = y #longitude
        self.necessidade = None
        self.gravidade = None # 0 - 10 (Gravissimo)
        self.isBase = isBase
        self.restricoes = []
        self.conexoes = []
        self.clima_atual = None  # Referência ao clima atual da zona
        self.deadline = 0.0


    
    @classmethod
    def from_json(cls, caminho_arquivo) -> List['Zona']:
        zonas = []  # Lista onde vamos armazenar as instâncias de Zona
        try:
            with open(caminho_arquivo, 'r') as file:
                dados = json.load(file)
                for zona_dados in dados:
                    zona = cls(zona_dados["nome"], zona_dados["populacao"], zona_dados["x"], zona_dados["y"], zona_dados["isBase"])
                    zona.necessidade = zona_dados.get("necessidade")
                    zona.gravidade = zona_dados.get("gravidade")
                    zona.restricoes = zona_dados.get("restricoes", [])
                    zona.deadline = zona_dados.get("janela_tempo_critica")
                    zona.conexoes = zona_dados.get("conexoes", [])
                    zonas.append(zona)
                return zonas
        
        except FileNotFoundError:
            print(f"O arquivo {caminho_arquivo} não foi encontrado.")
            return []
        
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON.")
            return []
        
    def getNome(self):
        return self.nome
    
    def getPopulacao(self):
        return self.populacao

    def getX(self):
        return self.x

    def getY(self):
        return self.y
    
    def getisBase(self):
        return self.isBase
    
    def getGravidade(self):
        return self.gravidade
    
    def setGravidade(self, num):
        self.gravidade = num
    
    def getNecessidade(self):
        return self.necessidade

    def setNecessidade(self, num):
        self.necessidade = num

    def getDeadline(self):
        return self.deadline
    
    def setDeadline(self, num):
        self.deadline = num


    def __str__(self):
        return "("+ self.nome + ")"
    
    def __hash__(self):
        return hash(self.nome)  # Use um atributo único, como 'nome', para gerar o hash.

    def __eq__(self, other):
        if isinstance(other, Zona):
            return self.nome == other.nome
        return False
    
    def calcular_distancia(zona1, zona2) -> float:
        """
        Calcula a distância entre duas zonas usando a fórmula de Haversine.
        """
        import math 
    
        R = 6371  # Raio da Terra em km
        lat1, lon1 = math.radians(zona1.getX()), math.radians(zona1.getY())
        lat2, lon2 = math.radians(zona2.getX()), math.radians(zona2.getY())
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
    
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distancia = R * c
    
        return distancia

    @staticmethod
    def calcular_suprimentos_necessarios(gravity):
        return (gravity or 0) * 100

    def calcular_prioridade(zona, base):
        distancia = Zona.calcular_distancia(zona, base)
        gravidade = zona.getGravidade()
        return gravidade * 10 - distancia  # 10 é o peso arbitrário para gravidade
    
    def aplicar_impacto_clima(self, veiculo):
        if self.clima_atual:
            return veiculo.getVelocidade() * self.clima_atual.impacto
            
        return veiculo.getVelocidade()
    
    def atribuir_deadline_por_distancia(zonas_afetadas, base):
        for zona in zonas_afetadas:
            distancia = Zona.calcular_distancia(base, zona)  # Distância da base à zona
            prazo = distancia / 70  # Considera velocidade média de 60 km/h
            margem_segurança = 1.2  # Margem adicional de 20%
            deadline = prazo * margem_segurança
            zona.setDeadline(deadline)
