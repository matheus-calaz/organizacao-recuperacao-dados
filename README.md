# Organização e Recuperação de Dados

Projetos acadêmicos desenvolvidos em Python na disciplina de **Organização e Recuperação de Dados**, do curso de Ciência da Computação da Universidade Estadual de Maringá (UEM).

O repositório reúne duas implementações voltadas ao armazenamento persistente, à indexação e à recuperação eficiente de registros de tamanho variável em arquivos binários.

## Projetos

| Projeto | Principais conceitos |
| --- | --- |
| [Trabalho 1 — Índices e lista invertida](./trabalho-1-indices/) | Índice primário, índices secundários, lista invertida, late binding, byte-offsets, remoção lógica e compactação |
| [Trabalho 2 — Árvore-B](./trabalho-2-arvore-b/) | Árvore-B persistida em disco, páginas de tamanho fixo, RRNs, busca, inserção, split e promoção de chaves |

## Tecnologias e conhecimentos aplicados

- Python;
- manipulação de arquivos binários;
- serialização com o módulo `struct`;
- registros de tamanho variável;
- acesso direto por byte-offset;
- estruturas de dados e algoritmos de busca;
- persistência e reconstrução de índices em disco.

## Estrutura do repositório

```text
organizacao-recuperacao-dados/
├── README.md
├── .gitignore
├── trabalho-1-indices/
│   ├── README.md
│   ├── programa.py
│   ├── operacoes-exemplo.txt
│   └── games.dat
└── trabalho-2-arvore-b/
    ├── README.md
    ├── programa.py
    ├── operacoes-exemplo.txt
    └── games.dat
```

## Pré-requisitos

- Python 3;
- arquivo binário `games.dat` compatível com o formato utilizado na disciplina.

Não são necessárias bibliotecas externas.

## Execução

Cada trabalho possui comandos e operações próprios. Consulte o `README.md` da pasta correspondente para ver as instruções completas e o formato esperado dos arquivos.

## Autor

**Matheus Calazans**  
Ciência da Computação — Universidade Estadual de Maringá

- [GitHub](https://github.com/matheus-calaz)
- [LinkedIn](https://www.linkedin.com/in/matheus-am-calazans)

