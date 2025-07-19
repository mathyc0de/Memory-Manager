from tqdm import tqdm
from enum import Enum
from dataclasses import dataclass
from json import loads


class MemoryPolicy(Enum):
    LOCAL = "local"
    GLOBAL = "global"



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
        self.last_clock = beggining
    

    def limit_reached(self):
        if len(self.pageTable) == self.maxPages: return True
        return False

    def havePagesInTable(self):
        return len(self.pageTable) > 0
    
    def add_to_page_table(self, page: int, frame_id: int): self.pageTable[page] = frame_id
            
    
    def isPageInTable(self):
        return self.pageTable.get(self.page_sequence[0], -1) != -1
    
    def __eq__(self, value):
        if (isinstance(value, Process)): return value == self
        elif (isinstance(value, int)): return value == self.pid
        return NotImplemented

    
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
    

@dataclass
class Moldura:
    id: int
    page: int | None = None
    time_load: int | None = None
    last_use: int | None = None
    pid: int = None

    def reset(self):
        self.page = None
        self.time_load = None
        self.last_use = None
        self.pid = None

    def redefine(self, process: Process):
        self.page = process.page_sequence[0]
        self.time_load = process.last_clock
        self.last_use = process.last_clock
        self.pid = process.pid
    


class MemoryManager:
    
    def __init__(self, policy: str, memorySize: int, pageSize: int, maxMemoryAllocationPercent: float, algSubstituicao: str):
        self.algSubstituicao = algSubstituicao
        self.memoryPolicy = MemoryPolicy(policy)
        self.memorySize = int(memorySize)
        self.pageSize = int(pageSize)
        self.maxMemoryAllocationPercent = float(maxMemoryAllocationPercent)
        self.memory: list[Moldura] = [Moldura(i) for i in range(self.memorySize // self.pageSize)]
        self.processes: list[Process] | None = None
        self.subst = 0
    
    def accessPage(self, process: Process):
        page = process.page_sequence[0]
        if not process.isPageInTable(): 
            print(f"Fault! A página {page} do processo {process.pid} não está na tabela de páginas",end=" --> ")
            self.insertPage(process)
        else:
            print(f"HIT! A página {page} do processo {process.pid} já existe na memória. ALG: {self.algSubstituicao}")
            self.memory[process.pageTable[page]].last_use = process.last_clock
        process.page_sequence.pop(0)  # Remove a página acessada da sequência de acesso do processo

    
    def findEmptyFrame(self):
        for frame in self.memory:
            if frame.page is None: return frame.id
        return -1
        

    def insertPage(self, process: Process):
        empty_frame = self.findEmptyFrame()
        if (process.limit_reached()):
            policy = MemoryPolicy.LOCAL if process.havePagesInTable() else MemoryPolicy.GLOBAL
            print(f"Não foi possível adicionar a página: limite percentual excedido, fazendo substituição {policy.value} de página. ALG: {self.algSubstituicao}")
            getattr(self, self.algSubstituicao)(process, policy)
            self.subst += 1
        else:
            page = process.page_sequence[0]
            if (empty_frame != -1):
                print(f"Existe espaço na memória, referenciando a página {page} do processo {process.pid} na moldura {empty_frame}. ALG: {self.algSubstituicao}")
                process.add_to_page_table(page, empty_frame)
                self.memory[empty_frame].redefine(process)
            else: 
                print(f"Não existe espaço disponível na memória, fazendo uma substituição de página... ALG: {self.algSubstituicao}")
                self.subst += 1
                policy = MemoryPolicy.LOCAL if self.memoryPolicy == MemoryPolicy.LOCAL and process.havePagesInTable() else MemoryPolicy.GLOBAL
                getattr(self, self.algSubstituicao)(process, policy) # Chama o método de substituição de página correspondente ao algoritmo
    
    def removeFinishedProcess(self, process: Process):
        for frame_id in list(process.pageTable.values()):
            self.memory[frame_id].reset()  # Reseta as molduras ocupadas pelo processo
        del process.pageTable

    def get_local_frames(self, process: Process):
        return [frame for frame in self.memory if frame.pid == process.pid]
    
    def remove_page_table_ref(self, pid: int, page: int): del self.processes[pid].pageTable[page]


    @staticmethod
    def fromList(infos: list, algSubstituicao: str):
        return MemoryManager(*infos[0].split("|")[2:], algSubstituicao)  # Cria um novo objeto MemoryManager a partir de uma lista de informações

    def FIFO(self, process: Process, policy: MemoryPolicy): # First in First Out
        if policy == MemoryPolicy.LOCAL:
            first_in: Moldura = min(self.get_local_frames(process), key=lambda frame: frame.time_load)
            print(f"Substituindo a página menos usada {first_in.page} do mesmo processo, pela página {process.page_sequence[0]}. ALG: {self.algSubstituicao}")
        else:
            first_in: Moldura = min(self.memory, key=lambda frame: frame.time_load)
            print(f"Substituindo a página contida na moldura {first_in.id} em escopo global, pela página {process.page_sequence[0]} do processo {process.pid}.")
        
        self.remove_page_table_ref(first_in.pid, first_in.page)
        first_in.redefine(process)
        process.add_to_page_table(process.page_sequence[0], first_in.id)

    def LRU(self, process: Process, policy: MemoryPolicy): # Least Recently Used (Menos Recentemente Usado)
        if policy == MemoryPolicy.LOCAL:
            frames: list[Moldura] = [frame for frame in self.memory if frame.page is not None and frame.page in process.pageTable]
        else:
            ...
    
    def NRU(self, process: Process, policy: MemoryPolicy): # Not Frequently Used (Não Frequentemente Usado)
        if policy == MemoryPolicy.LOCAL:
            frames: list[Moldura] = [frame for frame in self.memory if frame.page is not None and frame.page in process.pageTable]
        else:
            ...
    
    def optimal(self, process: Process, policy: MemoryPolicy): # Ótimo
        if policy == MemoryPolicy.LOCAL:
            frames: list[Moldura] = [frame for frame in self.memory if frame.page is not None and frame.page in process.pageTable]
        else:
            ...