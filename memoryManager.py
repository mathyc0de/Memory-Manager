from tqdm import tqdm
from enum import Enum
from dataclasses import dataclass
from json import loads


class MemoryPolicy(Enum):
    LOCAL = "local"
    GLOBAL = "global"

@dataclass
class Moldura:
    id: int
    page: int | None = None
    time_load: int | None = None
    last_use: int | None = None


class Process:                              #Criação do objeto Process
    def __init__(self, beggining, pid, exectime, priority, page_sequence, maxPages):
        self.beggining = beggining          # Momento de criação do processo
        self.pid = pid                      # Id do processo
        self.exectime = exectime            # Tempo necessário de execução para concluir o processo
        self.priority = priority            # Prioridade ou número de bilhetes
        self.alreadyexec = 0                # Quantidade de tempo já executada do processo
        self.done = None                    # Variável de controle para definir se o processo já foi concluido
        self.vruntime = None                # Tempo de execução virtual - Utilizado apenas no algoritmo CFS
        self.dynamic_priority = priority    # Usado somente no algoritmo de prioridade[:4]
        self.page_sequence = loads(page_sequence)
        self.maxPages = maxPages
        self.pageTable: dict[str, dict[int, int]] = {"FIFO": {}, "LRU": {}, "NRU": {}, "optimal": {}}
    

    def limit_reached(self, alg):
        if len(self.pageTable[alg]) == self.maxPages:
                print(f"Não foi possível adicionar a página: limite percentual excedido, fazendo substituição de página. ALG: {alg}")
                return True
        return False
            
    
    def access_next_page(self, alg):
        return self.pageTable[alg].get(self.page_sequence[0], False)

    
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
    



class MemoryManager:
    
    def __init__(self, policy: str, memorySize: int, pageSize: int, maxMemoryAllocationPercent: float):
        self.memoryPolicy = MemoryPolicy(policy)
        self.memorySize = int(memorySize)
        self.pageSize = int(pageSize)
        self.maxMemoryAllocationPercent = float(maxMemoryAllocationPercent)
        self.memory: dict[str, list[Moldura]] = {"FIFO": self.createFrames(), "LRU": self.createFrames(), "NRU": self.createFrames(), "optimal": self.createFrames()}
        self.subst = {"FIFO": 0, "LRU": 0, "NRU": 0, "optimal": 0}
    
    def putPage(self, process: Process):
        for alg in self.memory.keys():
            if not process.access_next_page(alg): 
                print(f"Fault! A página {process.page_sequence[0]} do processo {process.pid} não está na tabela de páginas",end=" --> ")
                self.__putPage(process, alg)
            else:
                print(f"HIT! A página {process.page_sequence[0]} do processo {process.pid} já existe na memória. ALG: {alg}")
        process.page_sequence.pop(0)  # Remove a página da sequência de acesso
    
    def createFrames(self):
        return [Moldura(i) for i in range(self.memorySize // self.pageSize)]
    
    def removeFinishedProcess(self, process: Process):
        for alg in self.memory.keys():
            self.__removeFinishedProcess(process, alg)
    
    def findEmptyFrame(self, alg: str):
        for frame in self.memory[alg]:
            if frame.page is None: return frame.id
        return -1

    def __putPage(self, process: Process, alg: str):
        if (process.limit_reached(alg)): 
            getattr(self, alg)(process, MemoryPolicy.LOCAL)
            self.subst[alg] += 1
        else:
            empty_frame = self.findEmptyFrame(alg)
            page = process.page_sequence[0]
            if (empty_frame != -1):
                print(f"Existe espaço na memória, referenciando a página {page} do processo {process.pid} na moldura {empty_frame}. ALG: {alg}")
                process.pageTable[alg][page] = empty_frame
                self.memory[alg][empty_frame].page = page
            else: 
                print(f"Não existe espaço disponível na memória, fazendo uma substituição de página... ALG: {alg}")
                self.subst[alg] += 1
                getattr(self, alg)(process) # Chama o método de substituição de página correspondente ao algoritmo
    
    def __removeFinishedProcess(self, process: Process, alg: str):
        for frame_id in process.pageTable[alg].values():
            self.memory[alg][frame_id].page = None


    @staticmethod
    def fromList(infos: list):
        return MemoryManager(*infos[0].split("|")[2:])

    def FIFO(self, process: Process, policy: MemoryPolicy = None): # First in First Out
        _policy = self.memoryPolicy if not policy else policy
        if _policy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def LRU(self, process: Process, policy: MemoryPolicy = None): # Least Recently Used (Menos Recentemente Usado)
        _policy = self.memoryPolicy if not policy else policy
        if _policy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def NRU(self, process: Process, policy: MemoryPolicy = None): # Not Frequently Used (Não Frequentemente Usado)
        _policy = self.memoryPolicy if not policy else policy
        if _policy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def optimal(self, process: Process, policy: MemoryPolicy = None): # Ótimo
        _policy = self.memoryPolicy if not policy else policy
        if _policy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def showResult(self):
        subst = self.subst
        optimal = subst.pop("optimal")
        best_key = min(subst, key=subst.get)
        best = best_key if list(subst.values()).count(subst[best_key]) == 1 else "EMPATE"
        with open("result.txt", "w") as result:
            result.write(f"{subst["FIFO"]}|{subst["LRU"]}|{subst["NRU"]}|{optimal}|{best}\n")