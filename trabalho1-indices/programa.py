import sys
import os
import struct

# Nomes dos arquivos de índice e dados
FILE_GAMES = "games.dat"
FILE_PRIMARIO = "primario.ind"
FILE_GENERO = "genero.ind"
FILE_PUBLICADORA = "publicadora.ind"
FILE_LISTA = "listalnvertida.lst" 

# --- FUNÇÕES DE SERIALIZAÇÃO DE ÍNDICES ---
# estrutura simples (binária) para armazenar os listas e a lista.

def salvar_indice_primario(primario): #primário é o índice lógico
    """
    Essa função percorre a lista do índice primário em memória
    e o grava no arquivo binário primario.ind. Para cada entrada, 
    ela salva o tamanho da chave (2 bytes),
    a string da chave (ID) e o seu respectivo byte-offset (8 bytes) no arquivo de dados.
    """
    with open(FILE_PRIMARIO, 'wb') as f: #abre para escrita binária e fecha o arquivo 
        for pk, offset in primario.items(): #vai percorrer cada um dos itens do lista
            # pk é a chave primária (ex: ID do jogo)
            # offset é o endereço físico (byte-offset)
            
            pk_bytes = pk.encode('utf-8') # transforma o texto do ID em bytes
            
            f.write(struct.pack('<h', len(pk_bytes))) # Grava o tamanho da chave (2 bytes)
            # a ´´<´´ significa que está usando o little-endian
            # o ´´h´´ serve para formatar o número como um inteiro de 2 bytes (short)
            # o ´´len´´ é utilizado para salvar quantos bytes o ID tem
            
            f.write(pk_bytes) # Chave
            # vai escrever no arquivo o conteúdo da chave primária
            
            f.write(struct.pack('<q', offset))# Grava a posição física Offset (8 bytes long long)
            # o ´´q´´ vai formatar o offset em um inteiro de 8 bytes (long(4) + long(4))
            # é utilizado 8 bytes pois comporta arquivos enormes sem ter erros
            # ´´Para achar esse ID, vá para essa posição no aquivo de dados

def carregar_indice_primario():
# vai ´´trazer´´ o mapa que está guardado no disco para a RAM, pra encontrar os jogos sem ler o arquivoi games.dat
# vai reconstruir o índice primário em memória
    """
    Realiza a leitura do arquivo primario.ind, reconstruindo a lista em RAM.
    Ela lê sequencialmente os indicadores de tamanho para saber quantos bytes de string 
    deve processar para cada ID e recupera os offsets.
    """
    primario = {} #dicionário vazio
    # cada entrada será um par {Chave primária e Endereço físico}

    if not os.path.exists(FILE_PRIMARIO): return primario
    # vai verificar se o arquivo físico está realmente presente no disco, se não existir apenas retorna o lista vazio

    with open(FILE_PRIMARIO, 'rb') as f:
    # vai abrir o arquivo em modo de leitura binária e depois fechá-lo

        while True:
        # faz com que rode até chegar ao final do arquivo

            tamanho_bytes = f.read(2)
            # vai tentar ler o 2 primeiros bytes para saber o ´´tamanho´´ do que vem a seguir

            if not tamanho_bytes: break
            # faz com que a leitura pare caso a função read(2) não consiga ler mais nada, ou seja, final do arquivo

            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            # vai pegar os bytes e converter para a forma que o Python entende
            # o ´´<h´´ indica que deve ser lido como um inteiro de 2 bytes (short)

            pk = f.read(tamanho).decode('utf-8')
            # sabendo o tamanho exato do ID (variável tamanho) utiliza-se o read para pegar todas as letras do ID de uma vez só
            # converte a sequencia de bytes de volta para a chave primária

            offset = struct.unpack('<q', f.read(8))[0]
            # depois do ID os próximos 8 bytes guardam o byte_offset
            # o ´´<q´´ vai converter os 8 bytes para um inteiro e vai dizer em qual byte do arquivo o jogo começa

            primario[pk] = offset
            # guarda o par no lista 

    return primario
    #fornece o dicionário completo ao final

