from enum import Enum
from dataclasses import dataclass
import sys
import os
import time

class MemoryPolicy(Enum): # Classe para definir as políticas de memória
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
        self.page_sequence = page_sequence
        self.maxPages = maxPages            # Limite de páginas que o processo pode alocar na memória: (tamanho da memória * porcentagem maxima de alocação) / tamanho da pagina
        self.pageTable: dict[int, int] = {} # Tabela de páginas de cada processo {<page>: <frame_id>}
        self.last_clock = beggining         # Último relógio em que o processo foi chamado no escalonador

    def limit_reached(self):                # Verifica se o processo já atingiu o limite de páginas alocadas   
        if len(self.pageTable) == self.maxPages: return True
        return False

    def havePagesInTable(self):             # Verifica se o processo possui alguma pagina alocada na tabela de páginas (o propósito é para forçar uma política global caso n tenha)
        return len(self.pageTable) > 0
    
    def add_to_page_table(self, page: int, frame_id: int): self.pageTable[page] = frame_id  # Adiciona uma página à tabela de páginas do processo
            
    
    def isPageInTable(self):                # Verifica se a página atual do processo está na tabela de páginas
        return self.pageTable.get(self.page_sequence[0], -1) != -1
    
    def __eq__(self, value):                # Método de comparação para verificar se o processo é igual a outro pelo PID
        if (isinstance(value, Process)): return value == self
        elif (isinstance(value, int)): return value == self.pid
        return NotImplemented

    """trecho de código que era utilizado no escalonador, mas não é mais necessário"""
    # def __repr__(self): #Define a forma de representação do objeto   
    #     if self.alreadyexec < self.exectime:
    #         if self.vruntime is None:
    #             return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
    #                     f'Alreadyexec: {self.alreadyexec:03} | Priority: {self.priority:03}')
    #         else:
    #             return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
    #                     f'Alreadyexec: {self.alreadyexec:03} | Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f}')
    #     else:
    #         waitingtime = self.done - self.beggining - self.exectime
    #         if self.vruntime is None:
    #             return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
    #                     f'Priority: {self.priority:03} | End: {self.done:04} | Waitingtime: {waitingtime:04}')
    #         else:
    #             return (f'Start: {self.beggining:02} | Pid: {self.pid:02} | Exectime: {self.exectime:04} | '
    #                     f'Priority: {self.priority:03} | Vruntime: {self.vruntime:06.2f} | End: {self.done:04} | Waitingtime: {waitingtime:04}')
    

@dataclass
class Moldura:                  # Classe para definir as molduras de memória
    id: int                     #frame id
    page: int | None = None     # Página que está na moldura
    time_load: int | None = None # Tempo de carga da página na moldura
    last_use: int | None = None  # Último uso da página na moldura
    pid: int = None              # É autoexplicativo
    next_use: int | None = None
    count: int = None            # Contador para NFU

    def reset(self):             # Anula as propriedades da moldura para tornar empty
        self.page = None
        self.time_load = None
        self.last_use = None
        self.pid = None
        self.next_use = None
        self.count = 0

    def redefine(self, process: Process): #Substitui as propriedades da moldura com as de outra página
        self.page = process.page_sequence[0]
        self.time_load = process.last_clock
        self.last_use = process.last_clock
        self.pid = process.pid
        self.count = 0

    


