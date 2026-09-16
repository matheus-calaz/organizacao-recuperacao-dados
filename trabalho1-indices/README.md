# Trabalho 1 — Índices e Lista Invertida

Implementação de um sistema de indexação para registros de jogos armazenados em um arquivo binário de tamanho variável.

O programa constrói e mantém um índice primário por identificador e dois índices secundários — gênero e publicadora — implementados com **late binding** e uma **lista invertida**.

## Funcionalidades

- construção dos índices a partir do arquivo `games.dat`;
- busca direta pela chave primária;
- busca secundária por gênero;
- busca secundária por publicadora;
- inserção de novos registros;
- detecção de identificadores duplicados;
- remoção lógica de registros;
- compactação do arquivo de dados;
- persistência dos índices em arquivos binários.

## Formato dos registros

Cada registro começa com um indicador de tamanho de 2 bytes. Em seguida, os campos são armazenados em texto e separados pelo caractere `|`:

```text
ID|nome|ano|gênero|publicadora|plataforma|
```

Exemplo:

```text
539|Minecraft|2011|Sandbox|Microsoft Studios|PC|
```

## Estruturas utilizadas

### Índice primário

Associa o identificador de cada jogo ao seu byte-offset em `games.dat`. Isso permite acessar diretamente o registro, sem percorrer todo o arquivo.

### Índices secundários

Os índices de gênero e publicadora armazenam o ponteiro para o início de uma cadeia na lista invertida.

### Lista invertida

Cada elo contém uma chave primária e o RRN do próximo elemento da mesma cadeia. O valor `-1` indica o final. Como os elos apontam para chaves primárias, e não diretamente para registros, a implementação utiliza late binding.

## Como executar

Coloque `games.dat` na mesma pasta de `programa.py` e execute os comandos a partir desse diretório.

### 1. Construir os índices

```bash
python programa.py -b
```

Essa etapa deve ser executada antes do processamento das operações. Os arquivos de índice existentes serão reconstruídos.

### 2. Executar buscas, inserções e remoções

```bash
python programa.py -e operacoes-exemplo.txt
```

O arquivo de operações contém um comando por linha:

| Comando | Operação | Exemplo |
| --- | --- | --- |
| `bp` | Busca pela chave primária | `bp 459` |
| `bs1` | Busca por gênero | `bs1 Hack and Slash` |
| `bs2` | Busca por publicadora | `bs2 CD Projekt RED` |
| `i` | Inserção de registro | `i <registro>` |
| `r` | Remoção lógica | `r 121` |

Exemplo de inserção:

```text
i 539|Minecraft|2011|Sandbox|Microsoft Studios|PC|
```

Ao final da execução, as alterações realizadas nos índices em memória são persistidas em disco.

### 3. Compactar o arquivo de dados

```bash
python programa.py -c
```

A compactação reescreve somente os registros válidos, elimina os espaços deixados pelas remoções lógicas e atualiza os byte-offsets do índice primário.

## Arquivos

```text
trabalho-1-indices/
├── README.md
├── programa.py
├── operacoes-exemplo.txt
└── games.dat
```

O `programa.py` gera os arquivos de índice e de lista invertida necessários à execução. Esses arquivos são derivados de `games.dat` e, por isso, devem permanecer fora do controle de versão.

## Observações

- O arquivo de operações deve seguir o formato apresentado acima.
- A remoção é lógica: o espaço físico só é recuperado durante a compactação.
- Atenção: as operações de inserção, remoção e compactação podem modificar o arquivo games.dat. Para preservar os dados originais durante os testes, utilize uma cópia do arquivo.