def salvar_indice_secundario(indice, filename):
    # serve para gênero e publicadora
    # o índice é a lista que está na RAM e a chave é o texto e o valor é o head
    # filename é o nome do arquivo onde os dados estarão salvos (genero.ind e publicadora.ind)

    """
    Uma função genérica usada para salvar tanto o índice de gênero quanto o de publicadora.
    Ela grava a chave secundária e um ponteiro (cabeça) que indica onde começa a lista de IDs
    associados a essa chave no arquivo de lista invertida.
    """
    with open(filename, 'wb') as f:
        #abre o arquivo para escrita em binário

        for chave, head in indice.items():
        # percorre as categorias indexadas
        # chave é o termo secundário (genero ou publicadora)
        # head é o ponteiro para a lista invertida

            chave_bytes = chave.encode('utf-8')
            # transforma o texto da categoria em bytes para que seja gravado

            f.write(struct.pack('<h', len(chave_bytes)))
            # grava primeiro um número de 2 bytes (´´h´´) para informar o tamanho do nome que vem a seguir

            f.write(chave_bytes)
            # grava o nome da categoria logo após o seu tamanho
    
            f.write(struct.pack('<q', head)) # Ponteiro para a lista invertida (8 bytes)
            # <q grava o valor do head como inteiro de 8 bytes (long-long)
            # esse valor é fundamental para o Late Binding, pois, não vai apontar para o endereço mas sim para o primeiro ´´elo´´ da corrente no arquivo

def carregar_indice_secundario(filename):
# vai receber o parâmetro filename que vai ser o nome do arquivo de índices à ser carregado

    """
    Abre os arquivos .ind secundários e reconstrói as estruturas em memória para permitir
    buscas rápidas por gênero ou publicadora.
    """
    indice = {}
    # dicionário vazio

    if not os.path.exists(filename): return indice
    # vai verifica se o arquivo existe, caso ainda não tenha sido usado o -b, vai retornar o dicionário vazio

    with open(filename, 'rb') as f:
    # abre o aarquivo em leitura binária

        while True:
        # vai ler até não encontrar mais dados à serem lidos

            tamanho_bytes = f.read(2)
            # indica o tamanho uilizando os 2 primeiro bytes para ´´mostrar´´ o tamanho do que vem a seguir

            if not tamanho_bytes: break
            # se a função read não retornar nada a leitura irá parar

            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            # vai traduzir os dados e indica que o dado é um inteiro de 2 bytes(short) gravado em little-endian

            chave = f.read(tamanho).decode('utf-8')
            # agora que já sabe o tamanho exato do nome, vai ler a quantidade correta de bytes
            # o decode vai converter os bytes de volta para o texto original

            head = struct.unpack('<q', f.read(8))[0]
            # depois do nome, vai ler os próximos 8 bytes
            # o <q vai traduzir esses bytes para um inteiro long-long 

            indice[chave] = head
            # guarda na lista a relação entre a categoria e o ponteiro de início, pra facilitar na hora de buscar por um genero por exemplo


    return indice 
    # finaliza devolvendo o índice secundário pronto

def salvar_lista_invertida(lista):
# lista vai conter pares no formato {Cheve Primária, Ponteiro para o próximo}

    """
    Grava as entradas da lista invertida no arquivo listalnvertida.lst.
    Cada entrada contém o ID do jogo e o ponteiro para a próxima ocorrência daquela mesma chave secundária,
    seguindo a lógica de encadeamento.
    """
    with open(FILE_LISTA, 'wb') as f:
    # abre o arquivo que está em FILE_LISTA em modo de escrita binario 

        for pk, proximo in lista:
        # parcorre todos os elementos da lista invertida
        # pk é a chave primária (ID jogo)
        # proximo indica o RRN ou posição do próximo jogo, se for o último, terá o valor de -1

            pk_bytes = pk.encode('utf-8')
            # transforma o texto do ID em bytes

            f.write(struct.pack('<h', len(pk_bytes)))
            # converto o comprimento do ID em um binário de 2 bytes (short) em formato little-endian

            f.write(pk_bytes)
            # grava os bytes reais do ID do jogo logo após seu tamanho

            f.write(struct.pack('<q', proximo))
            # grava o valor de proximo como um inteiro de 8 bytes (long-long)

