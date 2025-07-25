from enum import Enum
from dataclasses import dataclass
import sys
import os
import time


# ==============================================================================
# Classes de Estrutura de Dados
# ==============================================================================

class MemoryPolicy(Enum):
    """Define as políticas de substituição de página: LOCAL ou GLOBAL."""
    LOCAL = "local"
    GLOBAL = "global"

class Process:
    """
    Representa um processo no sistema, contendo todos os seus metadados.

    Isso inclui informações para o escalonador (PID, tempo de execução, prioridade)
    e para o gerenciador de memória (sequência de acesso a páginas, tabela de páginas).
    """
    def __init__(self, beggining, pid, exectime, priority, page_sequence, maxPages):
        self.beggining = beggining
        self.pid = pid
        self.exectime = exectime
        self.priority = priority
        self.alreadyexec = 0
        self.done = None
        self.vruntime = None
        self.dynamic_priority = priority
        
        self.page_sequence = page_sequence
        
        self.maxPages = maxPages
        self.pageTable: dict[int, int] = {}
        self.last_clock = beggining

    def limit_reached(self):                # Verifica se o processo já atingiu o limite de páginas alocadas   
        if len(self.pageTable) == self.maxPages: return True
        return False

    def havePagesInTable(self):             # Verifica se o processo possui alguma pagina alocada na tabela de páginas (o propósito é para forçar uma política global caso n tenha)
        return len(self.pageTable) > 0
    
    def add_to_page_table(self, page: int, frame_id: int): self.pageTable[page] = frame_id  # Adiciona uma página à tabela de páginas do processo
            
    
    def isPageInTable(self):                # Verifica se a página atual do processo está na tabela de páginas
        return self.pageTable.get(self.page_sequence[0], -1) != -1
    
    def __eq__(self, value):                # Método de comparação para verificar se o processo é igual a outro pelo PID
        if (isinstance(value, Process)): return value == self.pid
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
class Moldura:
    """
    Representa uma única moldura de página (page frame) na memória física.

    Esta classe é um contêiner de dados que armazena o estado de uma moldura,
    incluindo a página que ela contém e os metadados necessários para os
    algoritmos de substituição (FIFO, LRU, NFU).
    """
    id: int                         # frame id
    page: int | None = None         # Página que está na moldura
    time_load: int | None = None    # Tempo de carga da página na moldura
    last_use: int | None = None     # Último uso da página na moldura
    pid: int = None                 # É autoexplicativo
    count: int = 0                  # Contador para NFU
    r_bit: int = 0                  # Bit de referência para o Envelhecimento
    next_use: int | None = None

    def reset(self):
        """Reseta a moldura para o estado 'vazio', limpando todos os metadados."""
        self.page = None
        self.time_load = None
        self.last_use = None
        self.pid = None
        self.count = 0
        self.next_use = None

    def redefine(self, process: Process):
        """
        Atribui uma nova página a esta moldura, atualizando seus metadados.

        Args:
            process (Process): O processo cuja página será carregada nesta moldura.
        """
        self.page = process.page_sequence[0]
        self.time_load = process.last_clock
        self.last_use = process.last_clock
        self.pid = process.pid
        self.count = 0                      # NFU
        self.r_bit = 1                      # NFU
        self.next_use = process.page_sequence[1:].index(self.page) if self.page in process.page_sequence[1:] else float('inf')
        
# ==============================================================================
# Classe Principal do Gerenciador de Memória
# ==============================================================================


