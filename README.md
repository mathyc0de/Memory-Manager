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

<algoritmo>|<quantum ou fatia> <tempo de chegada>|<PID>|\<tempo de execução>|<prioridade>
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

## ▶️ Como executar

1. Instale o pacote `bintrees` (necessário para o uso da árvore Rubro-Negra):

```bash
pip install bintrees
````

2. Execute o programa com Python 3:

```bash
python3 escalonador.py
```

3. Verifique o arquivo `result.txt` para os resultados do escalonamento.

## 📖 Licença

Este projeto é livre para fins educacionais. Para outros usos, consulte o autor.

---

Desenvolvido por:
[Felipe Fagundes Costa](https://github.com/FelipeFagundesCosta)
[Pedro Martins Caurio](https://github.com/PedroCaurio)
[Matheus Silveira](https://github.com/mathyc0de)
[Gabriel Silva]()

