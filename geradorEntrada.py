import random
from tqdm import tqdm
from time import sleep
from math import log2
from random import choice, shuffle
from escalonador import Escalonador
# algoritmoDeEscalonamento|fraçãoDeCPU|políticaMemória|tamanhoMemória|tamanhoPáginasMolduras|percentualAlocação
# tempoCriacaoProcesso|PID|tempoDeExecução|prioridade (ou bilhetes)|qtdeMemoria|sequênciaAcessoPaginasProcesso

alg_escalonamento = {
    1: "alternanciaCircular",
    2: "prioridade",
    3: "loteria",
    4: "CFS"
}

memoryPolicy = {
    1: "local",
    2: "global"
}


if __name__ == "__main__":

    print("Bem-vindo ao gerador de arquivos de entrada para o Gerenciador de Memória!")
    print("Escolha o algoritmo de Escalonamento: 1: alternancia circular, 2: prioridade, 3: loteria, 4: CFS")
    alg = alg_escalonamento[int(input())]

    print("Informe a fracao de CPU que cada processo tera direito por vez")
    clock = int(input())

    print("Insira o tipo de política de memória: 1: local, 2: global")
    policy = memoryPolicy[int(input())]
    
    print("Informe o tamanho da memória principal (bytes): ")
    memorySize = int(input())
    assert memorySize > 512, "O tamanho da memória principal precisa ser maior que 512B!"
    assert memorySize >= 512 and log2(memorySize).is_integer(), "O tamanho da memória precisa principal ser uma potência de 2."

    print("Informe o tamanho das páginas e molduras (bytes): ")
    pageSize = int(input())
    assert pageSize < memorySize, "O tamanho da memória principal precisa ser maior que o tamanho da página."
    assert pageSize >= 512 and log2(pageSize).is_integer(), "O tamanho da página precisa ser maior ou igual a 512B e precisa ser uma potência de 2."

    print("Informe o percentual máximo que cada processo terá na memória principal: ")
    maxMemoryAllocationPercent = int(input().replace("%","")) / 100
    assert 0.01 <= maxMemoryAllocationPercent < 1, "A porcentagem de alocação máxima da memória é compreendida entre 1 e 100." 

    print("Informe o numero de processos a serem criados")
    numProcessos = int(input())
    
    out = open("entradaGerenciador.txt", 'w')

    out.write(f"{alg}|{clock}|{policy}|{memorySize}|{pageSize}|{maxMemoryAllocationPercent}\n")
    
    print("\nCriando Processos...")
    for i in tqdm(range(0, numProcessos)):
        sleep(0.1)
        prioridade = random.randrange(1, 100)

        expoente = int(log2(pageSize)) # ex 512 -> 9
        memoryAlloc = 2 ** random.randint((expoente + 1), expoente + 3) # ex 2 ** (10  -------  12) = (1024 ------- 4096)
        numberOfPages = int(memoryAlloc / pageSize) # ex 2048 / 512 = 4 pages

        tempo = random.randrange(numberOfPages, numberOfPages + int(numberOfPages * 0.5)) * clock # ex: (4 times ----- 6 times)

        pageAccessSequence = [x for x in range(1, numberOfPages + 1)] # ex: (1, 2, 3, 4)
        pageAccessSequence.extend([random.choice(pageAccessSequence) for _ in range(tempo - numberOfPages)]) 
        shuffle(pageAccessSequence) # ex: (1,2,1,3,4,1)


        out.write(f"{i}|{i}|{tempo}|{prioridade}|{memoryAlloc}|{pageAccessSequence}\n")

    out.close()