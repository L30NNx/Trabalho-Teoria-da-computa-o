class AFD:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_finais):
        self.Q = estados
        self.Sigma = alfabeto
        self.delta = transicoes
        self.q0 = estado_inicial
        self.F = estados_finais
    
    def validar_palavra(self, palavra):
        print(f"\n--- [AFD] Validando a palavra:  '{palavra}' ---")
        estado_atual = self.q0
        print(f"-> Estado Inicial: {estado_atual}")

        for i, simbolo in enumerate(palavra):
            if simbolo not in self.Sigma:
                print(f"[ERRO] Símbolo '{simbolo}' não pertence ao alfabeto!")
                return False
            
            if estado_atual in self.delta and simbolo in self.delta[estado_atual]:
                destino = self.delta[estado_atual][simbolo]
                print(f" [{i+1}] Lendo '{simbolo}': ({estado_atual}) --> ({destino})")
                estado_atual = destino
            else:
                print(f" [{i+1}] Lendo '{simbolo}': ({estado_atual}) ---> [Travou/Rejeitada]")
                return False

        print(f"-> Leitura finalizada no estado: {estado_atual}")
        if estado_atual in self.F:
              print("Resultado: Aprovado (Estado Final)")
              return True
        else:
            print("Resultado: Reprovado (Estado Não-Final)")
            return False  

class AFND:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_finais):
        self.Q = estados
        self.Sigma = alfabeto
        self.delta = transicoes
        self.q0 = estado_inicial
        self.F = estados_finais

# --- FUNÇÕES FICAM FORA DA CLASSE (SEM TAB NO INÍCIO) ---

def get_epsilon_closure(afnd, estados):
    pilha = list(estados)
    fecho = set(estados)
    while pilha:
        atual = pilha.pop()
        # Verifica transição vazia (string vazia '')
        if atual in afnd.delta and '' in afnd.delta[atual]:
            destinos = afnd.delta[atual]['']
            for d in destinos:
                if d not in fecho:
                    fecho.add(d)
                    pilha.append(d)
    return fecho

def converter_afnd_para_afd(afnd):
    print("\n=== INICIANDO CONVERSÃO AFND -> AFD ===")

    q0_fecho = get_epsilon_closure(afnd, {afnd.q0})
    q0_frozenset = frozenset(q0_fecho)

    mapa_nomes = {q0_frozenset: "S0"}
    fila = [q0_frozenset]

    novas_transicoes = {}
    novos_finais = []

    contador = 1
    processados = set()

    while fila:
        conjunto_atual = fila.pop(0)
        
        if conjunto_atual in processados:
            continue
            
        processados.add(conjunto_atual)
        nome_atual = mapa_nomes[conjunto_atual]

        # Verifica se é estado final
        eh_final = any(q in afnd.F for q in conjunto_atual)
        if eh_final and nome_atual not in novos_finais:
            novos_finais.append(nome_atual)

        if nome_atual not in novas_transicoes:
            novas_transicoes[nome_atual] = {}
        
        print(f"Processando Estado Composto {nome_atual}: {set(conjunto_atual)}")

        for simbolo in afnd.Sigma:
            destinos = set()
            for q in conjunto_atual:
                if q in afnd.delta and simbolo in afnd.delta[q]:
                    destinos.update(afnd.delta[q][simbolo])

            fecho_destinos = get_epsilon_closure(afnd, destinos)
            
            if not fecho_destinos:
                continue

            chave_destino = frozenset(fecho_destinos)

            if chave_destino not in mapa_nomes:
                novo_nome = f"S{contador}"
                mapa_nomes[chave_destino] = novo_nome
                contador += 1
                fila.append(chave_destino)
                print(f" ---> Novo estado descoberto via '{simbolo}': {novo_nome} {set(chave_destino)} ")

            novas_transicoes[nome_atual][simbolo] = mapa_nomes[chave_destino]
    
    print("==== CONVERSÃO CONCLUÍDA ===")

    # O RETURN DEVE FICAR FORA DO WHILE
    return AFD(
        estados=list(mapa_nomes.values()),  # Adicionei a vírgula que faltava aqui
        alfabeto=afnd.Sigma,
        transicoes=novas_transicoes,
        estado_inicial="S0",
        estados_finais=novos_finais
    )

