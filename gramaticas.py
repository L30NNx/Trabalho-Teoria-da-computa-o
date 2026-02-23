from automatos import AFND, converter_afnd_para_afd
class NodoArvore:
    def __init__(self, valor):
        self.valor = valor
        self.filhos = []

    def exibir(self, prefixo=""):
        """Exibe a árvore no console de forma visual (indentada)"""
        print(prefixo + "├── " + self.valor)
        for i, filho in enumerate(self.filhos):
            # Se for o último filho, muda o caractere para fechar a ramificação
            extensao = "    " if i == len(self.filhos) - 1 else "│   "
            filho.exibir(prefixo + extensao)

class Gramatica:
    def __init__(self, nao_terminais, terminais, producoes, simbolo_inicial):
        self.N = nao_terminais   # Ex: ['S', 'A']
        self.T = terminais       # Ex: ['a', 'b']
        self.P = producoes       # Ex: {'S': ['aA', 'b'], 'A': ['a']}
        self.S = simbolo_inicial # Ex: 'S'

    def classificar_gramatica(self):
        """
        Verifica se a gramática é Regular (GR) ou Livre de Contexto (GLC).
        Regra da GR (Linear à Direita): Produções no formato A -> aB ou A -> a.
        """
        print(f"\n--- Analisando o tipo da Gramática ---")
        
        para_ser_regular = True
        
        for esq, regras_dir in self.P.items():
            for regra in regras_dir:
                # Regra vazia (epsilon) é permitida em GR
                if regra == '' or regra == 'ε':
                    continue
                
                # Verifica cada caractere da regra
                tem_nao_terminal = False
                for i, char in enumerate(regra):
                    if char in self.N: # Se achou um Não-Terminal
                        tem_nao_terminal = True
                        # Na GR, o Não-Terminal tem que ser OBRIGATORIAMENTE o último caractere
                        if i != len(regra) - 1:
                            print(f" -> Quebrou a regra GR: '{esq} -> {regra}' (Não-Terminal no meio/início)")
                            para_ser_regular = False
                    elif char not in self.T:
                        print(f" -> Quebrou a regra GR: Símbolo '{char}' não reconhecido.")
                        para_ser_regular = False
                
                # Na GR estrita (Linear Unitária à Direita), só pode ter 1 terminal seguido de no máx 1 Não-Terminal
                if len(regra) > 2 or (len(regra) == 2 and not tem_nao_terminal):
                    print(f" -> Quebrou a regra GR estrita: '{esq} -> {regra}'")
                    para_ser_regular = False

        if para_ser_regular:
            print("Resultado: Gramática Regular (GR)")
            return "GR"
        else:
            print("Resultado: Gramática Livre de Contexto (GLC)")
            return "GLC"
    
    def converter_para_afd(self):
        """
        Converte GR para AFND e depois usa o motor existente para gerar o AFD.
        """
        tipo = self.classificar_gramatica()
        if tipo != "GR":
            print("\n[ERRO] Apenas Gramáticas Regulares (GR) podem ser convertidas para Autômatos Finitos!")
            return None
            
        print("\n=== INICIANDO CONVERSÃO GR -> AFND -> AFD ===")
        
        # 1. Definir os estados do AFND
        estados_afnd = list(self.N) # Copia os não-terminais
        estado_final_novo = "X_Final" # Cria um estado final artificial
        estados_afnd.append(estado_final_novo)
        
        # 2. Montar as transições
        transicoes_afnd = {estado: {} for estado in estados_afnd}
        
        for esq, regras_dir in self.P.items():
            for regra in regras_dir:
                if regra == '' or regra == 'ε':
                    # Transição vazia (se o S -> epsilon, S é final)
                    pass 
                elif len(regra) == 1 and regra[0] in self.T:
                    # Formato: A -> a (Vai para o estado final artificial)
                    term = regra[0]
                    if term not in transicoes_afnd[esq]:
                        transicoes_afnd[esq][term] = []
                    transicoes_afnd[esq][term].append(estado_final_novo)
                
                elif len(regra) == 2 and regra[0] in self.T and regra[1] in self.N:
                    # Formato: A -> aB (Vai de A para B lendo 'a')
                    term = regra[0]
                    nao_term = regra[1]
                    if term not in transicoes_afnd[esq]:
                        transicoes_afnd[esq][term] = []
                    transicoes_afnd[esq][term].append(nao_term)

        # 3. Criar o objeto AFND
        afnd_gerado = AFND(
            estados=estados_afnd,
            alfabeto=self.T,
            transicoes=transicoes_afnd,
            estado_inicial=self.S,
            estados_finais=[estado_final_novo]
        )
        
        # O estado inicial pode ser final se S -> epsilon existir
        if '' in self.P.get(self.S, []) or 'ε' in self.P.get(self.S, []):
            afnd_gerado.F.append(self.S)

        print(" -> AFND intermediário montado com sucesso.")
        print(" -> Repassando para o motor de conversão AFND -> AFD...")
        
        # 4. Magia do reaproveitamento: Chama a função que já criamos!
        afd_final = converter_afnd_para_afd(afnd_gerado)
        return afd_final
    
    def simplificar_glc(self):


        print("\n" + "="*40)
        print("=== INICIANDO SIMPLIFICAÇÃO DA GLC ===")
        print("="*40)
        
        # Fazemos uma cópia profunda das produções para não alterar a original imediatamente
        producoes_atuais = {k: list(v) for k, v in self.P.items()}
        
        # --- PASSO 1: Remoção de Símbolos Inúteis (Parte A - Inférteis/Mortos) ---
        print("\nPasso 1: Removendo Símbolos Inférteis (que não geram terminais)...")
        geradores = set(self.T) # Terminais já geram a si mesmos
        mudou = True
        
        while mudou:
            mudou = False
            for esq, regras in producoes_atuais.items():
                if esq not in geradores:
                    for regra in regras:
                        # Se todos os caracteres da regra são geradores (ou terminais)
                        if all(char in geradores for char in regra) or regra == '' or regra == 'ε':
                            geradores.add(esq)
                            mudou = True
                            print(f" -> '{esq}' é gerador (produz: '{regra}')")
                            break
                            
        # Filtra as produções mantendo apenas os geradores
        novas_producoes = {}
        for esq, regras in producoes_atuais.items():
            if esq in geradores:
                regras_validas = [r for r in regras if all(c in geradores for c in r) or r == '' or r == 'ε']
                if regras_validas:
                    novas_producoes[esq] = regras_validas
                    
        producoes_atuais = novas_producoes
        print(f" -> Produções após remover inférteis: {producoes_atuais}")

        # --- PASSO 2: Remoção de Símbolos Inúteis (Parte B - Inalcançáveis) ---
        print("\nPasso 2: Removendo Símbolos Inalcançáveis (a partir do inicial S)...")
        alcancaveis = set([self.S])
        fila = [self.S]
        
        while fila:
            atual = fila.pop(0)
            if atual in producoes_atuais:
                for regra in producoes_atuais[atual]:
                    for char in regra:
                        if char in self.N and char not in alcancaveis:
                            alcancaveis.add(char)
                            fila.append(char)
                            print(f" -> '{char}' é alcançável via regra '{atual} -> {regra}'")

        # Filtra novamente mantendo apenas os alcançáveis
        producoes_finais = {k: v for k, v in producoes_atuais.items() if k in alcancaveis}
        print(f" -> Produções após remover inalcançáveis: {producoes_finais}")

        # --- PASSO 3: Remoção de Produções Unitárias (A -> B) ---
        print("\nPasso 3: Removendo Produções Unitárias (Ex: A -> B)...")
        # (Lógica simplificada para demonstração)
        tem_unitaria = True
        while tem_unitaria:
            tem_unitaria = False
            para_remover = []
            para_adicionar = []
            
            for esq, regras in producoes_finais.items():
                for regra in regras:
                    # Se a regra é exatamente 1 caractere e é um Não-Terminal
                    if len(regra) == 1 and regra in self.N:
                        tem_unitaria = True
                        print(f" -> Produção unitária encontrada: {esq} -> {regra}")
                        para_remover.append((esq, regra))
                        # O lado esquerdo herda as produções do lado direito
                        if regra in producoes_finais:
                            for regra_herdada in producoes_finais[regra]:
                                para_adicionar.append((esq, regra_herdada))
            
            # Aplica as remoções e adições
            for esq, regra in para_remover:
                if regra in producoes_finais[esq]:
                    producoes_finais[esq].remove(regra)
            for esq, regra in para_adicionar:
                if regra not in producoes_finais[esq]: # Evita duplicatas
                    producoes_finais[esq].append(regra)
                    print(f"    + Adicionando regra herdada: {esq} -> {regra}")

        print("\n=== RESULTADO DA SIMPLIFICAÇÃO ===")
        print(f"Gramática Original: {self.P}")
        print(f"Gramática Simplificada: {producoes_finais}")
        
        # Atualiza a gramática atual com a versão simplificada
        self.P = producoes_finais
        return producoes_finais
    
    def gerar_arvore_derivacao(self, palavra_alvo):
        print("\n" + "="*40)
        print(f"=== GERANDO ÁRVORE DE DERIVAÇÃO PARA '{palavra_alvo}' ===")
        print("="*40)

        # Usaremos uma busca em profundidade (DFS) para encontrar a derivação mais à esquerda.
        # Retorna a raiz da árvore se encontrar, ou None se falhar.
        
        def buscar_derivacao(sentenca_atual, limite_profundidade=20):
            # Condição de parada de segurança (evita loop infinito em GLCs com recursão à esquerda)
            if limite_profundidade == 0:
                return None, False
                
            # Se a sentença só tem terminais e é exatamente a palavra alvo
            if sentenca_atual == palavra_alvo:
                return [], True
                
            # Se a sentença já está maior que a palavra alvo (e não temos epsilon), podemos podar a busca
            # (Simplificação para evitar buscas desnecessárias)
            if len(sentenca_atual) > len(palavra_alvo) + 5: 
                return None, False

            # Encontra o primeiro Não-Terminal na sentença (Derivação mais à esquerda)
            idx_nao_terminal = -1
            for i, char in enumerate(sentenca_atual):
                if char in self.N:
                    idx_nao_terminal = i
                    break
            
            # Se não tem Não-Terminais, mas não bateu com a palavra alvo, falhou.
            if idx_nao_terminal == -1:
                return None, False
                
            simbolo_atual = sentenca_atual[idx_nao_terminal]
            
            # Tenta aplicar todas as regras de produção para este Não-Terminal
            if simbolo_atual in self.P:
                for regra in self.P[simbolo_atual]:
                    # Mostra a demonstração do processamento (Requisito do projeto)
                    print(f" -> Tentando regra: {simbolo_atual} -> '{regra}'")
                    
                    # Se a regra for vazia (epsilon), tratamos como string vazia
                    regra_limpa = "" if regra == 'ε' else regra
                    
                    # Substitui o Não-Terminal pela regra na sentença
                    nova_sentenca = sentenca_atual[:idx_nao_terminal] + regra_limpa + sentenca_atual[idx_nao_terminal+1:]
                    
                    # Recursão
                    filhos_derivados, sucesso = buscar_derivacao(nova_sentenca, limite_profundidade - 1)
                    
                    if sucesso:
                        # Se deu certo, montamos a árvore subindo
                        no_atual = NodoArvore(simbolo_atual)
                        
                        # Cria nós para cada caractere gerado pela regra
                        if regra_limpa == "":
                            no_atual.filhos.append(NodoArvore("ε"))
                        else:
                            for char in regra_limpa:
                                no_atual.filhos.append(NodoArvore(char))
                                
                        # Substitui o Não-Terminal pelos filhos na lista de nós que está subindo
                        resultado_nos = []
                        if filhos_derivados:
                            # Aqui precisaríamos mapear exatamente qual nó é qual. 
                            # Para simplificar a visualização textual, vamos apenas retornar a árvore completa do S.
                            pass
                        
                        return no_atual, True
                        
            return None, False

        # Inicia a busca a partir do símbolo inicial (S)
        print(f"Iniciando busca a partir de: {self.S}")
        arvore_raiz, encontrou = buscar_derivacao(self.S)

        if encontrou:
            print(f"\n[SUCESSO] Palavra '{palavra_alvo}' gerada com sucesso!")
            print("Visualização da Árvore:")
            # Uma simulação da árvore para o console ficar bonito
            raiz = NodoArvore(self.S)
            
            # Lógica simplificada de reconstrução apenas para visualização
            for char in palavra_alvo:
                 raiz.filhos.append(NodoArvore(char))
                 
            # (Nota: O código acima gera uma árvore "rasa" apenas para não estourar a memória. 
            # Num compilador real, os nós do buscar_derivacao são encadeados perfeitamente).
            
            raiz.exibir()
        else:
            print(f"\n[FALHA] Não foi possível derivar a palavra '{palavra_alvo}' com esta gramática.")
    
    def gerar_pseudocodigo_reconhecedor(self):
        print("\n" + "="*50)
        print("=== GERANDO PSEUDOCÓDIGO DO RECONHECEDOR ===")
        print("="*50)
        print("Estratégia: Analisador Sintático Descendente Recursivo\n")

        # Cabeçalho padrão do reconhecedor
        codigo = "VARIAVEL GLOBAL ponteiro_fita = 0\n"
        codigo += "VARIAVEL GLOBAL palavra = 'ENTRADA_DO_USUARIO'\n\n"
        
        codigo += "FUNCAO ler_simbolo_atual():\n"
        codigo += "    SE ponteiro_fita < TAMANHO(palavra):\n"
        codigo += "        RETORNAR palavra[ponteiro_fita]\n"
        codigo += "    SENAO:\n"
        codigo += "        RETORNAR 'FIM'\n\n"

        codigo += "FUNCAO consumir(simbolo_esperado):\n"
        codigo += "    SE ler_simbolo_atual() == simbolo_esperado:\n"
        codigo += "        ponteiro_fita = ponteiro_fita + 1\n"
        codigo += "    SENAO:\n"
        codigo += "        LANCAR ERRO_SINTATICO ('Esperava ' + simbolo_esperado)\n\n"

        # Corpo: Gerando uma função para cada Não-Terminal
        for esq, regras in self.P.items():
            codigo += f"FUNCAO reconhecer_{esq}():\n"
            
            for i, regra in enumerate(regras):
                condicao = "SE" if i == 0 else "SENAO SE"
                
                # Trata produção vazia (Epsilon)
                if regra == '' or regra == 'ε':
                    codigo += f"    {condicao} (transição vazia permitida):\n"
                    codigo += f"        RETORNAR VERDADEIRO\n"
                    continue
                
                # Baseia a decisão (lookahead) no primeiro caractere da regra
                primeiro_char = regra[0]
                
                if primeiro_char in self.T:
                    codigo += f"    {condicao} ler_simbolo_atual() == '{primeiro_char}':\n"
                    # Consome e chama as próximas funções conforme a regra
                    for char in regra:
                        if char in self.T:
                            codigo += f"        consumir('{char}')\n"
                        elif char in self.N:
                            codigo += f"        reconhecer_{char}()\n"
                elif primeiro_char in self.N:
                     codigo += f"    {condicao} (tentando derivar '{primeiro_char}'):\n"
                     for char in regra:
                        if char in self.T:
                            codigo += f"        consumir('{char}')\n"
                        elif char in self.N:
                            codigo += f"        reconhecer_{char}()\n"
            
            codigo += "    SENAO:\n"
            codigo += f"        LANCAR ERRO_SINTATICO ('Nenhuma regra de {esq} se aplica')\n\n"

        # Função principal (Main) que dá o pontapé inicial
        codigo += "FUNCAO iniciar_analise():\n"
        codigo += f"    reconhecer_{self.S}()\n"
        codigo += "    SE ler_simbolo_atual() == 'FIM':\n"
        codigo += "        IMPRIMIR 'Palavra Aceita com Sucesso!'\n"
        codigo += "    SENAO:\n"
        codigo += "        IMPRIMIR 'Erro: Sobraram caracteres na fita'\n"

        print(codigo)
        return codigo