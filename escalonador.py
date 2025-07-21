from bintrees import RBTree
from random import randint
from memoryManager import MemoryManager, Process

class Escalonador:
    """
    Simula um escalonador de processos do Sistema Operacional.

    Esta classe é responsável por gerenciar o ciclo de vida dos processos,
    determinar qual processo usa a CPU a cada momento e, crucialmente,
    acionar o MemoryManager para simular os acessos à memória,
    permitindo a avaliação dos algoritmos de substituição de página.
    """
    
    def __init__(self, alg: str, frac: int, algSubstituicao: str, infos: list):
        """
        Inicializa o Escalonador e seus componentes.

        Args:
            alg (str): O nome do algoritmo de escalonamento a ser usado (ex: 'CFS').
            frac (int): A fração de CPU (quantum) que cada processo pode usar por vez.
            algSubstituicao (str): O nome do algoritmo de substituição de página.
            infos (list): A lista de strings lida do arquivo de entrada.
        """
        self.memory_manager = MemoryManager.fromList(infos, algSubstituicao)
        self.maxProcessPages = self.memory_manager.memorySize * self.memory_manager.maxMemoryAllocationPercent // self.memory_manager.pageSize
        infos.pop(0)
        self.alg = alg
        self.frac = frac
        self.clock = 0
        self.processes = []
        self.separate(infos)
        self.memory_manager.processes = self.processes

    @staticmethod
    def fromList(infos: list, algSubstituicao: str):
        """Cria uma instância de Escalonador a partir de uma lista de informações."""
        alg, frac = infos[0].split("|")[:2]
        return Escalonador(alg, int(frac), algSubstituicao, infos)

    def separate(self, infos: list):
        """Analisa as informações de entrada e cria os objetos Process."""
        for i in range(len(infos)):
            data = infos[i].split("|")
            splitting = list(map(int, data[:4]))
            newprocess = Process(*splitting, maxPages=self.maxProcessPages, page_sequence=data[5])
            self.processes.append(newprocess)

    def start(self) -> int:
        """
        Inicia o processo de escalonamento chamando o algoritmo selecionado.

        Returns:
            int: O número total de substituições de página ocorridas.
        """
        getattr(self, self.alg)()
        return self.memory_manager.subst

    def _update_ready_queue(self, ready_queue: list, waiting_queue: list, current_process: Process | None = None):
        """
        Função auxiliar para mover processos da fila de espera para a fila de prontos.
        Funciona para escalonadores que usam listas como fila de prontos.
        
        Args:
            ready_queue (list): A fila de processos prontos para executar.
            waiting_queue (list): A lista de processos que ainda não foram criados.
            current_process (Process | None): O processo atualmente em execução, para evitar que seja
                                               adicionado à fila de prontos novamente.
        """
        for process in waiting_queue[:]:
            if process.beggining <= self.clock:
                # A verificação 'process not in ready_queue' é crucial para evitar duplicação.
                if process not in ready_queue and process != current_process:
                    ready_queue.append(process)
                    waiting_queue.remove(process)

    def alternanciaCircular(self):
        """
        Implementa o algoritmo de escalonamento Alternância Circular.
        Os processos são executados em uma fila circular, cada um por um quantum de tempo.
        """
        waiting_queue = self.processes[:]
        ready_queue = []
        self._update_ready_queue(ready_queue, waiting_queue)

        while ready_queue:
            current_process = ready_queue.pop(0)
            
            # Fase 1: Executa o processo pelo seu quantum ou até terminar.
            for _ in range(self.frac):
                if current_process.alreadyexec == current_process.exectime:
                    break  # Processo concluiu sua execução.
                
                # Simula um acesso à memória a cada ciclo de clock.
                if current_process.page_sequence:
                    self.memory_manager.accessPage(current_process)

                current_process.alreadyexec += 1
                self.clock += 1
                
                # Fase 2: Verifica se novos processos ficaram prontos durante a execução.
                self._update_ready_queue(ready_queue, waiting_queue, current_process)
            
            # Fase 3: Aplica o envelhecimento para o NFU após o quantum.
            if self.memory_manager.algSubstituicao == "NFU":
                self.memory_manager.envelhecer_contadores()

            # Fase 4: Decide o destino do processo após a execução.
            if current_process.alreadyexec < current_process.exectime:
                ready_queue.append(current_process)  # Devolve para o fim da fila.
            else:
                current_process.done = self.clock
                self.memory_manager.removeFinishedProcess(current_process)

    def prioridade(self):
        """
        Implementa o algoritmo de escalonamento por Prioridade com envelhecimento dinâmico.
        O processo com a maior prioridade (menor valor numérico) é escolhido.
        A prioridade de um processo diminui (valor aumenta) após a execução para evitar inanição.
        """
        waiting_queue = self.processes[:]
        ready_queue = []
        
        while waiting_queue or ready_queue:
            self._update_ready_queue(ready_queue, waiting_queue)
            if not ready_queue:
                self.clock += 1
                continue

            # Encontra o processo com a maior prioridade.
            current_process = min(ready_queue, key=lambda p: p.dynamic_priority)
            ready_queue.remove(current_process)
            
            for _ in range(self.frac):
                if current_process.alreadyexec == current_process.exectime: break
                if current_process.page_sequence: self.memory_manager.accessPage(current_process)
                current_process.alreadyexec += 1
                self.clock += 1
                self._update_ready_queue(ready_queue, waiting_queue, current_process)
            
            if self.memory_manager.algSubstituicao == "NFU": self.memory_manager.envelhecer_contadores()

            if current_process.alreadyexec < current_process.exectime:
                current_process.dynamic_priority += 1  # Envelhece a prioridade.
                ready_queue.append(current_process)
            else:
                current_process.done = self.clock
                self.memory_manager.removeFinishedProcess(current_process)

    def loteria(self):
        """
        Implementa o algoritmo de escalonamento Loteria.
        Um processo é sorteado para execução com base no número de "bilhetes" (prioridade) que possui.
        """
        waiting_queue = self.processes[:]
        ready_queue = []
        
        while waiting_queue or ready_queue:
            self._update_ready_queue(ready_queue, waiting_queue)
            if not ready_queue:
                self.clock += 1
                continue

            total_tickets = sum(p.priority for p in ready_queue if p.priority > 0)
            if total_tickets <= 0:
                self.clock += 1
                continue

            # Sorteia o bilhete vencedor.
            winning_ticket = randint(1, total_tickets)
            
            # Encontra o processo dono do bilhete.
            ticket_count = 0
            winner_process = None
            for process in ready_queue:
                ticket_count += process.priority
                if ticket_count >= winning_ticket:
                    winner_process = process
                    break
            
            ready_queue.remove(winner_process)

            for _ in range(self.frac):
                if winner_process.alreadyexec == winner_process.exectime: break
                if winner_process.page_sequence: self.memory_manager.accessPage(winner_process)
                winner_process.alreadyexec += 1
                self.clock += 1
                self._update_ready_queue(ready_queue, waiting_queue, winner_process)
            
            if self.memory_manager.algSubstituicao == "NFU": self.memory_manager.envelhecer_contadores()

            if winner_process.alreadyexec < winner_process.exectime:
                ready_queue.append(winner_process)
            else:
                winner_process.done = self.clock
                self.memory_manager.removeFinishedProcess(winner_process)

    def CFS(self):
        """
        Implementa o Completely Fair Scheduler (CFS).
        Utiliza uma Árvore Rubro-Negra para escolher o processo com o menor
        tempo de execução virtual (vruntime), garantindo equidade.
        """
        tree = RBTree()
        waiting_queue = self.processes[:]
        for p in self.processes: p.vruntime = 0

        while not tree.is_empty() or waiting_queue:
            # Lógica de inserção específica para a árvore RBTree
            for process in waiting_queue[:]:
                if process.beggining <= self.clock:
                    if (process.vruntime, process.pid) not in tree:
                        tree.insert((process.vruntime, process.pid), process)
                        waiting_queue.remove(process)
            
            if tree.is_empty():
                self.clock += 1
                continue
            
            # Pega o processo com o menor vruntime.
            min_key = tree.min_key()
            execprocess = tree.pop(min_key)
            
            isdone = False
            for _ in range(self.frac):
                if execprocess.alreadyexec == execprocess.exectime:
                    isdone = True
                    break
                
                execprocess.last_clock = self.clock
                if execprocess.page_sequence: self.memory_manager.accessPage(execprocess)
                
                execprocess.alreadyexec += 1
                execprocess.vruntime += execprocess.priority  # vruntime aumenta com base na prioridade
                self.clock += 1

            if self.memory_manager.algSubstituicao == "NFU": self.memory_manager.envelhecer_contadores()
            
            if not isdone:
                tree.insert((execprocess.vruntime, execprocess.pid), execprocess)
            else:
                self.memory_manager.removeFinishedProcess(execprocess)