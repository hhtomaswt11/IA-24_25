from random import randint
from Graph import Graph
from clima import atualizar_clima_para_zonas
from veiculo import *
from zona import *

def verificar_deadline_por_distancia(zona, tempo_final):
    if zona.getDeadline() is None:
        return False

    if tempo_final > zona.getDeadline():
        print(f"Entrega para {zona.getNome()} falhou. Tempo ({tempo_final:.2f}h) excede o deadline ({zona.getDeadline():.2f}h).")
        return False
    else:
        print(f"Entrega para {zona.getNome()} realizada com sucesso dentro do prazo.")
        return True
    

def escolher_zonas_afetadas(zonas, num_entregas):
    print("\nZonas disponíveis:")
    for i, zona in enumerate(zonas):
        clima_info = (
            f"{zona.clima_atual.tipo} (Impacto: {zona.clima_atual.impacto})"
            if hasattr(zona, 'clima_atual') and zona.clima_atual
            else "Sem informação de clima"
        )
        print(
            f"{i + 1}. {zona.getNome()} "
            f"(População: {zona.getPopulacao()}, Gravidade: {zona.getGravidade()}, Clima: {clima_info})"
        )

    escolhidas = []
    while len(escolhidas) < num_entregas:
        try:
            restante = num_entregas - len(escolhidas)
            escolha = input(
                f"Escolha o número das zonas afetadas separadas por vírgula (restante {restante} zonas): "
            ).strip()

            if not escolha:
                print(f"Você precisa selecionar {restante} zonas restantes.")
                continue

            indices = [int(i.strip()) - 1 for i in escolha.split(",")]

            # Validar e adicionar zonas
            novas_escolhidas = []
            for i in indices:
                if i < 0 or i >= len(zonas):
                    print(f"Número inválido: {i + 1}. Por favor, escolha um número válido.")
                elif zonas[i] in escolhidas:
                    print(f"A zona '{zonas[i].getNome()}' já foi selecionada. Escolha outra.")
                else:
                    novas_escolhidas.append(zonas[i])

            if len(escolhidas) + len(novas_escolhidas) > num_entregas:
                print(f"Você escolheu zonas demais. Escolha no máximo {restante} zonas restantes.")
                continue

            escolhidas.extend(novas_escolhidas)

            if len(escolhidas) < num_entregas:
                print(f"Você ainda precisa selecionar {restante - len(novas_escolhidas)} zonas.")
        except (ValueError, IndexError):
            print("Entrada inválida. Certifique-se de usar números válidos separados por vírgula.")

    # Ajustar gravidade e necessidade para cada zona escolhida
    from random import randint
    for zona in escolhidas:
        # Se quiser randomizar a gravidade, faça algo como randint(1, 5)
        zona.setGravidade(randint(1,5))
        # Agora ajusta a necessidade a partir da gravidade
        zona.setNecessidade(Zona.calcular_suprimentos_necessarios(zona.getGravidade()))

    return escolhidas


def escolher_algoritmo():
    algoritmos = {
        '1': 'A*',
        '2': 'BFS',
        '3': 'DFS',
        '4': 'Greedy'
    }
    print("\nEscolha o algoritmo de busca para as rotas:")
    for key, value in algoritmos.items():
        print(f"{key}. {value}")

    escolha = None
    while escolha not in algoritmos:
        escolha = input("Digite o número correspondente ao algoritmo desejado: ").strip()
        if escolha not in algoritmos:
            print("Escolha inválida. Por favor, tente novamente.")

    return algoritmos[escolha]




