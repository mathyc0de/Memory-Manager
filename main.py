#Bloco principal
from escalonador import Escalonador


if __name__ == "__main__":
    with open("entradaGerenciador.txt", "r") as entry:  #Extrai informações da entrada
        infos = []
        for i in entry:
            infos.append(i.strip())

    Escalonador.fromList(infos).start()  #Cria o objeto Escalonador a partir da lista de informações e inicia o escalonamento