from bintrees import RBTree
import random
class Process:
    def __init__(self, beggining, pid, exectime, priority):
        self.beggining = beggining
        self.pid = pid
        self.exectime = exectime
        self.priority = priority
        self.alreadyexec = 0
        self.done = None
        self.vruntime = None

    def __repr__(self):
        if self.alreadyexec < self.exectime:
            if self.vruntime is None:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03}')
            else:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f}')
        else:
            waitingtime = self.done - self.beggining - self.exectime
            if self.vruntime is None:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03} | End: {self.done:04} | Waitingtime: {waitingtime:04}')
            else:
                return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
                        f'Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f} | End: {self.done:04} | Waitingtime: {waitingtime:04}')

class Escalonador:
    def __init__(self, infos):
        self.infos = list(infos)
        self.alg = None
        self.frac = None
        self.clock = 0
        self.processes = []

        self.separate()

    def separate(self):
        self.alg, self.frac = self.infos[0].split("|")
        self.frac = int(self.frac)
        self.infos.pop(0)

        for i in range(len(self.infos)):
            splitting = list(map(int, self.infos[i].split("|")))

            newprocess = Process(*splitting)
            self.processes.append(newprocess)

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
                winning_ticket = random.randint(1, total_tickets)
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
        tree = RBTree()
        waiting = self.processes[:]

        for process in self.processes:
            process.vruntime = 0

        while not tree.is_empty() or waiting:
            for process in waiting[:]:
                if process.beggining <= self.clock:
                    tree.insert((process.vruntime, process.pid), process)
                    waiting.remove(process)

            min = tree.min_key()
            isdone = False
            count = 0

            while count % self.frac != 0 or count == 0:
                execprocess = tree[min]
                execprocess.alreadyexec += 1
                execprocess.vruntime += execprocess.priority * 0.1
                self.clock += 1
                count += 1

                if execprocess.alreadyexec == execprocess.exectime:
                    execprocess.done = self.clock
                    tree.pop(min)
                    isdone = True
                    break

                if self.clock % self.frac == 0:
                    old_item = execprocess
                    tree.pop(min)

            if not isdone:
                tree.insert((old_item.vruntime, old_item.pid), old_item)

        self.showResult()
        self.infos = []
        self.alg = None
        self.frac = None
        self.clock = 0
        self.processes = []

    def showResult(self):
        with open("result.txt", "w") as result:
            for i in self.processes:
                result.write(f'{repr(i)}\n')

if __name__ == "__main__":
    with open("entradaEscalonador.txt", "r") as entry:
        infos = []
        for i in entry:
            infos.append(i.strip())

    escalonar = Escalonador(infos) 