# Classe grafo para representaçao de grafos,
import math
from queue import Queue
from zona import Zona

import networkx as nx  # biblioteca de tratamento de grafos necessária para desnhar graficamente o grafo
import matplotlib.pyplot as plt  # idem


class Graph:
    def __init__(self, directed=False):
        self.m_nodes = []
        self.m_directed = directed
        self.m_graph = {}  # dicionario para armazenar os nodos e arestas
        self.m_h = {}  # dicionario para posterirmente armazenar as heuristicas para cada nodo -> pesquisa informada

    #############
    #    escrever o grafo como string
    #############
    def __str__(self):
        out = ""
        for key in self.m_graph.keys():
            out = out + "zona" + str(key) + ": " + str(self.m_graph[key]) + "\n"
        return out

    ################################
    #   encontrar nodo pelo nome
    ################################

    def get_node_by_name(self, zona):
        for node in self.m_nodes:
            print(node) # ?!
            if node.getNome() == zona.getNome():
                return node
        return None

    ##############################3
    #   imprimir arestas
    ############################333333

    def imprime_aresta(self):
        listaA = ""
        lista = self.m_graph.keys()
        for nodo in lista:
            for (nodo2, custo) in self.m_graph[nodo]:
                listaA = listaA + nodo.getNome() + " ->" + nodo2.getNome() + " custo:" + str(custo) + "\n"
        return listaA

    ################
    #   adicionar   aresta no grafo
    ######################

    def add_edge(self, zona1, zona2, peso):

        if zona1 not in self.m_nodes:
            self.m_nodes.append(zona1)
            self.m_graph[zona1] = []

        if zona2 not in self.m_nodes:
            self.m_nodes.append(zona2)
            self.m_graph[zona2] = []

        self.m_graph[zona1].append((zona2, peso))

        if not self.m_directed:
            self.m_graph[zona2].append((zona1, peso))


    #############################
    # devolver nodos
    ##########################

    def getNodes(self):
        return self.m_nodes

    #######################
    #    devolver o custo de uma aresta
    ##############3

    def get_arc_cost(self, zona1, zona2):
        custoT = math.inf
        a = self.m_graph[zona1]  # lista de arestas para aquele nodo
        for (nodo, custo) in a:
            if nodo == zona2:
                custoT = custo

        return custoT

    ##############################
    #  dado um caminho calcula o seu custo
    ###############################

    def calcula_custo(self, caminho):
        # caminho é uma lista de nodos
        teste = caminho
        custo = 0
        i = 0
        while i + 1 < len(teste):
            custo = custo + self.get_arc_cost(teste[i], teste[i + 1])
            # print(teste[i])
            i = i + 1
        return custo

    ################################################################################
    #     procura DFS
    ####################################################################################

    def procura_DFS(self, start: Zona, end, path=[], visited=set()):
        path.append(start)
        visited.add(start)

        if start == end:
            # calcular o custo do caminho funçao calcula custo.
            custoT = self.calcula_custo(path)
            return (path, custoT)
        for (adjacente, peso) in self.m_graph[start]:
            if adjacente not in visited:
                resultado = self.procura_DFS(adjacente, end, path, visited)
                if resultado is not None:
                    return resultado
        path.pop()  # se nao encontra remover o que está no caminho
        return None

    #####################################################
    # Procura BFS
    ######################################################
    def procura_BFS(self, start, end):
       from queue import Queue

       visited = set()  # Zonas visitadas
       fila = Queue()  # Fila de busca
       fila.put(start)

       parent = {start: None}  # Rastreia o caminho para reconstrução
       path_found = False

       while not fila.empty():
           nodo_atual = fila.get()

           if nodo_atual == end:
               path_found = True
               break

           visited.add(nodo_atual)

           # Explora os vizinhos
           for (vizinho, peso) in self.m_graph[nodo_atual]:
               if vizinho not in visited and vizinho not in parent:
                   fila.put(vizinho)
                   parent[vizinho] = nodo_atual  # Define o nodo atual como pai do vizinho

       # Reconstruir o caminho
       if path_found:
           path = []
           atual = end
           while atual is not None:
               path.append(atual)
               atual = parent[atual]
           path.reverse()  # Inverte para ter o caminho do início ao fim
           custo_total = self.calcula_custo(path)  # Calcula o custo total do caminho
           return path, custo_total

       return None, None  # Caminho não encontrado

    ####################
    # funçãop  getneighbours, devolve vizinhos de um nó
    ##############################

    def getNeighbours(self, nodo):
        lista = []
        for (adjacente, peso) in self.m_graph[nodo]:
            lista.append((adjacente, peso))
        return lista

    ###########################
    # desenha grafo  modo grafico
    #########################

    def desenha(self):
        ##criar lista de vertices
        lista_v = self.m_nodes
        lista_a = []
        g = nx.Graph()
        for nodo in lista_v:
            n = nodo.getNome()
            g.add_node(n)
            for (adjacente, peso) in self.m_graph[n]:
                lista = (n, adjacente)
                # lista_a.append(lista)
                g.add_edge(n, adjacente, weight=peso)

        pos = nx.spring_layout(g)
        nx.draw_networkx(g, pos, with_labels=True, font_weight='bold')
        labels = nx.get_edge_attributes(g, 'weight')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)

        plt.draw()
        plt.show()

    ####################################33
    #    add_heuristica   -> define heuristica para cada nodo 1 por defeito....
    ################################3

    def add_heuristica(self, n, estima):
        n1 = Node(n)
        if n1 in self.m_nodes:
            self.m_h[n] = estima

    ##########################################
    #    A*
    ##########################################

    def procura_aStar(self, start, end):
        # open_list é uma lista de nós que foram visitados, mas cujos vizinhos não foram inspeccionados, começa com o nó inicial
        # closed_list é uma lista de nós que foram visitados e cujos os vizinhos foram inspeccionados
        open_list = {start}
        closed_list = set([])

        # g contém as distâncias atuais de start_node para todos os outros nós
        g = {}

        g[start] = 0

        # parents contém um mapa de adjacência de todos os nós
        parents = {}
        parents[start] = start

        while len(open_list) > 0:
            n = None

            # encontrar um nó com o valor mais baixo de f() - função de avaliação
            for v in open_list:
                if n == None or g[v] + self.m_h[v] < g[n] + self.m_h[n]:
                    n = v

            if n == None:
                return None

            # se o nó atual for o stop_node, então começamos a reconstruir o caminho do mesmo até ao start_node
            if n == end:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start)

                reconst_path.reverse()

                return (reconst_path, self.calcula_custo(reconst_path))

            # para todos os vizinhos do nó atual
            for (m, weight) in self.getNeighbours(n):
                # se o nó atual não estiver em open_list e closed_list, adicione-se a open_list
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight

                else:
                    if g[m] > g[n] + weight:
                        g[m] = g[n] + weight
                        parents[m] = n

                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)

            # remova n da open_list e adicione-o close_list porque todos os seus vizinhos foram inspecionados
            open_list.remove(n)
            closed_list.add(n)

        return None



    ##########################################
    #    A* com type filter
    ##########################################
    def procura_aStar_typeFilter(self, start, end, tipo_desejado):

        open_list = {start}
        closed_list = set()

        g = {start: 0}     # custo acumulado do start até o nodo
        parents = {start: start}

        while open_list:
            # A) Escolher nodo n com menor f(n) = g[n] + m_h[n]
            n = None
            for v in open_list:
                if n is None or (g[v] + self.m_h[v]) < (g[n] + self.m_h[n]):
                    n = v

            if n is None:
                # Falhou
                return (None, None)

            # B) Se n == end, reconstruir caminho
            if n == end:
                reconst_path = []
                cur = n
                while parents[cur] != cur:
                    reconst_path.append(cur)
                    cur = parents[cur]
                reconst_path.append(start)
                reconst_path.reverse()

                custo_total = self.calcula_custo(reconst_path)
                return (reconst_path, custo_total)

            # Tira n de open_list e bota em closed_list
            open_list.remove(n)
            closed_list.add(n)

            # C) Expandir vizinhos, MAS SÓ se a conexão for tipo_desejado
            for (m, dist) in self.m_graph[n]:
                # ### FILTRO ###
                # Precisamos verificar se n->m tem tipo == tipo_desejado
                # Então olhamos "n.conexoes" e vemos se há c["destino"] == m.nome and c["tipo"] == tipo_desejado
                eh_compativel = False
                for c in n.conexoes:
                    if c["destino"] == m.getNome() and c["tipo"] == tipo_desejado:
                        eh_compativel = True
                        break
                if not eh_compativel:
                    continue  # ignorar este vizinho

                # se m não estiver em closed_list nem open_list, adiciona
                # ou se encontramos um caminho melhor (menor g[m])
                if m not in closed_list and m not in open_list:
                    g[m] = g[n] + dist
                    parents[m] = n
                    open_list.add(m)
                else:
                    custo_atual_m = g.get(m, float('inf'))
                    novo_custo = g[n] + dist
                    if novo_custo < custo_atual_m:
                        g[m] = novo_custo
                        parents[m] = n
                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)

        # Se saímos do while sem retornar, não há caminho
        return (None, None)

    ###################################3
    # devolve heuristica do nodo
    ####################################

    def getH(self, nodo):
        if nodo not in self.m_h.keys():
            return 1000
        else:
            return (self.m_h[nodo])


    ##########################################
    #   Greedy
    ##########################################


    def greedy(self, start, end):

        open_list = set([start])
        closed_list = set([])

        # parents é um dicionário que mantém o antecessor de um nodo
        # começa com start
        parents = {}
        parents[start] = start

        while len(open_list) > 0:
            n = None

            # encontra nodo com a menor heuristica
            for v in open_list:
                if n == None or self.m_h[v] < self.m_h[n]:
                    n = v

            if n == None:
                return None

            # se o nodo corrente é o destino
            # reconstruir o caminho a partir desse nodo até ao start
            # seguindo o antecessor
            if n == end:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start)

                reconst_path.reverse()

                return (reconst_path, self.calcula_custo(reconst_path))
            # para todos os vizinhos  do nodo corrente

            for (m, weight) in self.getNeighbours(n):
                # Se o nodo corrente nao esta na open nem na closed list
                # adiciona-lo à open_list e marcar o antecessor
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n


            # remover n da open_list e adiciona-lo à closed_list
            # porque todos os seus vizinhos foram inspecionados
            open_list.remove(n)
            closed_list.add(n)

        return None


    # Em Graph.py
    def imprimir_grafo(self):
        """
        Imprime as conexões do grafo no formato {zona: [(vizinho, peso)]}.
        """
        for zona, conexoes in self.m_graph.items():
            print(f"{zona.getNome()}: {[(vizinho.getNome(), peso) for vizinho, peso in conexoes]}")

    def inicializar_heuristicas(self):
        for zona_no_grafo in self.m_nodes:
            self.m_h[zona_no_grafo] = 1000  # Ou valor padrão alto


 ##########################################
    #    BFS com filtro de tipo
    ##########################################
    def procura_BFS_typeFilter(self, start, end, tipo_desejado):
        from queue import Queue

        visited = set()
        fila = Queue()
        fila.put(start)

        parent = {start: None}
        path_found = False

        while not fila.empty():
            nodo_atual = fila.get()

            if nodo_atual == end:
                path_found = True
                break

            visited.add(nodo_atual)

            # Explora os vizinhos que são compatíveis com o tipo desejado
            for (vizinho, peso) in self.m_graph[nodo_atual]:
                # Verificar se a conexão é compatível com o tipo desejado
                eh_compativel = False
                for c in nodo_atual.conexoes:
                    if c["destino"] == vizinho.getNome() and c["tipo"] == tipo_desejado:
                        eh_compativel = True
                        break
                if not eh_compativel:
                    continue  # Ignorar este vizinho

                if vizinho not in visited and vizinho not in parent:
                    fila.put(vizinho)
                    parent[vizinho] = nodo_atual

        if path_found:
            path = []
            atual = end
            while atual is not None:
                path.append(atual)
                atual = parent[atual]
            path.reverse()
            custo_total = self.calcula_custo(path)
            return path, custo_total

        return None, None

    ##########################################
    #    DFS com filtro de tipo
    ##########################################
    def procura_DFS_typeFilter(self, start, end, tipo_desejado, path=None, visited=None):
        if path is None:
            path = []
        if visited is None:
            visited = set()

        path.append(start)
        visited.add(start)

        if start == end:
            custoT = self.calcula_custo(path)
            return (path, custoT)

        for (adjacente, peso) in self.m_graph[start]:
            # Verificar se a conexão é compatível com o tipo desejado
            eh_compativel = False
            for c in start.conexoes:
                if c["destino"] == adjacente.getNome() and c["tipo"] == tipo_desejado:
                    eh_compativel = True
                    break
            if not eh_compativel:
                continue  # Ignorar este vizinho

            if adjacente not in visited:
                resultado = self.procura_DFS_typeFilter(adjacente, end, tipo_desejado, path, visited)
                if resultado is not None:
                    return resultado

        path.pop()
        return None

    ##########################################
    #    Greedy com filtro de tipo
    ##########################################
    def greedy_typeFilter(self, start, end, tipo_desejado):
        open_list = set([start])
        closed_list = set()

        parents = {}
        parents[start] = start

        while open_list:
            n = None
            for v in open_list:
                if n is None or self.m_h[v] < self.m_h[n]:
                    n = v

            if n is None:
                return None, None

            if n == end:
                path = []
                while parents[n] != n:
                    path.append(n)
                    n = parents[n]
                path.append(start)
                path.reverse()
                custo_total = self.calcula_custo(path)
                return (path, custo_total)

            open_list.remove(n)
            closed_list.add(n)

            for (m, peso) in self.m_graph[n]:
                # Verificar se a conexão é compatível com o tipo desejado
                eh_compativel = False
                for c in n.conexoes:
                    if c["destino"] == m.getNome() and c["tipo"] == tipo_desejado:
                        eh_compativel = True
                        break
                if not eh_compativel:
                    continue  # Ignorar este vizinho

                if m not in closed_list and m not in open_list:
                    open_list.add(m)
                    parents[m] = n

        return None, None

    def atualizar_heuristica_Gravidade_Distancia(self, zonas_afetadas, destino):
        for zona in zonas_afetadas:
            distancia = Zona.calcular_distancia(zona, destino)
            gravidade = zona.getGravidade() or 0
            self.m_h[zona] = gravidade * 10 - distancia

    def atualizar_heuristica_tempo_viagem(self, zonas_afetadas, destino, frota):
        """
        Atualiza heurísticas baseadas no tempo de viagem estimado.
        """
        print("\n[DEBUG] --- Heurística: Tempo de Viagem ---")
        # Assume uma velocidade média do transporte terrestre como fallback
        velocidade_media = max(v.getVelocidade() for v in frota if v.getTipo() == "terrestre") or 50
        for zona in zonas_afetadas:
            distancia = Zona.calcular_distancia(zona, destino)
            tempo_estimado = distancia / velocidade_media
            self.m_h[zona] = tempo_estimado

            print(f"   Zona '{zona.getNome()}': dist={distancia:.2f}, "
                  f"velocidade_media={velocidade_media} km/h, h={tempo_estimado:.2f}")
        print("[DEBUG] --- Fim da Heurística: Tempo de Viagem ---")

    def atualizar_heuristica_populacao(self, zonas_afetadas, destino):
        """
        Atualiza heurísticas priorizando zonas com maior população.
        """
        print("\n[DEBUG] --- Heurística: População ---")
        for zona in zonas_afetadas:
            distancia = Zona.calcular_distancia(zona, destino)
            populacao = zona.getPopulacao() or 1  # Evitar divisão por zero
            valor_h = populacao / distancia
            self.m_h[zona] = valor_h

            print(f"   Zona '{zona.getNome()}': populacao={populacao}, "
                  f"dist={distancia:.2f}, h={valor_h:.4f}")
        print("[DEBUG] --- Fim da Heurística: População ---")

    def atualizar_heuristica_risco_operacional(self, zonas_afetadas, destino):
        """
        Atualiza heurísticas com base no risco operacional, considerando gravidade, distância e condições climáticas.
        """
        print("\n[DEBUG] --- Heurística: Risco Operacional ---")
        for zona in zonas_afetadas:
            distancia = Zona.calcular_distancia(zona, destino)
            gravidade = zona.getGravidade() or 1  # Assumir gravidade mínima de 1 para cálculo
            clima_impacto = zona.clima_atual.impacto if zona.clima_atual else 1.0
            risco = distancia * clima_impacto
            valor_h = (gravidade * zona.getPopulacao()) / risco if risco != 0 else 0
            self.m_h[zona] = valor_h

            print(f"   Zona '{zona.getNome()}': gravidade={gravidade}, "
                  f"pop={zona.getPopulacao()}, clima_impacto={clima_impacto}, "
                  f"dist={distancia:.2f}, risco={risco:.2f}, h={valor_h:.4f}")
        print("[DEBUG] --- Fim da Heurística: Risco Operacional ---")