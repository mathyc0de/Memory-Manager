# Escalonamento de Processos (CFS, Prioridade, Loteria, Alternância Circular)

Este projeto é um simulador de **escalonamento de processos**, implementado em Python, com suporte aos seguintes algoritmos:

- [x] CFS (Completely Fair Scheduler)
- [x] Prioridade
- [x] Loteria
- [x] Alternância Circular

## Descrição

O programa simula o funcionamento de escalonadores de processos usados em sistemas operacionais. Cada processo é representado por:

- Tempo de chegada
- PID
- Tempo de execução necessário
- Prioridade

Os resultados são salvos em um arquivo `result.txt`, incluindo o tempo de finalização e tempo de espera de cada processo.

## Estrutura do projeto

```

Escalonamento/
│
├── entradaEscalonador.txt   # Arquivo com a entrada dos processos
├── escalonador.py           # Código principal
├── result.txt               # Arquivo gerado com os resultados da simulação
└── README.md                # (Você está aqui)

```

## Formato da Entrada

O arquivo `entradaEscalonador.txt` deve seguir o seguinte formato:

```

<algoritmo>|<quantum ou fatia>
<tempo de chegada>|<PID>|\<tempo de execução>|<prioridade>
...

```

### Exemplo:
```

CFS|10
0|0|90|17
1|1|80|70
2|2|60|71
...

````

Este arquivo pode ser criado utilizando o script `geradorEntrada.py`, esse script é de autoria do Professor Pedro de Botelho Marcos.
### Utilizando geradorEntrada.py
1. Execute o programa com Python 3:

```bash
python3 geradorEntrada.py
```
2. O script irá solicitar entradas do usuário pelo terminal em que foi executado
   
    2.1 Informar o tipo de algoritmo que deseja utilizar
   | Entrada |  Algoritmo |
   |-------|-------|
   | 1 | Alternância Circular |
   | 2 | Prioridade |
   | 3 | Loteria |
   | 4 | CFS |
   
    2.2 Informar a fração da CPU que deseja que cada processo tenha por vez
   
    2.3 Informar o número de processos a serem criados
3. Exemplo
```bash
Bem-vindo ao gerador de arquivos de entrada para o escalonador!
Escolha o algoritmo: 1: alternancia circular, 2: prioridade, 3: loteria, 4: CFS
4
Informe a fracao de CPU que cada processo tera direito por vez
10
Informe o numero de processos a serem criados
15
````
## Como executar
1. Certifique-se de que o arquivo `entradaEscalonador.txt` está no mesmo diretório que o script `escalonador.py`
2. Instale o pacote `bintrees` (necessário para o uso da árvore Rubro-Negra):

```bash
pip install bintrees
````
   
3. Execute o programa com Python 3:

```bash
python3 escalonador.py
```

4. Verifique o arquivo `result.txt` para os resultados do escalonamento.

## Licença

Este projeto foi desenvolvido para a disciplina de Sistemas Operacionais no curso de Engenharia de Computação - FURG, ministrada pelo Professor Pedro de Botelho Marcos.

Este projeto é livre para fins educacionais. Para outros usos, consulte o autor.

---

Desenvolvido por:
[Felipe Fagundes Costa](https://github.com/FelipeFagundesCosta);
[Pedro Martins Caurio](https://github.com/PedroCaurio);
[Matheus Silveira](https://github.com/mathyc0de);
[Gabriel Silva](https://github.com/Foqueto).

