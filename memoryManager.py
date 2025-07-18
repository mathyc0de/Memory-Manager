from tqdm import tqdm
from enum import Enum
from dataclasses import dataclass
from json import loads


class MemoryPolicy(Enum):
    LOCAL = "local"
    GLOBAL = "global"

@dataclass
class Pagina:
    PID: int
    _id: int


    def __repr__(self):
        return f"Pagina {self._id} do processo {self.PID}"
    
    def __eq__(self, value):
        if isinstance(value, Pagina): return self.PID == value.PID and self._id == value._id
        raise f"Erro ao comparar um objeto do tipo 'página' com um objeto do tipo {type(value)}"
    
    # def __iter__(self):
    #     yield self.size
    
    # def __add__(self, value):
    #     print(self.PID)
    #     if isinstance(value, Pagina):
    #         return self.size + value.size
        
    # def __radd__(self, value):
    #     if isinstance(value, int): return self.size + value
    #     return NotImplemented


class Process:                              #Criação do objeto Process
    def __init__(self, beggining, pid, exectime, priority, page_sequence, memory_alloc):
        self.beggining = beggining          # Momento de criação do processo
        self.pid = pid                      # Id do processo
        self.exectime = exectime            # Tempo necessário de execução para concluir o processo
        self.priority = priority            # Prioridade ou número de bilhetes
        self.alreadyexec = 0                # Quantidade de tempo já executada do processo
        self.done = None                    # Variável de controle para definir se o processo já foi concluido
        self.vruntime = None                # Tempo de execução virtual - Utilizado apenas no algoritmo CFS
        self.dynamic_priority = priority    # Usado somente no algoritmo de prioridade[:4]
        self.page_sequence = loads(page_sequence)
        self.memory_alloc = memory_alloc

    
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
        self.memory: dict[str, list[Pagina]] = {"FIFO": [], "LRU": [], "NRU": [], "excellent": []}
        self.substituitions = {"FIFO": 0, "LRU": 0, "NRU": 0, "excellent": 0}
    
    def putPage(self, process: Process):
        page = Pagina(process.pid, process.page_sequence[0])
        for alg in self.memory.keys():
            if not page in self.memory[alg]: 
                print(f"Colocando a {page} na memória. ALG: {alg}")
                self.__putPage(page, alg)
            else:
                print(f"A {page} já existe na memória. ALG: {alg}")
        process.page_sequence.pop(0)  # Remove a página da sequência de acesso
    
    def removeFinishedProcess(self, process: Process):
        for alg in self.memory.keys():
            self.__removeFinishedProcess(process, alg)

    def __putPage(self, page: Pagina, alg: str):
        print(f"MEMÓRIA: {(len(self.memory[alg]) + 1) * self.pageSize}/{self.memorySize}: ALG: {alg}")
        if ((len(self.memory[alg]) + 1) * self.pageSize <= self.memorySize): ### FALTA IMPLEMENTAR A LÓGICA DA PORCENTAGEM MÁXIMA QUE UM PROCESSO TERÁ NA MEMÓRIA
            print(f"Existe espaço na memória, colocando a {page}. ALG: {alg}")
            self.memory[alg].append(page)
        else: 
            print(f"Não existe espaço na memória, fazendo uma substituição de página... ALG: {alg}")
            self.substituitions[alg] += 1
            getattr(self, alg)(page) # Chama o método de substituição de página correspondente ao algoritmo
    
    def __removeFinishedProcess(self, process: Process, alg: str):
        self.memory[alg] = [page for page in self.memory[alg] if page.PID != process.pid]

    @staticmethod
    def fromList(infos: list):
        return MemoryManager(*infos[0].split("|")[2:])

    def FIFO(self, page: Pagina): # First in First Out
        if self.memoryPolicy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def LRU(self, page: Pagina): # Least Recently Used (Menos Recentemente Usado)
        if self.memoryPolicy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def NRU(self, page: Pagina): # Not Frequently Used (Não Frequentemente Usado)
        if self.memoryPolicy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def excellent(self, page: Pagina): # Ótimo
        if self.memoryPolicy == MemoryPolicy.LOCAL:
            ...
        else:
            ...
    
    def showResult(self):
        subst = self.substituitions
        excellent = subst.pop("excellent")
        best_key = min(subst, key=subst.get)
        best = best_key if list(subst.values()).count(subst[best_key]) == 1 else "EMPATE"
        with open("result.txt", "w") as result:
            result.write(f"{subst["FIFO"]}|{subst["LRU"]}|{subst["NRU"]}|{excellent}|{best}\n")