def carregar_lista_invertida():
# Função para reconstruir a lista invertida

    """
    Carrega todos os elos da lista invertida para a memória principal,
    permitindo que o programa percorra as cadeias de chaves primárias durante buscas secundárias.
    """
    lista = []
    # cria uma lista vazia para armazenar os pares de dados {Id do jogo, ponteiro para o próximo}
    # lista criad pois é necessário manter a ordem das posições (RRN) da lista invertida

    if not os.path.exists(FILE_LISTA): return lista
    # vai retornar a lista vazia se não tiver sido executada a construção dos índices

    with open(FILE_LISTA, 'rb') as f:
    # abre o arquivo da lista invertida em modo de leitura em binário

        while True:
        # inicia um laço de repetição que só vai parar quando o arquivo termina

            tamanho_bytes = f.read(2)
            # vai ler os 2 primeiros bytes de entrada (os dois bytes sçao os indicadores do tamanho do texto)

            if not tamanho_bytes: break
            # se o read(2) não retornar nada é o fim do arquivo

            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            # traduz os 2 bytes lidos para um número inteiro curto (short) no formato little-endian

            pk = f.read(tamanho).decode('utf-8')
            # lê a quantidade exata de bytes do ID e usa o decode para transformar os bytes em texto

            proximo = struct.unpack('<q', f.read(8))[0]
            # lê os próximos 8 bytes e converte em um long-long, sendo esse o ponteiro de encadeamento, que vai indicar e qual posição da lista está o próximo jogo
        
            lista.append((pk, proximo))
            # guarda o par (ID, Ponteiro)

    return lista 
    #retorna a lista completa para uso

# --- FUNÇÕES PRINCIPAIS ---

def ler_registro(arq, offset):
# acesso direto em arquivos de tamanho variável
# vai receber o objeto do arquivo (arq) e a posição exata em bytes onde o jogo começa (offset)

    """
    Esta função é responsável pelo acesso direto ao arquivo games.dat.
    Ela move o ponteiro para o offset desejado, lê os 2 bytes que indicam o tamanho do registro e,
    em seguida, lê exatamente aquela quantidade de bytes para retornar a string do jogo.
    """
    arq.seek(offset)
    # execução do acesso direto
    # com o .seek da pra mover o ponteiro direto para o endereço fornecido

    tamanho_bytes = arq.read(2)
    # vai ler os 2 primeiros bytes do registro, que são os que servem para indicar o tamanho

    if not tamanho_bytes: return None
    # caso o read não retorne nada é porque o ponteiro chegou ao fonal do arquivo
    # retorna None para evitar erros

    tamanho = struct.unpack('<h', tamanho_bytes)[0]
    # vai converter os 2 bytes binários em um npumero inteiro
    # o <h indica que o dado é um inteiro de 2 bytes (short) e o < indica que a leitura está sendo feita em little-endian
    # quero apenas o primeiro valor
    
    registro_bytes = arq.read(tamanho)
    # como já temos quantos bytes o jogo ocupa, essa segunda leitura é feita para pegar os dados reais do registro do jogo

    registro_str = registro_bytes.decode('utf-8', errors='ignore')
    # o decode vai transformar os dados de binário para um texto normal
    # caso existam caracteres estranhos no arquivo binário, o errors vai ignorá-los para continuar a rodar

    return registro_str
    # retorna uma string do registro

