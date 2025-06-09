from bintrees   import RBTree
from random     import randint

class Process:  #Criação do objeto Process
    def __init__(self, beggining, pid, exectime, priority):
        self.beggining = beggining
        self.pid = pid
        self.exectime = exectime
        self.priority = priority
        self.alreadyexec = 0
        self.done = None
        self.vruntime = None

    def __repr__(self): #Define a forma de representação do objeto
        if self.alreadyexec < self.exectime:
            if self.vruntime is None:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Alreadyexec: {self.alreadyexec:03} | Priority: {self.priority:03}')
            else:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Alreadyexec: {self.alreadyexec:03} | Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f}')
        else:
            waitingtime = self.done - self.beggining - self.exectime
            if self.vruntime is None:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03} | End: {self.done:04} | Waitingtime: {waitingtime:04}')
            else:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f} | End: {self.done:04} | Waitingtime: {waitingtime:04}')

class Escalonador:
    def __init__(self, infos): #Criação do objeto Escalonador
        self.infos = list(infos)
        self.alg = None
        self.frac = None
        self.clock = 0
        self.processes = []

        self.separate() #Chama o método de separar as informações

    def separate(self):
        self.alg, self.frac = self.infos[0].split("|") #Separa a primeira linha guardando as informações do algoritmo e da fração de CPU
        self.frac = int(self.frac)
        self.infos.pop(0) #Remove a primeira linha das informações

        for i in range(len(self.infos)): #Itera sobre cada processo da entrada
            splitting = list(map(int, self.infos[i].split("|"))) #Separa as informações do processo em uma lista

            newprocess = Process(*splitting) #Cria uma variável newprocess da classe Process e utiliza as informações da entrada
            self.processes.append(newprocess) #Isere o novo processo na lista de processos do escalonador

        #Utiliza o algoritmo solicitado
        if self.alg == "alternanciaCircular":
            self.alternanciaCircular()
        elif self.alg == "prioridade":
            self.prioridade()
        elif self.alg == "loteria":
            self.loteria()
        elif self.alg == "CFS":
            self.cfs()

    def alternanciaCircular(self):
        pass
    def prioridade(self):
        pass
    def loteria(self):

        print("== LOTERIA ==")

        # Cria a lista de processos prontos e em espera
        waiting = self.processes[:] # copia da self.processes
        ready = []

        # Verifica se tem algum processo que pode se tornar pronto
        while waiting or ready:
            for w_process in waiting[:]:
                if w_process.beggining <= self.clock: # Se está no momento do processo executa
                    print(f"Processo pronto: {w_process.pid}")
                    ready.append(w_process)
                    waiting.remove(w_process) 

            # Lida com tempo ocioso da CPU 
            if not ready:
                self.clock += 1
                continue

            # Soma todos os tickets dos processos prontos
            total_tickets = 0
            for process in ready[:]:
                total_tickets += process.priority
            
            # Se tiver tickets / processos prontos
            if total_tickets > 0:

                # Sorteia o número de acordo com a quantidade de bilhetes
                winning_ticket = randint(1, total_tickets)
                ticket_count = 0

                # Acha o processo com o bilhete sorteado
                for process in ready:
                    ticket_count += process.priority
                    if ticket_count >= winning_ticket:
                        winner_process = process
                        break
                
                # Print para mostrar qual processo foi sorteado
                print(f"Processo sorteado com PID: {winner_process.pid}| clock: {self.clock} \nTempo restante: {winner_process.exectime - winner_process.alreadyexec}")
                        
                # Executa o processo vencedor
                for _ in range(self.frac):
                    self.clock += 1
                    winner_process.alreadyexec += 1

                    # Se o processo for finalizado
                    if winner_process.alreadyexec == winner_process.exectime:
                        winner_process.done = self.clock
                        ready.remove(winner_process)
                        print(f"Clock: {self.clock:03d} | PROCESSO {winner_process.pid} FINALIZADO! | Q_BILHETES {winner_process.priority}")
                        break
            
            else:
                self.clock += 1

        # Mostra o resultado 
        self.showResult()


    def cfs(self):

        print("== CFS ==")

        tree = RBTree()                 #Cria Árvore Rubro Negra
        waiting = self.processes[:]     #Cria uma lista que é uma cópia da lista self.processes

        for process in self.processes:  #Adiciona aos processos um valor 0 para vruntime
            process.vruntime = 0

        while not tree.is_empty() or waiting:   #Enquanto a Árvore RB não estiver vazia ou houver processos esperando
            for process in waiting[:]:
                if process.beggining <= self.clock:     #Só insere o processo na árvore RB se o instante de criação do processo já estiver passado
                    tree.insert((process.vruntime, process.pid), process)   #Chave da árvore RB é uma tupla com o primeiro valor sendo o vruntime e o segundo o pid
                    print(f'Processo {process.pid} criado no clock {self.clock}')
                    waiting.remove(process)

            min = tree.min_key()
            isdone = False

            for _ in range(self.frac):  #Itera sobre a fração da cpu disponibilizada para cada processo
                execprocess = tree[min] #Define como processo a ser executado o valor extraido como min da árvore RB
                execprocess.alreadyexec += 1
                execprocess.vruntime += execprocess.priority * 0.1  #Calcula o tempo de execução virtual
                self.clock += 1

                if execprocess.alreadyexec == execprocess.exectime: #Se o a quantidade já executada for igual a quantidade necessária para concluir o processo
                    execprocess.done = self.clock
                    tree.pop(min)   #Remove o processo da árvore RB
                    isdone = True   #Muda a variável de controle para True
                    print(f'Processo {execprocess.pid} concluido')
                    print(repr(execprocess))
                    break

                if self.clock % self.frac == 0: #Se estiver na ultima iteração do for
                    print(f'{repr(execprocess)}\nclock atual: {self.clock}')
                    old_process = execprocess #Guarda a informação do processo atual em old_process
                    tree.pop(min)

            if not isdone:
                tree.insert((old_process.vruntime, old_process.pid), old_process) #Reinsere o processo na árvore RB atualizando o vruntime chave

        self.showResult() #Mostra o resultado

    #Método para criar txt de resultados
    def showResult(self):
        with open("result.txt", "w") as result:
            for i in self.processes:
                result.write(f'{repr(i)}\n')

#Bloco principal
if __name__ == "__main__":
    with open("entradaEscalonador.txt", "r") as entry:  #Extrai informações da entrada
        infos = []
        for i in entry:
            infos.append(i.strip())

    Escalonador(infos) #Utiliza o escalonador com as informações extraidas