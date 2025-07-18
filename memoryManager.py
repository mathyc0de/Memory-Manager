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
        self.pageTable: dict[int, int] = {}
    

    def limit_reached(self):
        if len(self.pageTable) == self.maxPages: return True
        return False
            
    
    def isPageInTable(self):
        return self.pageTable.get(self.page_sequence[0], False)

    
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
    
    def __init__(self, policy: str, memorySize: int, pageSize: int, maxMemoryAllocationPercent: float, algSubstituicao: str):
        self.algSubstituicao = algSubstituicao
        self.memoryPolicy = MemoryPolicy(policy)
        self.memorySize = int(memorySize)
        self.pageSize = int(pageSize)
        self.maxMemoryAllocationPercent = float(maxMemoryAllocationPercent)
        self.memory: list[Moldura] = [Moldura(i) for i in range(self.memorySize // self.pageSize)]
        self.subst = 0
    
    def accessPage(self, process: Process):
        if not process.isPageInTable(): 
            print(f"Fault! A página {process.page_sequence[0]} do processo {process.pid} não está na tabela de páginas",end=" --> ")
            self.insertPage(process)
        else:
            print(f"HIT! A página {process.page_sequence[0]} do processo {process.pid} já existe na memória. ALG: {self.algSubstituicao}")
        process.page_sequence.pop(0)  # Remove a página acessada da sequência de acesso do processo

    
    def findEmptyFrame(self):
        for frame in self.memory:
            if frame.page is None: return frame.id
        return -1

    def insertPage(self, process: Process):
        if (process.limit_reached()):
            print(f"Não foi possível adicionar a página: limite percentual excedido, fazendo substituição local de página. ALG: {self.algSubstituicao}")
            getattr(self, self.algSubstituicao)(process, MemoryPolicy.LOCAL)
            self.subst += 1
        else:
            empty_frame = self.findEmptyFrame()
            page = process.page_sequence[0]
            if (empty_frame != -1):
                print(f"Existe espaço na memória, referenciando a página {page} do processo {process.pid} na moldura {empty_frame}. ALG: {self.algSubstituicao}")
                process.pageTable[page] = empty_frame
                self.memory[empty_frame].page = page
            else: 
                print(f"Não existe espaço disponível na memória, fazendo uma substituição de página... ALG: {self.algSubstituicao}")
                self.subst += 1
                getattr(self, self.algSubstituicao)(process) # Chama o método de substituição de página correspondente ao algoritmo
    
    def removeFinishedProcess(self, process: Process):
        for frame_id in process.pageTable.values():
            self.memory[frame_id].page = None


    @staticmethod
    def fromList(infos: list, algSubstituicao: str):
        return MemoryManager(*infos[0].split("|")[2:], algSubstituicao)  # Cria um novo objeto MemoryManager a partir de uma lista de informações

    def FIFO(self, process: Process, policy: MemoryPolicy = None): # First in First Out
        print(self.subst)
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