class MemoryManager:
    """Classe responsável por gerenciar a memória."""
    def __init__(self, policy: str, memorySize: int, pageSize: int, maxMemoryAllocationPercent: float, algSubstituicao: str):
        self.algSubstituicao = algSubstituicao # FIFO, LRU (Least Recently Used), NFU (Not Frequently Used), optimal
        self.memoryPolicy = MemoryPolicy(policy) # Política de memória: local ou global
        self.memorySize = int(memorySize) # Tamanho total da memória
        self.pageSize = int(pageSize) # Tamanho de cada página
        self.maxMemoryAllocationPercent = float(maxMemoryAllocationPercent) # Porcentagem máxima de alocação de memória por processo
        self.memory: list[Moldura] = [Moldura(i) for i in range(self.memorySize // self.pageSize)] # Criação das instâncias de molduras de memória
        self.processes: list[Process] | None = None  # Será feita uma cópia da lista de processos do escalonador
        self.subst = 0 # Contador de substituições

    def FIFO_INFO(self, frame: Moldura): # informações específicas do algoritmo FIFO
        return f"| Tempo de carga: {frame.time_load}"
    
    def LRU_INFO(self, frame: Moldura): # informações específicas do algoritmo LRU
        return f"| Último uso: {frame.last_use}"
    
    def NFU_INFO(self, frame: Moldura): # informações específicas do algoritmo NFU
        return f"| Contagem de hits: {frame.count}"
    
    def optimal_INFO(self, frame: Moldura): # informações específicas do algoritmo Ótimo
        if frame.next_use is None:
            return "| Próxima vez a ser utilizado: N/A"
        elif frame.next_use == float('inf'):
            return "| Próxima vez a ser utilizado: Nunca"
        return f"| Próxima vez a ser utilizado: {frame.next_use}"
    
    # Usado para NRU
    def reset_r_bits(self):
        """Zera o bit de referência (R) de todas as molduras na memória."""
        for frame in self.memory:
            if frame.page is not None:
                frame.r_bit = 0
    
    def accessPage(self, process: Process): # Tenta acessar a página atual do processo, ou insere na memória caso n esteja
        self.update_next_use(process)
        if not process.page_sequence:
            return
        page = process.page_sequence[0] # Página atual
        if not process.isPageInTable(): # Page fault
            self.insertPage(process)        # Tenta inserir a página na memória
        else: # Page hit
            frame_id = process.pageTable[page]
            self.memory[frame_id].last_use = process.last_clock # Atualiza o último uso da página
            self.print_memory_state(highlight={frame_id: "hit"}) # destaca a informação de hit
            self.memory[frame_id].r_bit = 1
        
        if process.page_sequence:
            process.page_sequence.pop(0)  # Remove a página acessada da sequência de acesso do processo

    def findEmptyFrame(self):
        for frame in self.memory:
            if frame.page is None: return frame.id
        return -1
        
    def insertPage(self, process: Process): # Insere a página do processo na memória, fazendo substituição se necessário
        empty_frame = self.findEmptyFrame() # Procura um espaço vazio ou retorna -1
        if (process.limit_reached()):  # Verifica se o processo já atingiu o limite de páginas alocadas
            getattr(self, self.algSubstituicao)(process, MemoryPolicy.LOCAL) # substituição
            self.subst += 1 
        else:
            page = process.page_sequence[0] 
            if (empty_frame != -1): # Se houver espaço vazio na memória
                process.add_to_page_table(page, empty_frame) # Adiciona a página e a moldura na tabela de páginas do processo
                self.memory[empty_frame].redefine(process) # define as propriedades da moldura com as do processo
                self.print_memory_state(highlight={empty_frame: "add"}) # destaca a informação de adição
            else: 
                self.subst += 1
                policy = MemoryPolicy.LOCAL if self.memoryPolicy == MemoryPolicy.LOCAL and process.havePagesInTable() else MemoryPolicy.GLOBAL
                getattr(self, self.algSubstituicao)(process, policy) # Chama o método de substituição de página correspondente ao algoritmo 
                
    def removeFinishedProcess(self, process: Process): # Caso o processo termine, remove suas páginas da memória
        for frame_id in list(process.pageTable.values()):
            self.memory[frame_id].reset()  # Reseta as molduras ocupadas pelo processo
        del process.pageTable

    def get_local_frames(self, process: Process): # Obtém as molduras de memória que pertencem ao processo
        return [frame for frame in self.memory if frame.pid == process.pid]
    
    def remove_page_table_ref(self, pid: int, page: int): del self.processes[pid].pageTable[page] # Remove a referência da página na tabela de páginas do processo

    def change_page(self, process: Process, frame: Moldura): # Substitui a página na moldura por uma nova página do processo
        self.remove_page_table_ref(frame.pid, frame.page)
        frame.redefine(process)
        process.add_to_page_table(process.page_sequence[0], frame.id)

    def print_memory_state(  # Método para exibir o estado atual da memória (FEITO COM O PRIMO COPILOT)
    self, 
    delay: float = 0.01, 
    highlight: dict[int, str] = None,
    ):
    # highlight: {frame_id: "add"|"hit"|"remove"}
        COLORS = {
            "add": "\033[92m",     # Verde
            "hit": "\033[93m",     # Amarelo
            "remove": "\033[91m",  # Vermelho
            "reset": "\033[0m"
        }
        os.system('clear')
        print(f"Algoritmo: {self.algSubstituicao} | Política: {self.memoryPolicy.value.upper()}")
        print("Estado atual das molduras de memória:")
        print("-" * 40)
        for frame in self.memory:
            color = COLORS["reset"]
            if highlight and frame.id in highlight:
                color = COLORS[highlight[frame.id]]
            print(f"{color}Moldura {frame.id:02}: Página {str(frame.page) if frame.page is not None else 'Vazia'} | PID: {str(frame.pid) if frame.pid is not None else '-'}{COLORS['reset']} {getattr(self,f"{self.algSubstituicao}_INFO")(frame)}")
        print("-" * 40)
        sys.stdout.flush()
        time.sleep(delay)

    @staticmethod
    def fromList(infos: list, algSubstituicao: str):
        return MemoryManager(*infos[0].split("|")[2:], algSubstituicao)  # Cria um novo objeto MemoryManager a partir de uma lista de informações

    def FIFO(self, process: Process, policy: MemoryPolicy): # First in First Out
        if policy == MemoryPolicy.LOCAL:
            first_in: Moldura = min(self.get_local_frames(process), key=lambda frame: frame.time_load)
        else:
            first_in: Moldura = min(self.memory, key=lambda frame: frame.time_load)
        
        self.print_memory_state(highlight={first_in.id: "remove"})
        self.change_page(process, first_in)
        self.print_memory_state(highlight={first_in.id: "add"})

    def LRU(self, process: Process, policy: MemoryPolicy): # Least Recently Used (Menos Recentemente Usado)
        if policy == MemoryPolicy.LOCAL:
            lru = min(self.get_local_frames(process), key=lambda frame: frame.last_use)
        else:
            lru = min(self.memory, key=lambda frame: frame.last_use)
        self.print_memory_state(highlight={lru.id: "remove"})
        self.change_page(process, lru)
        self.print_memory_state(highlight={lru.id: "add"})

    
    def NFU(self, process: Process, policy: MemoryPolicy): # Implementando NFU (Not Frequently Used)
        # Define o escopo de frames a serem considerados para substituição
        aging_value = 1
        candidate_frames: list[Moldura]
        if policy == MemoryPolicy.LOCAL:
            candidate_frames = self.get_local_frames(process)
        else: # GLOBAL
            candidate_frames = [frame for frame in self.memory if frame.page is not None]

        nfu_candidate_count = float("inf")
        victim: Moldura = None
        
        for frame in candidate_frames:
            if frame.count < nfu_candidate_count:
                victim = frame

        # Envelhecimento
        for frame in candidate_frames:
            if frame != victim and frame.count != 0:
                frame.count -= aging_value
        # self.print_memory_state(highlight={victim.id: "remove"}) # Descomente para visualização
        if victim:
            self.change_page(process, victim)
        # self.print_memory_state(highlight={victim.id: "add"}) # Descomente para visualização
        
        
    
    def optimal(self, process: Process, policy: MemoryPolicy): # Ótimo
        if policy == MemoryPolicy.LOCAL: # Define quais molduras terá acesso dependendo da política
            frames: list[Moldura] = self.get_local_frames(process)
        else:
            frames = self.memory

        frame_to_replace = max(frames, key=lambda f: f.next_use) # Define a variavel como a moldura com maior next_use (quando será utilizada novamente)

        self.print_memory_state(highlight={frame_to_replace.id: "remove"}) # Imprime log de remoção de pagina
        self.change_page(process, frame_to_replace)                        # Substitui a pagina da moldura
        self.print_memory_state(highlight={frame_to_replace.id: "add"})    # Imprime log de adição de pagina

    def update_next_use(self, process: Process):    # Função para atualizar quando cada pagina será utilizada
        future_accesses = process.page_sequence
        for frame in self.get_local_frames(process):    # É preciso atualizar apenas a do processo que está sendo executado, independente da política
            try:
                frame.next_use = future_accesses.index(frame.page) # Atualiza com base na sequencia
            except ValueError:
                frame.next_use = float('inf') # Se não aparece na sequencia, define como infinito, significando que não será utilizada