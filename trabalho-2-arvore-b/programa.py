import sys
import os
import struct

# Configuração da Árvore-B e do layout binário das páginas.
ORDEM = 5
NULO = -1
TAM_CAB = 4
FORMATO_PAGINA = f"=i{ORDEM-1}i{ORDEM-1}i{ORDEM}i"
TAM_PAGINA = struct.calcsize(FORMATO_PAGINA)


class Pagina:
    """Representa uma página de tamanho fixo persistida em btree.dat."""

    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [NULO] * (ORDEM - 1)
        self.offsets: list = [NULO] * (ORDEM - 1)
        self.filhos: list = [NULO] * ORDEM


# Persistência das páginas e do cabeçalho

def lePagina(rrn: int) -> Pagina:
    """Localiza uma página pelo RRN e a reconstrói a partir do arquivo binário."""
    if rrn == NULO:
        return None
    offset_disco = TAM_CAB + rrn * TAM_PAGINA
    if not os.path.exists("btree.dat"):
        return None
    with open("btree.dat", "rb") as arqBtree:
        arqBtree.seek(offset_disco)
        dados = arqBtree.read(TAM_PAGINA)
        if len(dados) < TAM_PAGINA:
            return None
        unpacked = struct.unpack(FORMATO_PAGINA, dados)
        pag = Pagina()
        pag.numChaves = unpacked[0]
        idx = 1
        pag.chaves = list(unpacked[idx : idx + ORDEM - 1])
        idx += ORDEM - 1
        pag.offsets = list(unpacked[idx : idx + ORDEM - 1])
        idx += ORDEM - 1
        pag.filhos = list(unpacked[idx : idx + ORDEM])
        return pag


def escrevePagina(rrn: int, pag: Pagina) -> None:
    """Serializa uma página na posição de disco determinada por seu RRN."""
    offset_disco = TAM_CAB + rrn * TAM_PAGINA
    dados_para_empacotar = [pag.numChaves] + pag.chaves + pag.offsets + pag.filhos
    dados_dados = struct.pack(FORMATO_PAGINA, *dados_para_empacotar)
    modo = "r+b" if os.path.exists("btree.dat") else "wb"
    with open("btree.dat", modo) as arqBtree:
        arqBtree.seek(offset_disco)
        arqBtree.write(dados_dados)


def le_raiz_cabecalho() -> int:
    """Lê o RRN da raiz armazenado nos 4 bytes iniciais do arquivo."""
    if not os.path.exists("btree.dat"):
        return NULO
    with open("btree.dat", "rb") as arqBtree:
        dados = arqBtree.read(4)
        if len(dados) < 4:
            return NULO
        return struct.unpack("=i", dados)[0]


def atualiza_raiz_cabecalho(raiz_rrn: int) -> None:
    """Atualiza o RRN da raiz no cabeçalho do arquivo."""
    modo = "r+b" if os.path.exists("btree.dat") else "wb"
    with open("btree.dat", modo) as arqBtree:
        arqBtree.seek(0)
        arqBtree.write(struct.pack("=i", raiz_rrn))


def novo_rrn() -> int:
    """Calcula o próximo RRN disponível com base no tamanho de btree.dat."""
    if not os.path.exists("btree.dat"):
        return 0
    tamanho_arquivo = os.path.getsize("btree.dat")
    return (tamanho_arquivo - TAM_CAB) // TAM_PAGINA


# Busca e inserção na Árvore-B

def buscaNaPagina(chave: int, pag: Pagina) -> tuple:
    """Busca linear dentro de uma página específica."""
    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos


def buscaNaArvore(chave: int, rrn: int) -> tuple:
    """Busca recursivamente a chave, seguindo o filho correspondente em cada página."""
    if rrn == NULO:
        return False, NULO, NULO
    pag = lePagina(rrn)
    achou, pos = buscaNaPagina(chave, pag)
    if achou:
        return True, rrn, pos
    else:
        return buscaNaArvore(chave, pag.filhos[pos])