# 5. Processo de Mimização
def minimizar_afd(afd): # 5.a.i: Verificar se AF é deterministíco
    print("\n" + "="*40)
    print("=== INICIANDO MINIMIZAÇÃO DO AFD ===")
    print("="*40)

    # 5.a.iii: Verificar estados alcançáveis a partir do estado inicial
    print("\nPasso 1: Removendo estados inalcançáveis...")
    alcancaveis = set()
    fila = [afd.q0]
    alcancaveis.add(afd.q0)
    
    while fila:
        atual = fila.pop(0)
        for simb in afd.Sigma:
            if atual in afd.delta and simb in afd.delta[atual]:
                destino = afd.delta[atual][simb]
                if destino not in alcancaveis:
                    alcancaveis.add(destino)
                    fila.append(destino)

    estados_uteis = [q for q in afd.Q if q in alcancaveis]
    finais_uteis = [q for q in afd.F if q in alcancaveis]
    print(f" -> Estados alcançáveis encontrados: {estados_uteis}")

    # 5.a.ii: Verificar se a Função de Transição é total/completa 
    print("\nPasso 2: Verificando se a função de transição é total...")
    transicoes_completas = {q: dict(afd.delta.get(q, {})) for q in estados_uteis}
    precisa_estado_erro = False

    for q in estados_uteis:
        for simb in afd.Sigma:
            if q not in afd.delta or simb not in afd.delta[q]:
                precisa_estado_erro = True
                break

    if precisa_estado_erro:
        estado_erro = "Erro" # Estado artificial (A) 
        print(f" -> Incompleta! Adicionando estado artificial '{estado_erro}'.")
        estados_uteis.append(estado_erro)
        transicoes_completas[estado_erro] = {simb: estado_erro for simb in afd.Sigma}
        
        for q in estados_uteis:
            for simb in afd.Sigma:
                if simb not in transicoes_completas.get(q, {}):
                    if q not in transicoes_completas: transicoes_completas[q] = {}
                    transicoes_completas[q][simb] = estado_erro
    else:
        print(" -> A função já é total. Nenhuma alteração necessária.")

    # 5.b: Construir a tabela de todos os pares de estados possíveis
    print("\nPasso 3: Construindo tabela de pares de estados possíveis...")
    pares = {}
    for i in range(len(estados_uteis)):
        for j in range(i + 1, len(estados_uteis)):
            pares[(estados_uteis[i], estados_uteis[j])] = False # False = Não marcados (Equivalentes)

    # 5.c: Identificar os pares de estados trivialmente não equivalentes 
    print("\nPasso 4: Marcando pares trivialmente não equivalentes (Final vs Não-Final)...")
    for p in pares:
        q1, q2 = p
        # Um é final e o outro não é
        if (q1 in finais_uteis) != (q2 in finais_uteis):
            pares[p] = True
            print(f" -> Par {p} marcado (Trivial).")

    # 5.d: Analisar pares faltantes iterativamente 
    print("\nPasso 5: Analisando pares faltantes via processo de análise...")
    mudou = True
    while mudou:
        mudou = False
        for p in pares:
            if not pares[p]: # Se o par não está marcado
                q1, q2 = p
                for simb in afd.Sigma:
                    d1 = transicoes_completas[q1][simb]
                    d2 = transicoes_completas[q2][simb]
                    
                    if d1 != d2:
                        par_destino = (d1, d2) if (d1, d2) in pares else (d2, d1)
                        if par_destino in pares and pares[par_destino]:
                            pares[p] = True
                            mudou = True
                            print(f" -> Par {p} marcado! (Com o símbolo '{simb}' eles vão para o par já marcado {par_destino}).")
                            break

    # 5.e: Unificar pares de estados equivalentes
    print("\nPasso 6: Unificando estados equivalentes...")
    equivalentes = [p for p, marcado in pares.items() if not marcado]
    
    if not equivalentes:
        print(" -> Nenhum estado equivalente encontrado. O AFD já é mínimo!")
    else:
        for p in equivalentes:
            print(f" -> Par equivalente encontrado: {p} serão unificados!")

    # Criação do dicionário de unificação (quem vira quem)
    agrupamento = {q: q for q in estados_uteis}
    for q1, q2 in equivalentes:
        grupo_base = agrupamento[q1]
        grupo_alvo = agrupamento[q2]
        for q in agrupamento:
            if agrupamento[q] == grupo_alvo:
                agrupamento[q] = grupo_base # Unifica 

    novos_estados = list(set(agrupamento.values()))
    
    # 5.f: Gerar a função de transição equivalente do AFD Mínimo
    print("\nPasso 7: Gerando função de transição do AFD Mínimo...")
    novo_q0 = agrupamento[afd.q0]
    novos_finais = list(set([agrupamento[q] for q in finais_uteis]))
    
    novas_transicoes = {}
    for q in novos_estados:
        novas_transicoes[q] = {}
        # Pega um representante qualquer que forma este grupo
        representante = [orig for orig, novo in agrupamento.items() if novo == q][0]
        for simb in afd.Sigma:
            dest_original = transicoes_completas[representante][simb]
            novas_transicoes[q][simb] = agrupamento[dest_original]

    print(f"\n=== RESULTADO DO AFD MÍNIMO ===")
    print(f" -> Novos Estados: {novos_estados}")
    print(f" -> Estado Inicial: {novo_q0}")
    print(f" -> Estados Finais: {novos_finais}")
    
    # Retorna o novo AFD (permitindo a validação de palavras a partir do AFD Mínimo) 
    return AFD(novos_estados, afd.Sigma, novas_transicoes, novo_q0, novos_finais)
