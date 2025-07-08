import json
from typing import List
from zona import Zona



class Veiculo:
    def __init__(self,id: str, tipo: str,peso_maximo : int, velocidade: int ):
        self.id: str = id
        self.tipo: str = tipo
        self.peso_maximo_kg: int = peso_maximo #kg
        self.velocidade: int = velocidade #hm/h

    @classmethod
    def from_json(cls, caminho_arquivo: str) -> List['Veiculo']:
        veiculos = []
        try:
            with open(caminho_arquivo, 'r') as file:
                dados = json.load(file)
                for dados_veiculo in dados:
                    veiculo = cls(
                        dados_veiculo["id"],
                        dados_veiculo["tipo"],
                        dados_veiculo["peso_maximo"],
                        dados_veiculo["velocidade"]
                    )
                    veiculos.append(veiculo)
                return veiculos
        except FileNotFoundError:
            print(f"O arquivo {caminho_arquivo} não foi encontrado.")
            return []
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON.")
            return []
        
    def getId(self):
        return self.id
    
    def getTipo(self):
        return self.tipo

    def getCapacidade_carga(self):
        return self.capacidade_carga

    def getAutonomia(self):
        return self.autonomia

    def getCapacidade(self):
        return self.peso_maximo_kg

    def getVelocidade(self):
        return self.velocidade
        
       
    def __str__(self):
        return "("+ self.id + "," + self.tipo +  ")"
    
    def pode_continuar(veiculo, peso_necessario):
        return veiculo.getCapacidade() >= peso_necessario

    def selecionar_veiculo_global_com_grafo(frota, base, rota):
        print("\n[DEBUG] Iniciando seleção de veículo...")
    
        # Identificar o tipo dominante da conexão ao longo da rota
        tipos_conexao = set(
            c["tipo"] for zona in rota for c in zona.conexoes if c["destino"] in [z.getNome() for z in rota]
        )
    
        if len(tipos_conexao) > 1:
            print("[DEBUG] A rota contém múltiplos tipos de conexão, mas apenas um tipo é permitido.")
            return None
    
        tipo_conexao = tipos_conexao.pop() if tipos_conexao else None
        print(f"[DEBUG] Tipo de conexão para a rota: {tipo_conexao}")
    
        # Filtrar veículos compatíveis
        veiculos_filtrados = [v for v in frota if v.getTipo() == tipo_conexao]
    
        # Validar restrições de zonas
        for zona in rota:
            if tipo_conexao not in zona.restricoes:
                print(f"[DEBUG] A zona {zona.getNome()} não aceita o tipo {tipo_conexao}.")
                return None
    
        if not veiculos_filtrados:
            print("[DEBUG] Nenhum veículo compatível com o tipo de conexão da rota.")
            return None
    
        # Calcular peso total necessário
        peso_total = sum(Zona.calcular_suprimentos_necessarios(z.getGravidade()) for z in rota)
        veiculos_por_carga = [v for v in veiculos_filtrados if v.getCapacidade() >= peso_total]
    
        if veiculos_por_carga:
            return max(veiculos_por_carga, key=lambda v: v.getCapacidade())
    
        print("[DEBUG] Nenhum veículo com capacidade suficiente foi encontrado.")
        return None