def construir_indices():
# vai ler o games.dat e criar o índice primário, secundário e a lista invertida
    """
    Funcionalidade: -b (Construção dos índices)
    Implementa a funcionalidade de criação das estruturas do zero. 
    Ela lê o arquivo de dados sequencialmente, captura a posição física de cada jogo,
    o índice primário e as listas invertidas.
    """
    primario = {}
    genero_idx = {}
    pub_idx = {}
    # os dicionários vão guardar os índices primários e secundários 

    lista_invertida = []
    # armazenar temporáriamente os elos da lista invertida antes de serem salvos no disco
    
    with open(FILE_GAMES, 'rb') as f:
    # abre o arquivo games.dat para leitura binária, Funciona como um acesso sequencial para mapear onde está cada jogo

        while True:
        # percorreo o arquivo de registro até o final

            offset = f.tell()
            # o tell() vai pegar a posição exata (em bytes) onde o registro começa e vai guardar esse valor na variável offset

            tamanho_bytes = f.read(2)
            # vai ler o indicador de tamanho de 2 bytes

            if not tamanho_bytes:
                break
            # se o read não retornar nada, para a execução pois chegou ao final do arquivo

            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            # vai ler o indicador de tamanho de 2 bytes
            # o unpack vai traduzir o binário para um inteiro
            # o <h indica que o dado é um inteiro de 2 bytes (short) e o < indica que a leitura está sendo feita em little-endian
            # quero apenas o primeiro valor

            registro_bytes = f.read(tamanho)
            # vai ler a quantidade exata de bytes do registro

            registro_str = registro_bytes.decode('utf-8', errors='ignore')
            # também vai ler a quantidade de bytes do registro, mas vai também traduzir os bytes e caso encontre algum erro no arquivo com os bytes vai ignorar
            
            campos = registro_str.split('|')
            # vai separar os dados do jogo utilizando a barra reta

            if len(campos) < 6: continue
            # se a quantidade de elementos na variável campos for menor que 6, vai pular o restante do código desta repetição e vai para o próximo item.
            
            pk = campos[0]
            genero = campos[3]
            pub = campos[4]
            # vão extrair a chave primária e as chaves secundárias respectivamente

            primario[pk] = offset
            # atualiza índice primário ´´para tal ID, o dado está em tal posição´´
            
            # Atualiza índice secundário de Gênero (Late Binding)
            ptr_atual_genero = len(lista_invertida)
            # identifica qual será a posição do novo elo do arquivo de lista invertida

            head_genero = genero_idx.get(genero, -1)
            # tenta buscar o ID do jogo anterior e caso seja o primeiro vai receber o -1

            lista_invertida.append((pk, head_genero))
            # guarda o ID atual e aponta para o jogo anterior da mesma categoria (encadeamento)

            genero_idx[genero] = ptr_atual_genero
            # # atualizao índice de gênero para apontar para o novo jogo, que vai ser o topo da lista

            
            # Atualiza índice secundário de Publicadora (Late Binding), vai ser a mesma coisa que gênero, mas, agora para publicadora
            ptr_atual_pub = len(lista_invertida)
            head_pub = pub_idx.get(pub, -1)
            lista_invertida.append((pk, head_pub))
            pub_idx[pub] = ptr_atual_pub

    # Sobrescreve os arquivos de índice, com as funções abaixo e grava nos respectivos arquivos
    salvar_indice_primario(primario)
    salvar_indice_secundario(genero_idx, FILE_GENERO)
    salvar_indice_secundario(pub_idx, FILE_PUBLICADORA)
    salvar_lista_invertida(lista_invertida)
    print("Índices criados com sucesso.")