def gerenciar_entregas(base, zonas_afetadas, grafo, frota, algoritmo):
    # Mapeamento de algoritmos para métodos de busca
    algoritmos_map = {
        'A*': grafo.procura_aStar_typeFilter,
        'BFS': grafo.procura_BFS_typeFilter,
        'DFS': grafo.procura_DFS_typeFilter,
        'Greedy': grafo.greedy_typeFilter
    }

    # Verificar se o algoritmo selecionado está disponível
    if algoritmo not in algoritmos_map:
        print(f"[ERRO] Algoritmo '{algoritmo}' não suportado.")
        return None, None

    busca_rotas = algoritmos_map[algoritmo]

    caminho = [base]     # histórico de visita (na ordem)
    tempo_total = 0.0
    local_atual = base

    # Função auxiliar para remover as zonas que já não precisam de suprimentos
    def limpar_zonas_completas(lista):
        return [z for z in lista if z.getNecessidade() > 0]

    # -------------------------------------------------------------------------
    # Função para percorrer uma rota (lista de Zonas), entregando parcial.
    # Retorna (último_nodo, capacidade_restante).
    def percorrer_rota(rota, veiculo, cap_inicial):
        nonlocal tempo_total, caminho, local_atual
        cap_rest = cap_inicial

        for i in range(len(rota) - 1):
            origem = rota[i]
            destino = rota[i + 1]

            dist = grafo.get_arc_cost(origem, destino)
            if dist == float('inf'):
                # Não há conexão
                return (destino, cap_rest)

            # Ajustar velocidade por clima
            impA = origem.clima_atual.impacto if origem.clima_atual else 1.0
            impB = destino.clima_atual.impacto if destino.clima_atual else 1.0
            vel_ajustada = veiculo.getVelocidade() * impA * impB
            tempo_segmento = dist / vel_ajustada if vel_ajustada > 0 else float('inf')
            verificar_deadline_por_distancia(destino,tempo_segmento)
            tempo_total += tempo_segmento

            caminho.append(destino)
            local_atual = destino

            # Entrega se destino ainda precisar
            if destino in zonas_afetadas:
                nd = destino.getNecessidade()
                if nd > 0 and cap_rest > 0:
                    entregue = min(cap_rest, nd)
                    destino.setNecessidade(nd - entregue)
                    cap_rest -= entregue

        return (rota[-1], cap_rest)

    # -------------------------------------------------------------------------
    # 1) Tentar uma VIAGEM ÚNICA se houver veículo capaz de levar total_necessario
    total_necessario = sum(z.getNecessidade() for z in zonas_afetadas)
    veiculos_viaveis = [v for v in frota if v.getCapacidade() >= total_necessario]

    if veiculos_viaveis:
        # Ordenar as zonas pela distância até a base, para visita "lógica"
        # (se preferir outro critério, mude aqui)
        zonas_a_visitar = zonas_afetadas[:]
        zonas_a_visitar.sort(key=lambda z: Zona.calcular_distancia(base, z))

        veiculo_unico_encontrado = None
        rota_unica_final = []
        tipo_escolhido_unico = None

        for veic in veiculos_viaveis[:]:  # Cópia para evitar alterações diretas durante a iteração
            tipo_v = veic.getTipo()
            rota_unica = [base]
            falhou = False

            for z in zonas_a_visitar:
                # Ignorar zonas já atendidas ou duplicadas na rota
                if z in rota_unica or z.getNecessidade() <= 0:
                    continue

                sub_rota, _ = busca_rotas(rota_unica[-1], z, tipo_v)
                if sub_rota is None:
                    falhou = True
                    break

                # Evitar duplicar nó inicial se for igual
                if sub_rota[0] == rota_unica[-1]:
                    rota_unica.extend(sub_rota[1:])
                else:
                    rota_unica.extend(sub_rota)

            if falhou:
                continue  # Próximo veículo, se a sub-rota falhou

            # Avaliar se o veículo aéreo pode operar
            if tipo_v == "aereo" and (
                    (local_atual.clima_atual and local_atual.clima_atual.tipo == "tempestade") or
                    (rota_unica[-1].clima_atual and rota_unica[-1].clima_atual.tipo == "tempestade")
            ):
                #print("[Debug] Aviao nao voa na Tempestade")
                veiculos_viaveis.remove(veic)  # Remover o veículo atual
                continue  # Tentar próximo veículo

            # Se o veículo é viável
            veiculo_unico_encontrado = veic
            rota_unica_final = rota_unica
            tipo_escolhido_unico = tipo_v
            break  # Encerra o loop se um veículo válido foi encontrado

        #if not veiculo_unico_encontrado:
            #print("[Debug] Nenhum veículo encontrado para a viagem única.")

        if veiculo_unico_encontrado and rota_unica_final:
            # Faz a entrega agora, de uma só vez
            print(f"Um só veículo (ID={veiculo_unico_encontrado.getId()}, "
                  f"tipo={veiculo_unico_encontrado.getTipo()}, "
                  f"cap={veiculo_unico_encontrado.getCapacidade()}) "
                  f"pode levar {total_necessario} kg e achou rota para todas as zonas.\n")
            cap_rest = total_necessario

            # Percorrer a rota final
            percorrer_rota(rota_unica_final, veiculo_unico_encontrado, cap_rest)

            # Limpar as zonas que ficaram completas
            zonas_afetadas = limpar_zonas_completas(zonas_afetadas)

            print("\n==== ENTREGA COMPLETA (VIAGEM ÚNICA) ====")
            return caminho, tempo_total
        else:
            print("[Debug] Existe veículo com capacidade total, mas não encontrou sub-rotas "
                  "unificadas para todas as zonas sem duplicar caminho. "
                  "Seguindo fluxo padrão.\n")
    else:
        print(" Nenhum veículo comporta toda a demanda. Seguindo fluxo padrão.\n")

    # -------------------------------------------------------------------------
    # 2) FLUXO PADRÃO: priorizar cada zona pela gravidade, etc.
    # -------------------------------------------------------------------------
    while True:
        zonas_afetadas = limpar_zonas_completas(zonas_afetadas)
        if not zonas_afetadas:
            break

        # Ordenar pela gravidade (desc)
        zonas_afetadas.sort(key=lambda z: z.getGravidade(), reverse=True)
        zona_prioritaria = zonas_afetadas[0]

        #print(f"\n[DEBUG] Zonas afetadas restantes: "
         #     f"{[(z.getNome(), z.getNecessidade()) for z in zonas_afetadas]}")
        #print(f"[DEBUG] Zona prioritária: {zona_prioritaria.getNome()} "
         #     f"(Gravidade: {zona_prioritaria.getGravidade()}, "
          #    f"Necessidade: {zona_prioritaria.getNecessidade()} kg)")

        melhor_rota = None
        melhor_custo = float('inf')
        veiculo_escolhido = None
        capacidade_restante = 0.0

        # Se está na base, escolhe veículo e rota
        if local_atual == base:
            print("\n==== TROCA DE VEÍCULO NA BASE ====")
            for tipo_v in ["terrestre", "aereo", "aquatico"]:
                if tipo_v == "aereo":
                    if (local_atual.clima_atual and local_atual.clima_atual.tipo == "tempestade") or \
                            (zona_prioritaria.clima_atual and zona_prioritaria.clima_atual.tipo == "tempestade"):
                        #print("[Debug] Aviao nao voa na Tempestade")
                        continue  # Ignorar o tipo "aereo" em condições de tempestade
                rota_temp, custo_temp = busca_rotas(base, zona_prioritaria, tipo_v)
                veics = [v for v in frota if v.getTipo() == tipo_v]

                if rota_temp is not None and veics and custo_temp < melhor_custo:
                    melhor_rota = rota_temp
                    melhor_custo = custo_temp
                    veiculo_escolhido = max(veics, key=lambda v: v.getCapacidade())

            if not veiculo_escolhido or melhor_rota is None:
                print(f"[ERRO] Nenhum veículo/rota para {zona_prioritaria.getNome()}. "
                      f"Removendo zona da lista (inacessível).")
                zonas_afetadas.remove(zona_prioritaria)
                continue

            # Calcular necessidade do caminho
            zonas_no_caminho = [z for z in melhor_rota if z in zonas_afetadas and z != base]
            demanda_rota = sum(z.getNecessidade() for z in zonas_no_caminho)
            capacidade_restante = min(veiculo_escolhido.getCapacidade(), demanda_rota)

            print(f"Veículo escolhido: {veiculo_escolhido.getId()} "
                  f"(tipo={veiculo_escolhido.getTipo()}, cap={veiculo_escolhido.getCapacidade()})")
            print(f"Rota de ida: {[z.getNome() for z in melhor_rota]}")
            print(f"Necessidade no caminho = {demanda_rota} kg, "
                  f"Carregando {capacidade_restante} kg.\n")

        else:
            # Se não está na base, tenta rota pro zona_prioritaria com o veículo atual
            if veiculo_escolhido:
                rota_temp, custo_temp = busca_rotas(local_atual, zona_prioritaria, veiculo_escolhido.getTipo())
                if rota_temp is not None and custo_temp < melhor_custo:
                    melhor_rota = rota_temp
                    melhor_custo = custo_temp

        if melhor_rota is None:
            print(f"Não há rota para {zona_prioritaria.getNome()}. Tentando voltar à base.")
            if not veiculo_escolhido:
                print("[ERRO] Sem veículo definido. Encerrando.")
                break
            rota_base, custo_base = busca_rotas(local_atual, base, veiculo_escolhido.getTipo())
            if rota_base is None:
                print("[ERRO] Nem rota de volta à base. Encerrando.")
                break
            local_atual, capacidade_restante = percorrer_rota(rota_base, veiculo_escolhido, capacidade_restante)
            # Marcar zona_prioritaria como inacessível
            zonas_afetadas.remove(zona_prioritaria)
            continue

        # Percorrer a melhor_rota (ida)
        local_atual, capacidade_restante = percorrer_rota(melhor_rota, veiculo_escolhido, capacidade_restante)

        # Se acabou tudo, encerra
        zonas_afetadas = limpar_zonas_completas(zonas_afetadas)
        if not zonas_afetadas:
            print(f"Todas as entregas concluídas. Final em {local_atual.getNome()}.")
            break

        # Voltar à base para reabastecer/trocar veículo
        if local_atual != base:
            rota_base, cbase = busca_rotas(local_atual, base, veiculo_escolhido.getTipo())
            if rota_base is None:
                print("[ERRO] Não há rota de volta à base. Encerrando.")
                break
            local_atual, capacidade_restante = percorrer_rota(rota_base, veiculo_escolhido, capacidade_restante)
            #print(f"[DEBUG] Retornou à base: {base.getNome()}")

    print("\n==== ENTREGA COMPLETA ====")
    print(f"Caminho percorrido: {', '.join([z.getNome() for z in caminho])}")
    print(f"Tempo total de operação: {tempo_total:.2f} horas.")
    return caminho, tempo_total

