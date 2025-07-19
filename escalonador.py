from bintrees   import RBTree
from random     import randint
from memoryManager import MemoryManager, Process


class Escalonador:                  #Criação do objeto Escalonador
    def __init__(self, alg: str, frac: int, algSubstituicao: str, infos: list):   
        print(infos[0])   
        self.memory_manager = MemoryManager.fromList(infos, algSubstituicao)
        self.maxProcessPages = self.memory_manager.memorySize * self.memory_manager.maxMemoryAllocationPercent // self.memory_manager.pageSize
        infos.pop(0)
        self.alg = alg         # Algoritmo selecionado pelo usuário
        self.frac = frac            # Fração da CPU que cada processo terá controle 
        self.clock = 0              # Clock atual
        self.processes = []         # Lista de processos
        self.separate(infos)             #Chama o método de separar as informações


    @staticmethod
    def fromList(infos: list, algSubstuicao: str):
        alg, frac = infos[0].split("|")[:2] #Separa a primeira linha guardando as informações do algoritmo e da fração de CPU
        return Escalonador(alg, int(frac) ,algSubstuicao ,infos)  #Cria um novo objeto Escalonador a partir de uma lista de informações

    def separate(self, infos):
        self.tempoex = [] # Cria uma lista vazia para armazenar o tempo que cada processo precisa na CPU
        for i in range(len(infos)): #Itera sobre cada processo da entrada
            data =  infos[i].split("|")
            splitting = list(map(int, data[:4])) #Separa as informações do processo em uma lista
            newprocess = Process(*splitting, maxPages = self.maxProcessPages, page_sequence=data[5]) #Cria uma variável newprocess da classe Process e utiliza as informações da entrada
            self.processes.append(newprocess) #Isere o novo processo na lista de processos do escalonador
            self.tempoex.append(newprocess.exectime) # Insere o tempo de execução desse novo Processo na lista tempo de execução

    def start(self): 
        getattr(self, self.alg)()
        return self.memory_manager.subst

    def alternanciaCircular(self):
            
        # *OBS End = Tempo Total e Waitingtime = Tempo que ficou sem ussar a CPU no estado "Pronto"

        print("                     Alternância Circular") # Printa o nome do escalonamento
        processos_prontos = [] # Lista com Processos prontos para executar
        self.time = 0 #tempo

        for a in self.processes: # Percorre toos os Processos
            if self.time >= a.beggining: # Verifica se o processo existe
                processos_prontos.append(a) # Caso exista adiciona o mesmo a uma lista de processos prontos...
                                            # ...para ussar a CPU
        print()
        print("Ordem de Processos utilizando a CPU:")
        print()

        while processos_prontos: #Equanto houver um processo pronto para a CPU segue a operação
            
            processo_atual = processos_prontos.pop(0)# Entende quem é o processo atual e remove ele da lista de prontos
            indice = self.processes.index(processo_atual) # Pega seu indice para calcular seu tempo de execução corretamente
            

            if processo_atual.exectime >= self.frac: # Verifica qual o caso do processo, se cobre todo o tempo...
                                                     # ... fornecido pela CPU
                
                print(f"Time {self.time:04d} | PID {processo_atual.pid:02d} esta usando a CPU | Tempo restante: {processo_atual.exectime - processo_atual.alreadyexec}")
                print("------------------------------------------------------------------------")
                self.tempoex[indice]-= self.frac # Subtrai o tempo de execução necessario daquele processo, pois ele ussou a CPU
                self.time += self.frac # Registra esse ato ao tempo
                processo_atual.alreadyexec += self.frac # Registra em quanto tempo o Processo ussou a CPU
                
                for m in self.processes: # Busca novos processos que estejam prontos para ussas a CPU e que são diferentes do processo atual
                    if m.done is None and self.time >= m.beggining and m not in processos_prontos and m != processo_atual:
                        processos_prontos.append(m)

                if self.tempoex[indice] != 0: # Logo apos, verifica se o processo nao terminou
                    processos_prontos.append(processo_atual)# Caso não tenha adiciona o mesmo novamente a lista de processos ...
                                                            # ...que seram executados pela CPU

                else: # Caso contrario diz que o processo terminou, e define  o tempo total que levou para terminar.
                    processo_atual.done = self.time # Define  o tempo total que levou para terminar e que terminou.

            else: # Caso o Processo leve menos tempo que a CPU
                tempo_restante = self.tempoex[indice] # Define o tempo que falta
    
                print(f"Time {self.time:04d} | PID {processo_atual.pid:02d} esta usando a CPU | Tempo restante: {processo_atual.exectime - processo_atual.alreadyexec}")
                print("------------------------------------------------------------------------")

                self.time += tempo_restante #Registra essa acão do Processo  ao ussar  a CPU ao tempo
                processo_atual.alreadyexec += tempo_restante # Registra esse tempo de usso na CPU
                self.tempoex[indice] = 0 # Zero o tempo preciso para executar pois ja ussou o que precisava
                processo_atual.done = self.time # Soma essa diferença ao tempo que ficou na CPU

                

            for u in self.processes:# Busca em todos os processos se algum esta pronto para ussar a CPU
                if u.done == None and (self.time >= u.beggining) and (u not in processos_prontos): #Verifica se podem entrar na lista dos Prontos
                    processos_prontos.append(u)# Caso possa entrar na lista de prontos para ussar a CPU, adiciona o mesmo á fila
                    
        for l in self.processes:# Printa cada Processo após a Execução
                print(l)


    def prioridade(self):

        print("== PRIORIDADE ==")
        
        #armazena os processos em uma variavel local
        waiting: list[Process] = self.processes[:]
        created = []

        while waiting or created:
            
            # Verifica se existem novos processos prontos para execução
            for process in waiting[:]:
                if (process.beggining) <= self.clock:
                    print(f"Processo criado | PID: {process.pid} | CLOCK: {self.clock} | PRIORIDADE: {process.priority} | TEMPO DE CPU {process.exectime}")
                    created.append(process)
                    waiting.remove(process)

            # Caso não existam novos processos e os demais já foram finalizados, permanece ocioso
            if not created:
                self.clock += 1
                continue
            
            # Obtém o processo com a maior prioridade
            priorities = [process.dynamic_priority for process in created]
            highest_priority: Process = created[priorities.index(min(priorities))] # Maior prioridade
            print(f"Processo {highest_priority.pid} selecionado | tempo restante {highest_priority.exectime - highest_priority.alreadyexec} | prioridade dinâmica {highest_priority.dynamic_priority} | prioridade original {highest_priority.priority}.")

            # Executa os processos
            for _ in range(self.frac):
                self.clock += 1
                highest_priority.alreadyexec += 1

                # Caso o processo tenha terminado seu tempo de execução, remove ele da lista dos processos prontos
                if (highest_priority.alreadyexec == highest_priority.exectime):
                    print(f"Processo finalizado | PID: {highest_priority.pid} | CLOCK: {self.clock}")
                    created.remove(highest_priority)
                    highest_priority.done = self.clock
                    break
            
            # Incrementa a prioridade para evitar monopólio da cpu.
            highest_priority.dynamic_priority += 10

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


    def CFS(self):

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
                self.memory_manager.accessPage(execprocess, self.clock)
                execprocess.alreadyexec += 1
                execprocess.vruntime += execprocess.priority * 0.1  #Calcula o tempo de execução virtual
                self.clock += 1

                if execprocess.alreadyexec == execprocess.exectime: #Se o a quantidade já executada for igual a quantidade necessária para concluir o processo
                    execprocess.done = self.clock
                    tree.pop(min)   #Remove o processo da árvore RB
                    isdone = True   #Muda a variável de controle para True
                    print(f'Processo {execprocess.pid} concluido')
                    print(f'Removendo o processo da memória...')
                    self.memory_manager.removeFinishedProcess(execprocess) #Remove processo finalizado da memória
                    break

                if self.clock % self.frac == 0: #Se estiver na ultima iteração do for
                    print(f'{repr(execprocess)}\nclock atual: {self.clock}')
                    old_process = execprocess #Guarda a informação do processo atual em old_process
                    tree.pop(min)

            if not isdone:
                tree.insert((old_process.vruntime, old_process.pid), old_process) #Reinsere o processo na árvore RB atualizando o vruntime chave