def executar_operacoes(arquivo_operacoes):
# vai receber o caminho do arquivo de operções

    """
    Funcionalidade: -e (Execução de operações)
    Cuida do processamento do arquivo de texto contendo os comandos (busca, inserção ou remoção).
    Antes de começar, ela verifica a existência dos arquivos necessários e carrega os índices para a RAM
    """
    # Verifica a existência dos arquivos
    if not all(os.path.exists(f) for f in [FILE_GAMES, FILE_PRIMARIO, FILE_GENERO, FILE_PUBLICADORA, FILE_LISTA]):
        print("Erro: Arquivos de índice ou de dados não encontrados.")
        return
    # vai checar se o arquivo de operações está presente, caso não esteja vai parar a execução

    primario = carregar_indice_primario()
    genero_idx = carregar_indice_secundario(FILE_GENERO)
    pub_idx = carregar_indice_secundario(FILE_PUBLICADORA)
    lista_invertida = carregar_lista_invertida()
    # vai ler todos os arquivos de índice e vai colocar na RAM, facilitando a leitura e gravação
    
    with open(FILE_GAMES, 'r+b') as f_games, open(arquivo_operacoes, 'r') as f_ops:
    # abre o arquivo games.dat em modo de leitura binária, e o arquivo de operações em modo de leitura de texto

        for linha in f_ops:
            linha = linha.strip()
            if not linha: continue
        # vai passar linha por linha no arquivo de comandos, vai remover os espaços em branco nas pontas (strip()), e vai ignorar as linhas vazias
            
            partes = linha.split(' ', 1)
            op = partes[0]
            arg = partes[1] if len(partes) > 1 else ""
            # quebra o comando no primeiro espaço vazio, o que ficar do lado esquerdo é a operação (ex: bp) e do lado direito e o argumento (ex: Id do jogo)
            
            if op == 'bp': # Busca primária
                print(f'Busca pelo registro de ID "{arg}"')
                if arg in primario:
                    reg = ler_registro(f_games, primario[arg])
                    print(reg)
                else:
                    print("Registro não encontrado!")
            # se a operação for bp (busca primária), vai procurar a chave primária (arg), no dicionário primario.
            # se existir esse dicionário, vai pegar o valor associado (byte-offset), e ´´pula´´ direto para esse byte usando a função ler_registro e no fianl imprime os dados
                    
            elif op == 'bs1' or op == 'bs2': # Busca secundária
                indice_alvo = genero_idx if op == 'bs1' else pub_idx
                tipo_busca = "gênero" if op == 'bs1' else "publicadora"
                head = indice_alvo.get(arg, -1)
                #procura o termo desejado (ex: ação) no índice e se achar vai retornar o head que indica onde a lista desse gênero ou publicadora começa na lista invertida, caso não ache retorna -1
                pks_encontrados = []
            # identifica qual índice secundário vai ser utilizado
                
                # Percorre a lista invertida
                ptr = head
                while ptr != -1:
                # vai passar de ponteiro em ponteiro(ptr) até achar o -1 (fim da lista)

                    pk, prox = lista_invertida[ptr]
                    # O índice não vai apontar para o byte do arquivo, vai apontar para a chave primária (pk) (late binding)

                    if pk in primario:
                        pks_encontrados.append(pk)
                    ptr = prox
                    # verifica se o registro não foi apagado e se ele existir vai guardar a chave primária na lista
                
                print(f'Busca por registros de {tipo_busca} "{arg}" ({len(pks_encontrados)} registros)')
                for pk in sorted(pks_encontrados):
                    reg = ler_registro(f_games, primario[pk])
                    print(reg)
                # ordena as chaves primárias encontradas, pega o byte-offset de cada uma no primario, e vai no disco (f_games) pegar os dados reais
                    
            elif op == 'i': # Inserção
                campos = arg.split('|')
                pk = campos[0]
                if pk in primario:
                    print(f'Erro: ID {pk} duplicado.')
                else:
                    # Vai para o fim do arquivo
                    f_games.seek(0, os.SEEK_END)
                    offset = f_games.tell()
            # essa parte vai separa os campos com a barra reta e varifricar se a chave primária existe (para não duplicar)
            # se for uma nova, usa o .seek(0, os.SEEK_END) para pular para o final do arquivo de dados
            # o tell() é usado para descobrir em qual byte exato estamos (esse será o byte-offset)
                    
                    registro_bytes = arg.encode('utf-8')
                    tamanho = len(registro_bytes)
                    f_games.write(struct.pack('<h', tamanho))
                    f_games.write(registro_bytes)
                    # essa parte vai converter a string do registyro para bytes.
                    # calcula o tamanho do registro e grava os 2 primeiros bytes (<h, indica o tamanho, little-endian e short)
                    # utiliza o módulo struct seguido pelos dados do jogo
                    # é a estrutura de registros de tamanho variável
                    
                    primario[pk] = offset
                    genero = campos[3]
                    pub = campos[4]
                    # vai adicionar a nova chave primária e seu offset no índice primário da memória e no secundário respectivamente
                    
                    # Atualiza índice secundário de Gênero
                    ptr_atual_genero = len(lista_invertida)
                    # o novo elemento é colocado no final do arquivo

                    head_genero = genero_idx.get(genero, -1)
                    # o ponteiro proximo aponta para o antigo primeiro elemento de um determinado gênero

                    lista_invertida.append((pk, head_genero))
                    genero_idx[genero] = ptr_atual_genero # o índice de gênero é atualizado para apontar para a posição do novo elemento
                    # essa parte vai atualizar a lista invertida 
                    # a iserção é feita no inicio da lista                     
                    
                    # Atualiza índice secundário de Publicadora (funciona igual a parte anterior que era pra gênero)
                    ptr_atual_pub = len(lista_invertida)
                    head_pub = pub_idx.get(pub, -1)
                    lista_invertida.append((pk, head_pub))
                    pub_idx[pub] = ptr_atual_pub
                    
                    print(f'Inserção do registro de chave "{pk}" ({tamanho} bytes)') # mostra que foi feita a iserção

            elif op == 'r': # Remoção Lógica
                if arg in primario:
                    offset = primario[arg]
                    del primario[arg] # Remoção lógica apenas no primário 
                    print(f'Remoção do registro de chave "{arg}" (offset = {offset})')
            # vai remover o registro apagando a chave apenas no índice primário
            # quando a busca secundária tentar achar essa chave primária, o if arg in primário será falso e o registro apagado vai ser ignorado

                else:
                    print(f'Remoção do registro de chave "{arg}"')
                    print("Registro não encontrado!")
                    
    # Atualiza os arquivos no dispositivo de armazenamento 
    salvar_indice_primario(primario)
    salvar_indice_secundario(genero_idx, FILE_GENERO)
    salvar_indice_secundario(pub_idx, FILE_PUBLICADORA)
    salvar_lista_invertida(lista_invertida)
    # quando o arquivo de operações terminar de ser lido (´´for´´ acabar), a função vai pegar todos os índices que foram alterados e regrava-los de volta nos arquivos físicos para salvar as alterações

