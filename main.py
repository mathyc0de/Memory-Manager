#Bloco principal
from escalonador import Escalonador


if __name__ == "__main__":
    with open("entradaEscalonador.txt", "r") as entry:  #Extrai informações da entrada
        infos = []
        for i in entry:
            infos.append(i.strip())

    Escalonador(infos) #Utiliza o escalonador com as informações extraidas