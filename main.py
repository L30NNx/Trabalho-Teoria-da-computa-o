import sys
from automatos import AFD, AFND, converter_afnd_para_afd, minimizar_afd
from gramaticas import Gramatica

def menu():
    print("\n" + "="*40)
    print("PROJETO TEORIA DA COMPUTAÇÃO - MENU")
    print("="*40)
    print("1. Testar um AFD (Requisitos 1 e 2)")
    print("2. Converter AFND para AFD (Requisitos 3 e 4)")
    print("3. Minimizar um AFD (Requisito 5)")
    print("4. Analisar e Simplificar Gramática (Req 6, 7 e 8)")
    print("5. Gerar Árvore de Derivação (Requisito 9)")
    print("6. Gerar Pseudocódigo do Reconhecedor (Requisito 10)") # <- Nova opção
    print("0. Sair")
    return input("Escolha uma opção: ")

def executar_teste_afd():
    print("\n--- TESTE DE AFD (Exemplo Fixo) ---")
    print("Autômato: Aceita número par de 'a's")
    
    # Criando o objeto usando a classe importada
    meu_afd = AFD(
        estados=['q0', 'q1'],
        alfabeto=['a', 'b'],
        transicoes={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q0', 'b': 'q1'}
        },
        estado_inicial='q0',
        estados_finais=['q0']
    )
    
    palavra = input("Digite a palavra para testar: ")
    meu_afd.validar_palavra(palavra)

def executar_conversao_afnd():
    print("\n--- CONVERSÃO AFND -> AFD ---")
    print("Autômato Original: Aceita termina com 'ab'")
    
    # Criando AFND
    meu_afnd = AFND(
        estados=['q0', 'q1', 'q2'],
        alfabeto=['a', 'b'],
        transicoes={
            'q0': {'a': ['q0', 'q1'], 'b': ['q0']}, # Não-determinismo aqui
            'q1': {'b': ['q2']},
            'q2': {}
        },
        estado_inicial='q0',
        estados_finais=['q2']
    )
    
    # Realiza a conversão chamando a função do outro arquivo
    afd_gerado = converter_afnd_para_afd(meu_afnd)
    
    print("\n--- Testando o AFD Gerado ---")
    palavra = input("Digite uma palavra para o AFD convertido validar: ")
    afd_gerado.validar_palavra(palavra)

def executar_minimizacao():
    print("\n--- MINIMIZAÇÃO DE AFD ---")
    print("Vamos usar um AFD que possui estados redundantes.")
    
    afd_inchado = AFD(
        estados=['q0', 'q1', 'q2', 'q3'],
        alfabeto=['a', 'b'],
        transicoes={
            'q0': {'a': 'q1', 'b': 'q2'},
            'q1': {'a': 'q1', 'b': 'q3'},
            'q2': {'a': 'q2', 'b': 'q3'}, 
            'q3': {'a': 'q3', 'b': 'q3'}
        },
        estado_inicial='q0',
        estados_finais=['q3']
    )
    

    afd_minimo = minimizar_afd(afd_inchado)
    
    print("\n--- Validando palavra no AFD Mínimo ---")
    palavra = input("Digite uma palavra para validar no novo AFD Mínimo (ex: 'ab'): ")
    afd_minimo.validar_palavra(palavra)

def executar_gramatica():
    print("\n--- ANALISANDO E SIMPLIFICANDO GRAMÁTICA ---")
    
    
    
    minha_glc = Gramatica(
        nao_terminais=['S', 'A', 'B', 'C', 'D'],
        terminais=['a', 'b', 'c', 'd'],
        producoes={
            'S': ['aA', 'B', 'C'],
            'A': ['a'],
            'B': ['b'],
            'C': ['cC'], # Infértil
            'D': ['d']   # Inalcançável
        },
        simbolo_inicial='S'
    )
    
    tipo = minha_glc.classificar_gramatica()
    
    if tipo == "GR":
        print("\nA gramática é Regular. Convertendo para AFD...")
        afd = minha_glc.converter_para_afd()
    else:
        print("\nA gramática é Livre de Contexto (GLC). Iniciando processo de Simplificação (Requisito 8)...")
        minha_glc.simplificar_glc()

def executar_arvore_derivacao():
    print("\n--- GERADOR DE ÁRVORE DE DERIVAÇÃO ---")
    print("Usaremos a gramática de parênteses balanceados (GLC):")
    print("S -> (S) | SS | ε")
    
    gramatica_parenteses = Gramatica(
        nao_terminais=['S'],
        terminais=['(', ')'],
        producoes={
            'S': ['(S)', 'SS', 'ε']
        },
        simbolo_inicial='S'
    )
    
    palavra = input("Digite uma sequência de parênteses (ex: '()' ou '(())'): ")
    gramatica_parenteses.gerar_arvore_derivacao(palavra)

def executar_gerador_pseudocodigo():
    print("\n--- GERADOR DE PSEUDOCÓDIGO ---")
    print("Usaremos uma Gramática Livre de Contexto de exemplo:")
    print("S -> aA")
    print("A -> bA | c")
    
    gramatica_exemplo = Gramatica(
        nao_terminais=['S', 'A'],
        terminais=['a', 'b', 'c'],
        producoes={
            'S': ['aA'],
            'A': ['bA', 'c']
        },
        simbolo_inicial='S'
    )
    
    gramatica_exemplo.gerar_pseudocodigo_reconhecedor()

# --- Loop Principal ---
if __name__ == "__main__":
    while True:
        opcao = menu()
        
        if opcao == '1':
            executar_teste_afd()
        elif opcao == '2':
            executar_conversao_afnd()
        elif opcao == '3':
            executar_minimizacao()
        elif opcao == '4':
            executar_gramatica() 
        elif opcao == '5':
            executar_arvore_derivacao()
        elif opcao =='6':
            executar_gerador_pseudocodigo()
        elif opcao == '0':
            print("Saindo...")
            sys.exit()
        else:
            print("Opção inválida!")