def compactar_arquivo():
# vai atualizar o arquivo games.dat para que fiquem apenas os registros que não foram removidos logicamente, elimina a fragmentação externa
    """
    Funcionalidade: -c (Compactação)
    Elimina a fragmentação externa causada por remoções lógicas.
    Ela reescreve apenas os registros válidos em um novo arquivo e, obrigatoriamente, reconstrói o índice primário,
    já que as posições físicas (offsets) de todos os jogos vão mudar.
    """
    if not os.path.exists(FILE_GAMES) or not os.path.exists(FILE_PRIMARIO):
        print("Erro: Arquivos necessários não encontrados para compactação.")
        return
    # se o arquivo nçao existir vai exibir essa mensagem de erro
    # a compactação le os dados originais e usa o índice primário como um guia
        
    primario = carregar_indice_primario()
    # carrega o dicionário para a RAM
    # como na remoção é retirado os índices primários, esse dicionário só vai conter os registros válidos

    TEMP_FILE = "games_temp.dat"
    # cria um arquivo temporário que vai receber os dados limpos

    novo_primario = {}
    # vai inicializar um novo dicionário vazio para mapear os novo endereços físicos de cada jogo após a mudança
    
    with open(FILE_GAMES, 'rb') as f_old, open(TEMP_FILE, 'wb') as f_new:
    # abre o arquivo antigo para leitura binária e o arquivo temporário para escrita binária

        for pk in sorted(primario.keys()):
        # vai percorrer apenas os IDs das chaves primárias que ainda estão no índice
        # o sorted vai organizar fisicamente o arquivo pela ordem da chave

            offset_antigo = primario[pk]
            # pega o endereço antigo do jogo no arquivo original

            f_old.seek(offset_antigo)
            # usa o seek para pular a cabeça do disco direto para onde o registro está no arquivo original
            
            tamanho_bytes = f_old.read(2)
            tamanho = struct.unpack('<h', tamanho_bytes)[0]
            # vão ler o indicador de tamanho do registro antigo e converter para um número inteiro usando o little-endian de 2 bytes(short)

            registro_bytes = f_old.read(tamanho)
            # vai ler o conteúdo real (os dados) do jogo
            
            # Grava no novo arquivo
            novo_offset = f_new.tell()
            # antes de escrever o jogo no novo arquivo, utiliza o tell() para saber exatamente em qual byte o arquivo novo está
            # esse será o novo byte-offset do jogo

            f_new.write(struct.pack('<h', tamanho))
            f_new.write(registro_bytes)
            # vão escrever o indicador de tamanho e os dados do jogo no arquivo temporário
            # como estão sendo escritos um após o outro sem pular bytes, a fragmentação externa é eliminada
            
            novo_primario[pk] = novo_offset
            # atualiza o novo mapa em memória
            
    # Substitui o arquivo antigo pelo novo 
    os.replace(TEMP_FILE, FILE_GAMES)
    # o replace joga fora o arquivo antigo e renomeia o arquivo temporário para o nome inicial ´´games.dat´´
    
    # Atualiza o índice primário
    salvar_indice_primario(novo_primario)
    print("Arquivo de registros compactado com sucesso.")
    # como os jogos mudaram de posição física no disco, salva o novo dicionário no disco para que continue funcionando