def insereNaPagina(chave: int, pos_offset: int, filhoD: int, pag: Pagina) -> None:
    """Insere ordenadamente uma chave, seu offset e o filho direito na página."""
    i = pag.numChaves
    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.offsets[i] = pag.offsets[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        i -= 1
    pag.chaves[i] = chave
    pag.offsets[i] = pos_offset
    pag.filhos[i + 1] = filhoD
    pag.numChaves += 1


def divide(chave: int, pos_offset: int, filhoD: int, pag: Pagina) -> tuple:
    """Divide uma página em overflow e retorna a chave promovida ao nível superior."""
    class TempPag:
        def __init__(self):
            self.numChaves = pag.numChaves
            self.chaves = pag.chaves + [NULO]
            self.offsets = pag.offsets + [NULO]
            self.filhos = pag.filhos + [NULO]
    temp = TempPag()
    i = temp.numChaves
    while i > 0 and chave < temp.chaves[i - 1]:
        temp.chaves[i] = temp.chaves[i - 1]
        temp.offsets[i] = temp.offsets[i - 1]
        temp.filhos[i + 1] = temp.filhos[i]
        i -= 1
    temp.chaves[i] = chave
    temp.offsets[i] = pos_offset
    temp.filhos[i + 1] = filhoD
    temp.numChaves += 1

    # O elemento central é promovido; os demais são distribuídos entre as páginas.
    meio = ORDEM // 2
    chavePro = temp.chaves[meio]
    offsetPro = temp.offsets[meio]
    filhoDpro = novo_rrn()
    pAtual = Pagina()
    pAtual.numChaves = meio
    for idx in range(meio):
        pAtual.chaves[idx] = temp.chaves[idx]
        pAtual.offsets[idx] = temp.offsets[idx]
    for idx in range(meio + 1):
        pAtual.filhos[idx] = temp.filhos[idx]
    pNova = Pagina()
    pNova.numChaves = temp.numChaves - meio - 1
    for idx in range(pNova.numChaves):
        pNova.chaves[idx] = temp.chaves[meio + 1 + idx]
        pNova.offsets[idx] = temp.offsets[meio + 1 + idx]
    for idx in range(pNova.numChaves + 1):
        pNova.filhos[idx] = temp.filhos[meio + 1 + idx]
    return chavePro, offsetPro, filhoDpro, pAtual, pNova


def insereNaArvore(chave: int, pos_offset: int, rrnAtual: int) -> tuple:
    """Insere recursivamente o par (chave, offset) e propaga promoções."""
    if rrnAtual == NULO:
        return chave, pos_offset, NULO, True
    pag = lePagina(rrnAtual)
    achou, pos = buscaNaPagina(chave, pag)
    if achou:
        raise ValueError("Chave duplicada")
    chavePro, offsetPro, filhoDpro, promo = insereNaArvore(chave, pos_offset, pag.filhos[pos])
    if not promo:
        return NULO, NULO, NULO, False
    if pag.numChaves < ORDEM - 1:
        insereNaPagina(chavePro, offsetPro, filhoDpro, pag)
        escrevePagina(rrnAtual, pag)
        return NULO, NULO, NULO, False
    else:
        chavePro, offsetPro, filhoDpro, pag, novapag = divide(chavePro, offsetPro, filhoDpro, pag)
        escrevePagina(rrnAtual, pag)
        escrevePagina(filhoDpro, novapag)
        return chavePro, offsetPro, filhoDpro, True


def gerenciadorDeInsercao(raiz: int, chave: int, pos_offset: int) -> tuple:
    """Coordena a inserção e cria uma nova raiz quando a promoção alcança o topo."""
    try:
        chavePro, offsetPro, filhoDpro, promocao = insereNaArvore(chave, pos_offset, raiz)
        if promocao:
            pNova = Pagina()
            pNova.chaves[0] = chavePro
            pNova.offsets[0] = offsetPro
            pNova.filhos[0] = raiz
            pNova.filhos[1] = filhoDpro
            pNova.numChaves = 1
            nova_raiz_rrn = novo_rrn()
            escrevePagina(nova_raiz_rrn, pNova)
            raiz = nova_raiz_rrn
            atualiza_raiz_cabecalho(raiz)
        return raiz, True
    except ValueError:
        return raiz, False


# Acesso direto ao arquivo de registros

def ler_registro_games(offset: int) -> tuple:
    """Acessa diretamente o arquivo games.dat via byte-offset e lê o registro."""
    if not os.path.exists("games.dat"):
        return None, 0
    with open("games.dat", "rb") as fg:
        fg.seek(offset)
        len_bytes = fg.read(2)
        if len(len_bytes) < 2:
            return None, 0

        # Aceita o indicador de tamanho nas duas ordens de bytes previstas.
        size = int.from_bytes(len_bytes, byteorder="little")
        if size > 2000 or size <= 0:
            size = int.from_bytes(len_bytes, byteorder="big")
        record_bytes = fg.read(size)
        record_str = record_bytes.decode("utf-8", errors="ignore").strip()
        return record_str, size


# Modos de execução

def modo_criacao():
    """Cria a árvore-B do zero a partir do games.dat (Opção -b)."""
    if not os.path.exists("games.dat"):
        print("Erro: Arquivo 'games.dat' obrigatorio nao encontrado.")
        sys.exit(1)
    atualiza_raiz_cabecalho(0)
    p_vazia = Pagina()
    escrevePagina(0, p_vazia)
    raiz = 0
    with open("games.dat", "rb") as fg:
        while True:
            offset_atual = fg.tell()
            len_bytes = fg.read(2)
            if not len_bytes or len(len_bytes) < 2:
                break
            size = int.from_bytes(len_bytes, byteorder="little")
            if size > 2000 or size <= 0:
                size = int.from_bytes(len_bytes, byteorder="big")
            dados_registro = fg.read(size)
            string_registro = dados_registro.decode("utf-8", errors="ignore")
            if not string_registro:
                break
            partes = string_registro.split("|")

            # A primeira posição do registro contém a chave primária numérica.
            if len(partes) > 0 and partes[0].strip().isdigit():
                game_id = int(partes[0].strip())
                raiz, sucesso = gerenciadorDeInsercao(raiz, game_id, offset_atual)
    print("O indice (Arvore-B) foi criado com sucesso!")


def modo_execucao(nome_arq_ops: str):
    """Executa um arquivo sequencial de operações de busca e inserção (Opção -e)."""
    if not os.path.exists("games.dat") or not os.path.exists("btree.dat"):
        print("Erro: Os arquivos 'games.dat' e 'btree.dat' devem existir para este modo.")
        sys.exit(1)
    if not os.path.exists(nome_arq_ops):
        print(f"Erro: Arquivo de operacoes '{nome_arq_ops}' nao encontrado.")
        sys.exit(1)
    with open(nome_arq_ops, "r", encoding="utf-8", errors="ignore") as fops:
        linhas = fops.readlines()
    raiz = le_raiz_cabecalho()
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        op_tipo = linha[0]
        argumento = linha[2:].strip()
        if op_tipo == "b":
            chave_busca = int(argumento)
            print(f"Busca pelo registro de chave \"{chave_busca}\"")
            achou, rrn_encontrado, pos_encontrada = buscaNaArvore(chave_busca, raiz)
            if achou:
                pag = lePagina(rrn_encontrado)
                offset_game = pag.offsets[pos_encontrada]
                rec_str, rec_size = ler_registro_games(offset_game)
                print(f"{rec_str} ({rec_size} bytes offset {offset_game})")
            else:
                print(f"Erro: chave \"{chave_busca}\" não encontrada")
        elif op_tipo == "i":
            if "|" in argumento:
                game_id = int(argumento.split("|")[0].strip())
            else:
                game_id = int(argumento.split()[0].strip())
            print(f"Inserção do registro de chave \"{game_id}\"")
            achou, _, _ = buscaNaArvore(game_id, raiz)
            if achou:
                print(f"Erro: chave \"{game_id}\" duplicada")
            else:

                # O registro é acrescentado ao fim de games.dat antes da indexação.
                with open("games.dat", "a+b") as fg:
                    fg.seek(0, os.SEEK_END)
                    novo_offset = fg.tell()
                    bytes_registro = argumento.encode("utf-8")
                    tamanho_reg = len(bytes_registro)
                    fg.write(tamanho_reg.to_bytes(2, byteorder="little"))
                    fg.write(bytes_registro)

                # A Árvore-B associa a chave ao byte-offset recém-calculado.
                raiz, sucesso = gerenciadorDeInsercao(raiz, game_id, novo_offset)
                print(f"{argumento} ({tamanho_reg} bytes offset {novo_offset})")
    print(f"As operacoes do arquivo \"{nome_arq_ops}\" foram executadas com sucesso!")


def modo_impressao():
    """Apresenta na tela os dados internos de todas as páginas ordenadas por RRN (Opção -p)."""
    if not os.path.exists("btree.dat"):
        print("Erro: Arquivo 'btree.dat' nao existe.")
        sys.exit(1)
    raiz = le_raiz_cabecalho()
    total_paginas = novo_rrn()
    if total_paginas == 0 and raiz == NULO:
        print("Arvore-B vazia.")
        return
    for rrn in range(total_paginas):
        pag = lePagina(rrn)
        if pag is None:
            continue
        print(f"Pagina {rrn}:")
        print("Chaves = " + " | ".join(str(c) for c in pag.chaves))
        print("Offsets = " + " | ".join(str(o) for o in pag.offsets))
        print("Filhos = " + " | ".join(str(f) for f in pag.filhos))
        if rrn == raiz:
            print("Raiz")
        print()


# Interface de linha de comando

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso incorreto. Utilize as flags:")
        print("  python programa.py -b")
        print("  python programa.py -e nome_arquivo_operacoes")
        print("  python programa.py -p")
        sys.exit(1)
    flag = sys.argv[1]
    if flag == "-b":
        modo_criacao()
    elif flag == "-e":
        if len(sys.argv) < 3:
            print("Erro: Especifique o arquivo de operacoes. Ex: python programa.py -e operacoes.txt")
            sys.exit(1)
        modo_execucao(sys.argv[2])
    elif flag == "-p":
        modo_impressao()
    else:
        print(f"Flag '{flag}' inválida ou desconhecida.")
