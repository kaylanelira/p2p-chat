import socket
import os
from socket import socket as funcSocket

# criando buffer, porta e host
buffer_size  = 1024
HOST = 'localhost'
PORT = 5000
orig = (HOST, PORT)

# criando servidor udp
ServidorUdp = funcSocket(socket.AF_INET, socket.SOCK_DGRAM)
ServidorUdp.bind(orig)

endereco = './servidorFile'

# criando diretório
if not os.path.exists(endereco):
    os.makedirs(endereco)

extention, cliente = ServidorUdp.recvfrom(buffer_size)
extention = extention.decode('utf-8') # converte extensão p/ string

with open(f"{endereco}/arquivoNovo.{extention}", 'wb') as f: 
    while True:
        msg, cliente = ServidorUdp.recvfrom(buffer_size)
        if not msg:
            break
        print("arquivo teste:", msg.decode('utf-8'))  
        f.write(msg)
        f.flush()   # passei 3 horas tmb por conta dessa desgraça

with open(f"{endereco}/arquivoNovo.{extention.decode()}", 'rb') as f:
    l = f.read(buffer_size)
    dest = cliente  # Utilize o endereço do cliente para enviar a resposta
    while l:
        ServidorUdp.sendto(l, dest)
        l = f.read(buffer_size)

f.close()



"""f = open("servidor/arquivoNovo" + extention, 'rb')
l = f.read()

while(l):
    ServidorUdp.sendto(l, cliente)
    l = f.read()
f.close()
    
ServidorUdp.close()"""
   