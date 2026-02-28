# Autores 
Projeto desenvolvido como parte do conceito da disciplina Teoria da Computação:

Gabriel Rosa Batista

Hisashi Muniz Kamizono

Leon Matheus Oliveira Alves

# Trabalho-Teoria-da-computa-o
O projeto está dividido em três grandes pilares: Autômatos, Gramáticas e Reconhecedores.

1. Manipulação de Autômatos (AFD e AFND)
Teste de AFD: Validação de palavras com log detalhado de cada mudança de estado.

Conversão AFND para AFD: Algoritmo que transforma o não-determinismo em uma estrutura determinista equivalente.

Minimização: Remove estados redundantes, inalcançáveis e unifica estados equivalentes para entregar o autômato mais enxuto possível.

2. Estudo de Gramáticas
Classificação: Identifica automaticamente se a gramática é Regular (GR) ou Livre de Contexto (GLC).

Simplificação de GLC: Limpeza automática de produções, removendo símbolos inférteis, inalcançáveis e produções unitárias.

Conversão GR ➔ AFD: Transforma regras de produção gramatical em um autômato funcional pronto para testes.

3. Visualização e Lógica
Árvore de Derivação: Gera uma representação visual da hierarquia de substituição de símbolos para validar uma sentença.

Gerador de Pseudocódigo: Cria a lógica de um analisador sintático descendente recursivo baseado na gramática fornecida.
