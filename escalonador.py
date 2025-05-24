from bintrees import RBTree
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
        pass
    def cfs(self):
        print(self.frac, self.infos)
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
                execprocess.vruntime += 1 * (1 + (execprocess.priority / 100))
                self.clock += 1
                count += 1

                if execprocess.alreadyexec == execprocess.exectime:
                    execprocess.done = self.clock
                    tree.pop(min)
                    isdone = True
                    break

                if self.clock % self.frac == 0:
                    old_item = execprocess
                    print(old_item)
                    tree.pop(min)

            if not isdone:
                tree.insert((old_item.vruntime, old_item.pid), old_item)

        self.showResult()
        
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