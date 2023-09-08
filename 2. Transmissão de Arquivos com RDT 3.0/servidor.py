import socket
import os
import random
from socket import socket as funcSocket

# criando buffer, porta e host
BUFFER_SIZE  = 1024
HOST = 'localhost'
PORT = 5000
orig = (HOST, PORT)

# rdt
next_seq = 0 # enviado
snd_base = 0 # recebido
rcv_base = 0 # recebido

# criando servidor udp
servidor_udp = funcSocket(socket.AF_INET, socket.SOCK_DGRAM)
servidor_udp.bind(orig)

endereco = './servidorFile'

# criando diretório
if not os.path.exists(endereco):
    os.makedirs(endereco)

def incrementa(val):
    return 1 - val

def error_gen():
    numero_aleatorio = random.random()
    probabilidade_de_erro = 0.5
    if numero_aleatorio < probabilidade_de_erro:
        print('Erro na transmissão!')
        return 1
    else: 
        return 0

def snd_pkt(msg):
    global next_seq, rcv_base, cliente
    servidor_udp.sendto((str(next_seq).zfill(2) + str(rcv_base).zfill(2) + str(msg)).encode(), cliente)
    # print(len(msg))
    next_seq_antigo = next_seq
    next_seq = incrementa(next_seq) 

    for i in range(3):
        flag = 0
        try:
            print('Esperando ACK!')
            rcv_msg, _ = servidor_udp.recvfrom(BUFFER_SIZE)    
            flag = 1
        except socket.timeout:
            if i == 2: 
                print('Não foi possivel enviar pacote!')
                break 
            print('Reenvia pacote!')
            if error_gen() == 0:
                print('pacote enviado!')
                servidor_udp.sendto((str(next_seq_antigo).zfill(2) + str(rcv_base).zfill(2) + str(msg)).encode(), cliente)
        if flag == 1:
            break
    rcv_msg = rcv_msg.decode()

    # print('(ACK recebido)', int(rcv_msg[:2]), '==', rcv_base, 'rcv_base (server)')
    if int(rcv_msg[:2]) == rcv_base: # next_seq (server) - seq = rcv_base (cliente) 
        rcv_base = incrementa(rcv_base) 
        if int(rcv_msg[2:4]) == snd_base: # rcv_base (server) - ack = snd_base (cliente)
            print('ACK correto recebido!')

    # snd_base (ack recebido), next_seq (soma de tamanho enviado), rcv_base (soma de tamanho recebido)

def rcv_pkt():
    global rcv_base, snd_base, next_seq, cliente
    msg, cliente = servidor_udp.recvfrom(BUFFER_SIZE)
    msg = msg.decode()
    if int(msg[:2]) == rcv_base: 
        rcv_base = incrementa(rcv_base)
        # if snd_base == int(msg[2:4]):
            # print('ack recebido!')
    servidor_udp.sendto((str(next_seq).zfill(2) + str(rcv_base).zfill(2)).encode(), cliente)
    
    # print(next_seq, rcv_base, '<- next_seq, rcv_base (server)')
    next_seq = incrementa(next_seq)
    return str(msg[4:]) 

def main():
    global rcv_base, next_seq
    # criando diretório
    if not os.path.exists(endereco):
        os.makedirs(endereco)

    # sync
    syn, cliente = servidor_udp.recvfrom(BUFFER_SIZE)
    # print(syn[:3])
    if syn[:3] == 'syn':
        rcv_base = incrementa(rcv_base)
    synack_next_seq_rcv_base = ('synack' + str(next_seq).zfill(2) + str(rcv_base).zfill(2)).encode()
    servidor_udp.sendto(synack_next_seq_rcv_base, cliente)
    next_seq = incrementa(next_seq)
    print('Sincronizado! (synack enviado)')

    extentionFile = rcv_pkt()

    # enquanto o cliente não pediu fim da conexão
    while extentionFile != "fyn" :
        # recebendo arquivo enviado pelo cliente
        print(extentionFile, '<- extentionFile')
        with open(f"{endereco}/arquivoNovo.{extentionFile}", 'wb') as f:
            while True:
                msg = rcv_pkt()
                if not msg:
                    break
                f.write(msg.encode())
                f.flush() 
            f.close()
        print(f"Arquivo {endereco}/arquivoNovo.{extentionFile} recebido!")

        # reenviando o arquivo para o cliente
        with open(f"{endereco}/arquivoNovo.{extentionFile}", 'r') as f:
            snd_pkt(extentionFile)

            l = f.read(BUFFER_SIZE - 25)
            while l:
                snd_pkt(l) 
                l = f.read(BUFFER_SIZE - 25)
            # print('send packet vazio')
            snd_pkt('') # 
            print(f"Arquivo: {endereco}/arquivoNovo.{extentionFile} enviado de volta!")
        f.close()

        extentionFile = rcv_pkt()  
        print('Próxima mensagem: ', extentionFile)
    snd_pkt('fynack')
    print("Fim da conexão. (fynack)")

    servidor_udp.close()

if __name__ == "__main__":
    main()  