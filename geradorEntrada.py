import random
from tqdm import tqdm
from time import sleep
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

    print("Informe o tamanho das páginas e molduras (bytes): ")
    pageSize = int(input())
    assert pageSize < memorySize, "O tamanho da memória principal precisa ser maior que o tamanho da página."
    assert pageSize >= 512 and pageSize ** (1 /2) % 1 == 0, "O tamanho da página precisa ser maior que 512B e precisa ser uma potência de 2."

    print("Informe o percentual máximo que cada processo terá na memória principal: ")
    maxMemoryAllocationPercent = int(input().replace("%","")) / 100
    assert 0.01 <= maxMemoryAllocationPercent < 1, "A porcentagem de alocação máxima da memória é compreendida entre 1 e 100." 

    print("Informe o numero de processos a serem criados")
    numProcessos = int(input())
    
    out = open("entradaEscalonador.txt", 'w')

    out.write(f"{alg}|{clock}|{policy}|{memorySize}|{pageSize}|{maxMemoryAllocationPercent}\n")
    
    print("\nCriando Processos...")
    for i in tqdm(range(0, numProcessos)):
        sleep(0.1)
        tempo = random.randrange(1,10)*clock
        prioridade = random.randrange(1, 100)
        memoryAlloc = 2 ** random.randint(9, 18)
        numberOfPages = int(memoryAlloc / pageSize)
        pageAccessSequence = [random.randint(1, numberOfPages) for _ in range(tempo)] ##### tem problema aqui spa
        out.write(f"{i}|{i}|{tempo}|{prioridade}|{memoryAlloc}|{pageAccessSequence}\n")

    out.close()