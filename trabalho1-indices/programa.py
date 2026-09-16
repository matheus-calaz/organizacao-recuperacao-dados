import sys
import os
import struct

# Arquivos de dados e índices persistidos em disco.
FILE_GAMES = "games.dat"
FILE_PRIMARIO = "primario.ind"
FILE_GENERO = "genero.ind"
FILE_PUBLICADORA = "publicadora.ind"
FILE_LISTA = "listalnvertida.lst"


# Serialização e carregamento dos índices

def salvar_indice_primario(primario):
    """Persiste pares de chave primária e byte-offset em formato binário."""
    with open(FILE_PRIMARIO, 'wb') as f:
        for pk, offset in primario.items():
            pk_bytes = pk.encode('utf-8')
            f.write(struct.pack('<h', len(pk_bytes)))
            f.write(pk_bytes)
            f.write(struct.pack('<q', offset))


def carregar_indice_primario():
    """Reconstrói em memória o índice primário armazenado em disco."""
    primario = {}
    if not os.path.exists(FILE_PRIMARIO): return primario
    with open(FILE_PRIMARIO, 'rb') as f:
        while True:
            tamanho_bytes = f.read(2)
            if not tamanho_bytes: break
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            pk = f.read(tamanho).decode('utf-8')
            offset = struct.unpack('<q', f.read(8))[0]
            primario[pk] = offset
    return primario


def salvar_indice_secundario(indice, filename):
    """Persiste um índice secundário e os ponteiros para a lista invertida."""
    with open(filename, 'wb') as f:
        for chave, head in indice.items():
            chave_bytes = chave.encode('utf-8')
            f.write(struct.pack('<h', len(chave_bytes)))
            f.write(chave_bytes)
            f.write(struct.pack('<q', head))


def carregar_indice_secundario(filename):
    """Carrega um índice secundário de gênero ou publicadora para a memória."""
    indice = {}
    if not os.path.exists(filename): return indice
    with open(filename, 'rb') as f:
        while True:
            tamanho_bytes = f.read(2)
            if not tamanho_bytes: break
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            chave = f.read(tamanho).decode('utf-8')
            head = struct.unpack('<q', f.read(8))[0]
            indice[chave] = head
    return indice


def salvar_lista_invertida(lista):
    """Persiste os elos da lista invertida no formato (ID, próximo RRN)."""
    with open(FILE_LISTA, 'wb') as f:
        for pk, proximo in lista:
            pk_bytes = pk.encode('utf-8')
            f.write(struct.pack('<h', len(pk_bytes)))
            f.write(pk_bytes)
            f.write(struct.pack('<q', proximo))


def carregar_lista_invertida():
    """Carrega os elos da lista invertida para percorrer as cadeias em memória."""
    lista = []
    if not os.path.exists(FILE_LISTA): return lista
    with open(FILE_LISTA, 'rb') as f:
        while True:
            tamanho_bytes = f.read(2)
            if not tamanho_bytes: break
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            pk = f.read(tamanho).decode('utf-8')
            proximo = struct.unpack('<q', f.read(8))[0]
            lista.append((pk, proximo))
    return lista


# Acesso aos registros e operações principais

def ler_registro(arq, offset):
    """Lê diretamente um registro de tamanho variável a partir do byte-offset."""
    arq.seek(offset)
    tamanho_bytes = arq.read(2)
    if not tamanho_bytes: return None
    tamanho = struct.unpack('<h', tamanho_bytes)[0]
    registro_bytes = arq.read(tamanho)
    registro_str = registro_bytes.decode('utf-8', errors='ignore')
    return registro_str


def construir_indices():
    """Constrói os índices primário e secundários a partir do arquivo games.dat."""
    primario = {}
    genero_idx = {}
    pub_idx = {}
    lista_invertida = []
    with open(FILE_GAMES, 'rb') as f:
        while True:
            offset = f.tell()
            tamanho_bytes = f.read(2)
            if not tamanho_bytes:
                break
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            registro_bytes = f.read(tamanho)
            registro_str = registro_bytes.decode('utf-8', errors='ignore')
            campos = registro_str.split('|')
            if len(campos) < 6: continue
            pk = campos[0]
            genero = campos[3]
            pub = campos[4]

            # O índice primário associa o ID à posição física do registro.
            primario[pk] = offset

            # Late binding por gênero: o novo elo aponta para o antigo início da cadeia.
            ptr_atual_genero = len(lista_invertida)
            head_genero = genero_idx.get(genero, -1)
            lista_invertida.append((pk, head_genero))
            genero_idx[genero] = ptr_atual_genero

            # A publicadora utiliza a mesma lista invertida em uma cadeia independente.
            ptr_atual_pub = len(lista_invertida)
            head_pub = pub_idx.get(pub, -1)
            lista_invertida.append((pk, head_pub))
            pub_idx[pub] = ptr_atual_pub
    salvar_indice_primario(primario)
    salvar_indice_secundario(genero_idx, FILE_GENERO)
    salvar_indice_secundario(pub_idx, FILE_PUBLICADORA)
    salvar_lista_invertida(lista_invertida)
    print("Índices criados com sucesso.")


