#Bloco principal
from escalonador import Escalonador

"""
    Para alterar a velocidade que as informações são mostradas no terminal altere a variável delay na linha 240 do arquivo memoryManager.py
    Alunos: Gabriel Silva - 162581, Felipe Fagundes- 162566, Matheus Pimenta - 162590 e Pedro Caurio 162564  
"""

def showResult(subst: dict):
    optimal = subst.pop("optimal")
    best_key = min(subst, key=subst.get)
    best = best_key if list(subst.values()).count(subst[best_key]) == 1 else "EMPATE"
    with open("result.txt", "w") as result:
        result.write(f"{subst["FIFO"]}|{subst["LRU"]}|{subst["NFU"]}|{optimal}|{best}\n")

SUBSTITUITION_ALGORITHMS = ["FIFO","LRU","NFU","optimal"]

if __name__ == "__main__":
    with open("entradaGerenciador.txt", "r") as entry:  #Extrai informações da entrada
        infos = []
        for i in entry:
            infos.append(i.strip())


result = {}

for alg in SUBSTITUITION_ALGORITHMS:
    result[alg] =  Escalonador.fromList(infos[:], alg).start()  #Cria o objeto Escalonador a partir da lista de informações e inicia o escalonamento

showResult(result)  #Exibe o resultado final