def main():
    g = Graph()
    zonas = Zona.from_json("../../data/zonasBig.json")
    frota = Veiculo.from_json("../../data/veiculos.json")

    # Solicitar input do usuário para o número de entregas
    while True:
        try:
            num_entregas = int(input("Quantas entregas queres fazer? (1 a 3): "))
            if 1 <= num_entregas <= 3:
                break
            else:
                print("Por favor, escolha um número entre 1 e 3.")
        except ValueError:
            print("Entrada inválida! Digite um número.")

    print(f"Você escolheu fazer {num_entregas} entregas.")

    # Selecionar o algoritmo de busca
    algoritmo_selecionado = escolher_algoritmo()
    print(f"Algoritmo selecionado: {algoritmo_selecionado}")

    # Montar o grafo a partir das conexões de cada zona
    for zona in zonas:
        for conexao in zona.conexoes:
            destino_nome = conexao["destino"]
            destino = next((z for z in zonas if z.getNome() == destino_nome), None)
            if destino:
                distancia = Zona.calcular_distancia(zona, destino)
                g.add_edge(zona, destino, distancia)

    atualizar_clima_para_zonas(zonas)
    zonas_afetadas = escolher_zonas_afetadas(zonas, num_entregas)
    # Encontrar a zona base
    base = next((z for z in zonas if z.getisBase()), None)
    Zona.atribuir_deadline_por_distancia(zonas_afetadas, base)

    # Exemplo: imprime as zonas afetadas
    for z in zonas_afetadas:
        print(
            f"{z.getNome()} -> Gravidade {z.getGravidade()}, "
            f"Suprimentos = {Zona.calcular_suprimentos_necessarios(z.getGravidade())} kg"
            f" Deadline = {z.getDeadline():.2f}h"
        )

    # Chama o gerenciador de entregas

    g.inicializar_heuristicas()
    g.atualizar_heuristica_Gravidade_Distancia(zonas_afetadas, base)

    rota, tempo_total = gerenciar_entregas(base, zonas_afetadas, g, frota, algoritmo_selecionado)

    

    print(f"\nRota planejada: {[z.getNome() for z in rota]}")
    print(f"Tempo total gasto: {tempo_total:.2f} horas")

if __name__ == "__main__":
    main()