if __name__ == "__main__": # vai garantir que só funcione se for chamado diretamente ´´py programa.py´´
    if len(sys.argv) < 2:
    # o sys.argv funciona como uma lista contendo o que foi digitado no terminal para rodar o progama
    # vai verificar se alguma flag foi esquecida, e se a lista tiver menos de 2 itens (nome do script e a flag), vai avisar 

        print("Uso: python programa.py [-b | -e operacoes.txt | -c]")
        #se nenhuma flag tenha sido digitada vai mostrar essa mensagem com as flags que podem ser usadas

        sys.exit(1)
        # vai parar a execução já que nenhuma flag válida foi inserida

    flag = sys.argv[1]
    # vai pegar o primeiro argumento digitado após o nome do script (flag -b, -e, -c) e guarda na variável flag

    if flag == '-b':
        construir_indices()
    # se a flag -b for digitada vai chamar a função construir_indices
    # vai percorrer o arquivo games.dat para mapear os endereços e criar os arquivos de índice

    elif flag == '-e':
    # se a flag -e for usada vai para o modo de execução das operações
        if len(sys.argv) != 3: # qualquer coisa diferente de 3 argumentos irá dar erro também
            print("Erro: Arquivo de operações não fornecido. Uso: python programa.py -e operacoes.txt")
            sys.exit(1)
        # se não for fornecido o operacoe.txt junto com essa flag, o programa para de rodar e avisa o erro

        executar_operacoes(sys.argv[2])
        # cahamada da função que vai ler o arquivo de texto com os comandos (operacoes.txt)

    elif flag == '-c':
        compactar_arquivo()
    # se for digitada a flag -c, vai entrar na parte de compactação
    # vai limpar o arquivo games.dat removendo os registros deletados e eliminando a fragmentação externa

    else:
        print("Flag inválida. Use -b, -e ou -c.")
    # se for digitada qualquer outra flag, vai ser exibida essa mensagem