class MemoryManager:
    """
        Simula o Gerenciador de Memória de um Sistema Operacional.

        Esta classe orquestra a alocação de páginas em molduras, lida com faltas de página
        (page faults), e implementa diferentes algoritmos de substituição de página
        para decidir qual página remover da memória quando ela está cheia.
        """
    def __init__(self, policy: str, memorySize: int, pageSize: int, maxMemoryAllocationPercent: float, algSubstituicao: str):
        """
        Inicializa o Gerenciador de Memória com os parâmetros da simulação.

        Args:
            policy (str): A política de memória ('local' ou 'global').
            memorySize (str): O tamanho total da memória física em bytes.
            pageSize (str): O tamanho de cada página/moldura em bytes.
            maxMemoryAllocationPercent (str): O percentual máximo de memória que um processo pode usar.
            algSubstituicao (str): O algoritmo de substituição de página a ser usado ('FIFO', 'LRU', 'NFU', 'optimal').
        """
        self.algSubstituicao = algSubstituicao          # FIFO, LRU (Least Recently Used), NFU (Not Frequently Used), optimal
        self.memoryPolicy = MemoryPolicy(policy)        # Política de memória: local ou global
        self.memorySize = int(memorySize)               # Tamanho total da memória
        self.pageSize = int(pageSize)                   # Tamanho de cada página
        self.maxMemoryAllocationPercent = float(maxMemoryAllocationPercent) # Porcentagem máxima de alocação de memória por processo
        self.memory: list[Moldura] = [Moldura(i) for i in range(self.memorySize // self.pageSize)] # Criação das instâncias de molduras de memória
        self.processes: list[Process] | None = None     # Será feita uma cópia da lista de processos do escalonador
        self.subst = 0                                  # Contador de substituições

    def FIFO_INFO(self, frame: Moldura): # informações específicas do algoritmo FIFO
        return f"| Tempo de carga: {frame.time_load}"
    
    def LRU_INFO(self, frame: Moldura): # informações específicas do algoritmo LRU
        return f"| Último uso: {frame.last_use}"
    
    def NFU_INFO(self, frame: Moldura): 
        if frame.page is not None:
            # Exibe o contador em decimal e em binário de 8 bits
            return f"| Contador: {frame.count} ({frame.count:08b})"
        return ""
    
    def optimal_INFO(self, frame: Moldura): # informações específicas do algoritmo Ótimo
        if frame.next_use is None:
            return "| Próxima vez a ser utilizado: N/A"
        elif frame.next_use == float('inf'):
            return "| Próxima vez a ser utilizado: Nunca"
        return f"| Próxima vez a ser utilizado: {frame.next_use}"
    
    def accessPage(self, process: Process): # Tenta acessar a página atual do processo, ou insere na memória caso n esteja
        self.update_next_use(process)
        if not process.page_sequence:
            return
        page = process.page_sequence[0]         # Página atual
        if not process.isPageInTable():         # Page fault
            self.insertPage(process)            # Tenta inserir a página na memória
        else:                                   # Page hit
            frame_id = process.pageTable[page]
            self.memory[frame_id].last_use = process.last_clock     # Atualiza o último uso da página
            #self.memory[frame_id].count += 1                        # Incrementa o contador de NFU
            self.memory[frame_id].r_bit = 1
            self.print_memory_state(highlight={frame_id: "hit"})    # destaca a informação de hit

        if process.page_sequence:
            process.page_sequence.pop(0)        # Remove a página acessada da sequência de acesso do processo

    def findEmptyFrame(self):
        for frame in self.memory:
            if frame.page is None: return frame.id
        return -1
        
    def insertPage(self, process: Process):     # Insere a página do processo na memória, fazendo substituição se necessário
        empty_frame = self.findEmptyFrame()     # Procura um espaço vazio ou retorna -1
        if (process.limit_reached()):           # Verifica se o processo já atingiu o limite de páginas alocadas
            getattr(self, self.algSubstituicao)(process, MemoryPolicy.LOCAL) # substituição
            self.subst += 1 
        else:
            page = process.page_sequence[0] 
            if (empty_frame != -1):             # Se houver espaço vazio na memória
                # print(f"Existe espaço na memória, referenciando a página {page} do processo {process.pid} na moldura {empty_frame}. ALG: {self.algSubstituicao}")
                process.add_to_page_table(page, empty_frame)    # Adiciona a página e a moldura na tabela de páginas do processo
                self.memory[empty_frame].redefine(process)      # Define as propriedades da moldura com as do processo
                self.print_memory_state(highlight={empty_frame: "add"}) # Destaca a informação de adição
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

    def envelhecer_contadores(self):
        """Implementa a técnica de Envelhecimento (Aging).
        Periodicamente, desloca o contador para a direita e adiciona o R-bit.
        """
        for frame in self.memory:
            if frame.page is not None:
                # 1. Desloca o contador 1 bit para a direita (envelhece)
                frame.count >>= 1
                # 2. Adiciona o R-bit ao bit mais significativo (assumindo contador de 8 bits)
                frame.count |= (frame.r_bit << 7)
                # 3. Zera o R-bit para o próximo ciclo
                frame.r_bit = 0
    
    def print_memory_state(  # Método para exibir o estado atual da memória (FEITO COM O PRIMO COPILOT)
    self, 
    delay: float = 1,     # ------------------------------------ ALTERE A VELOCIDADE AQUI e.g 1 -------------------------------------------
    highlight: dict[int, str] = None,
    ):
    # highlight: {frame_id: "add"|"hit"|"remove"}
        COLORS = {
            "add": "\033[92m",     # Verde
            "hit": "\033[93m",     # Amarelo
            "remove": "\033[91m",  # Vermelho
            "reset": "\033[0m"
        }
        os.system('cls' if os.name == 'nt' else 'clear')
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

        
    def NFU(self, process: Process, policy: MemoryPolicy): 
        candidate_frames: list[Moldura]
        if policy == MemoryPolicy.LOCAL:
            candidate_frames = self.get_local_frames(process)
        else: # GLOBAL
            candidate_frames = [frame for frame in self.memory if frame.page is not None]

        # Encontra a(s) página(s) com o menor contador de envelhecimento
        min_count = min(candidate_frames, key=lambda frame: frame.count).count
        lowest_counter_frames = [frame for frame in candidate_frames if frame.count == min_count]

        victim: Moldura
        # Se há empate no menor contador, desempata pelo menor ID de PÁGINA, como no enunciado
        # (O enunciado diz ID, o que pode ser ambíguo. ID de página é mais lógico que ID de moldura)
        victim = min(lowest_counter_frames, key=lambda frame: frame.page)
        
        
        
        self.print_memory_state(highlight={victim.id: "remove"})
        self.change_page(process, victim)
        self.print_memory_state(highlight={victim.id: "add"})  
        
        #self.envelhecer_contadores()
    
    def optimal(self, process: Process, policy: MemoryPolicy): # Ótimo
        if policy == MemoryPolicy.LOCAL: # Define quais molduras terá acesso dependendo da política
            frames: list[Moldura] = self.get_local_frames(process)
        else:
            frames = self.memory

        frame_to_replace = max(frames, key=lambda f: f.next_use)

        self.print_memory_state(highlight={frame_to_replace.id: "remove"})
        self.change_page(process, frame_to_replace)
        self.print_memory_state(highlight={frame_to_replace.id: "add"})

    def update_next_use(self, process: Process):
        future_accesses = process.page_sequence
        for frame in self.get_local_frames(process):
            try:
                frame.next_use = future_accesses.index(frame.page)
            except ValueError:
                frame.next_use = float('inf')