def executar_operacoes(arquivo_operacoes):
    """Executa, em sequência, as buscas, inserções e remoções do arquivo informado."""
    if not all(os.path.exists(f) for f in [FILE_GAMES, FILE_PRIMARIO, FILE_GENERO, FILE_PUBLICADORA, FILE_LISTA]):
        print("Erro: Arquivos de índice ou de dados não encontrados.")
        return
    primario = carregar_indice_primario()
    genero_idx = carregar_indice_secundario(FILE_GENERO)
    pub_idx = carregar_indice_secundario(FILE_PUBLICADORA)
    lista_invertida = carregar_lista_invertida()
    with open(FILE_GAMES, 'r+b') as f_games, open(arquivo_operacoes, 'r') as f_ops:
        for linha in f_ops:
            linha = linha.strip()
            if not linha: continue
            partes = linha.split(' ', 1)
            op = partes[0]
            arg = partes[1] if len(partes) > 1 else ""

            # Busca primária: acesso direto pelo byte-offset armazenado no índice.
            if op == 'bp':
                print(f'Busca pelo registro de ID "{arg}"')
                if arg in primario:
                    reg = ler_registro(f_games, primario[arg])
                    print(reg)
                else:
                    print("Registro não encontrado!")

            # Busca secundária por gênero (bs1) ou publicadora (bs2).
            elif op == 'bs1' or op == 'bs2':
                indice_alvo = genero_idx if op == 'bs1' else pub_idx
                tipo_busca = "gênero" if op == 'bs1' else "publicadora"
                head = indice_alvo.get(arg, -1)
                pks_encontrados = []
                ptr = head

                # Percorre a cadeia até o sentinela -1 e ignora registros removidos.
                while ptr != -1:
                    pk, prox = lista_invertida[ptr]
                    if pk in primario:
                        pks_encontrados.append(pk)
                    ptr = prox
                print(f'Busca por registros de {tipo_busca} "{arg}" ({len(pks_encontrados)} registros)')
                for pk in sorted(pks_encontrados):
                    reg = ler_registro(f_games, primario[pk])
                    print(reg)

            # Insere o registro no fim do arquivo e atualiza todos os índices em memória.
            elif op == 'i':
                campos = arg.split('|')
                pk = campos[0]
                if pk in primario:
                    print(f'Erro: ID {pk} duplicado.')
                else:
                    f_games.seek(0, os.SEEK_END)
                    offset = f_games.tell()
                    registro_bytes = arg.encode('utf-8')
                    tamanho = len(registro_bytes)
                    f_games.write(struct.pack('<h', tamanho))
                    f_games.write(registro_bytes)
                    primario[pk] = offset
                    genero = campos[3]
                    pub = campos[4]
                    ptr_atual_genero = len(lista_invertida)
                    head_genero = genero_idx.get(genero, -1)
                    lista_invertida.append((pk, head_genero))
                    genero_idx[genero] = ptr_atual_genero
                    ptr_atual_pub = len(lista_invertida)
                    head_pub = pub_idx.get(pub, -1)
                    lista_invertida.append((pk, head_pub))
                    pub_idx[pub] = ptr_atual_pub
                    print(f'Inserção do registro de chave "{pk}" ({tamanho} bytes)')

            # A remoção é lógica: somente a entrada do índice primário é descartada.
            elif op == 'r':
                if arg in primario:
                    offset = primario[arg]
                    del primario[arg]
                    print(f'Remoção do registro de chave "{arg}" (offset = {offset})')
                else:
                    print(f'Remoção do registro de chave "{arg}"')
                    print("Registro não encontrado!")

    # Persiste as alterações acumuladas durante a execução das operações.
    salvar_indice_primario(primario)
    salvar_indice_secundario(genero_idx, FILE_GENERO)
    salvar_indice_secundario(pub_idx, FILE_PUBLICADORA)
    salvar_lista_invertida(lista_invertida)


def compactar_arquivo():
    """Reescreve apenas registros válidos e atualiza seus novos byte-offsets."""
    if not os.path.exists(FILE_GAMES) or not os.path.exists(FILE_PRIMARIO):
        print("Erro: Arquivos necessários não encontrados para compactação.")
        return
    primario = carregar_indice_primario()
    TEMP_FILE = "games_temp.dat"
    novo_primario = {}
    with open(FILE_GAMES, 'rb') as f_old, open(TEMP_FILE, 'wb') as f_new:
        for pk in sorted(primario.keys()):
            offset_antigo = primario[pk]
            f_old.seek(offset_antigo)
            tamanho_bytes = f_old.read(2)
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            registro_bytes = f_old.read(tamanho)
            novo_offset = f_new.tell()
            f_new.write(struct.pack('<h', tamanho))
            f_new.write(registro_bytes)
            novo_primario[pk] = novo_offset

    # A substituição elimina fisicamente os espaços deixados por remoções lógicas.
    os.replace(TEMP_FILE, FILE_GAMES)
    salvar_indice_primario(novo_primario)
    print("Arquivo de registros compactado com sucesso.")


# Interface de linha de comando

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python programa.py [-b | -e operacoes.txt | -c]")
        sys.exit(1)
    flag = sys.argv[1]
    if flag == '-b':
        construir_indices()
    elif flag == '-e':
        if len(sys.argv) != 3:
            print("Erro: Arquivo de operações não fornecido. Uso: python programa.py -e operacoes.txt")
            sys.exit(1)
        executar_operacoes(sys.argv[2])
    elif flag == '-c':
        compactar_arquivo()
    else:
        print("Flag inválida. Use -b, -e ou -c.")
