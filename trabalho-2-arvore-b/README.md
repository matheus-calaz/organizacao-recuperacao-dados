# Trabalho 2 — Árvore-B

Implementação de uma **Árvore-B persistida em arquivo binário** para indexar registros de jogos armazenados em `games.dat`.

Cada chave da árvore é associada ao byte-offset do registro correspondente. Dessa forma, a Árvore-B localiza a chave e o programa acessa diretamente o registro no arquivo de dados.

## Funcionalidades

- construção da Árvore-B a partir de `games.dat`;
- persistência de páginas de tamanho fixo em `btree.dat`;
- armazenamento do RRN da raiz no cabeçalho do arquivo;
- busca recursiva por chave;
- inserção ordenada;
- prevenção de chaves duplicadas;
- divisão de páginas em overflow;
- promoção de chaves;
- criação de uma nova raiz quando necessário;
- impressão da estrutura interna da árvore.

## Organização do arquivo da árvore

Os 4 primeiros bytes de `btree.dat` armazenam o RRN da raiz. Depois do cabeçalho, cada página ocupa uma posição fixa e contém:

- quantidade de chaves válidas;
- chaves primárias;
- byte-offsets dos registros;
- RRNs das páginas filhas.

A implementação utiliza uma Árvore-B de ordem 5. Portanto, cada página armazena até 4 chaves e 5 referências para filhos.

## Formato dos registros

Cada registro de `games.dat` começa com um indicador de tamanho de 2 bytes e utiliza o seguinte formato:

```text
ID|nome|ano|gênero|publicadora|plataforma|
```

## Como executar

Coloque `games.dat` na mesma pasta de `programa.py` e execute os comandos a partir desse diretório.

### 1. Construir a Árvore-B

```bash
python programa.py -b
```

O programa percorre `games.dat`, obtém a chave primária e o byte-offset de cada registro e cria `btree.dat`.

### 2. Executar buscas e inserções

```bash
python programa.py -e operacoes-exemplo.txt
```

O arquivo contém uma operação por linha:

| Comando | Operação | Exemplo |
| --- | --- | --- |
| `b` | Busca pela chave primária | `b 220` |
| `i` | Inserção de um novo registro | `i <registro>` |

Exemplo de inserção:

```text
i 14|The Last of Us|2013|Action-Adventure|Sony|PlayStation 3|
```

Durante uma inserção válida, o registro é acrescentado ao final de `games.dat` e sua chave é inserida na Árvore-B com o byte-offset correspondente.

### 3. Imprimir as páginas da árvore

```bash
python programa.py -p
```

Esse modo apresenta as chaves, os offsets e os filhos de cada página em ordem de RRN, além de identificar a raiz.

## Fluxo de inserção

1. A árvore é percorrida recursivamente até a página adequada.
2. Se houver espaço, a chave é inserida em ordem.
3. Se a página estiver cheia, ocorre o split.
4. A chave central é promovida ao nível superior.
5. Caso a promoção ultrapasse a raiz, uma nova raiz é criada.

## Arquivos

```text
trabalho-2-arvore-b/
├── README.md
├── programa.py
├── operacoes-exemplo.txt
└── games.dat
```

O arquivo `btree.dat` é gerado pelo programa e não deve ser versionado.

## Observações

- Execute a construção da árvore antes de processar o arquivo de operações.
- O programa utiliza apenas módulos da biblioteca padrão do Python.
- Atenção: as operações de inserção, remoção e compactação podem modificar o arquivo games.dat. Para preservar os dados originais durante os testes, utilize uma cópia do arquivo.
