import socket
import os
from socket import socket as funcSocket

# configurações da conexão
buffer_size  = 1024

HOST = 'localhost'
PORT = 5000
dest = (HOST, PORT)

# criando socket udp
udp = funcSocket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(('localhost',3000))

# função que pega o input do user e define o arquivo desejado
def define_file():
    print("----------------------------------------------------------")
    print("Escreva o nome do arquivo que quer receber:\n")
    print("Opções disponíveis:")
    print("- testePDF.pdf")
    print("- testeTXT.txt")
    print("- testeMP3.mp3")
    print("- testeIMG.jpeg\n")
    print("Ou finalize a conexão com")
    print("- Finalizar\n")
    file_type = input()
    
    return file_type

# função que termina a conexão udp
def finish_conection():
    finish = "END"
    udp.sendto(finish.encode(),dest)
    udp.close()


def main(): 
    # criação da pasta no cliente
    enderecoChegada = './clienteFile'

    if not os.path.exists(enderecoChegada):
        os.makedirs(enderecoChegada)

    # pegando caminho da pasta de arquivos
    pasta = "files"
    caminho_pasta = os.path.join(os.path.dirname(__file__), pasta)

    while True:

        arquivo = define_file()

        # fim da conexão
        if arquivo == "Finalizar":
            finish_conection()
            break
        
        enderecoEnvio = os.path.join(caminho_pasta, arquivo)

        # Verifica se o arquivo existe
        if not os.path.exists(enderecoEnvio):
            print("----------------------------------------------------------")
            print(f"Arquivo '{arquivo}' não encontrado. Tente novamente.\n")
            continue

        # enviando arquivo escolhido para o servidor
        with open(enderecoEnvio, 'rb') as f:
            extensao = enderecoEnvio.split('.')[-1] # pegando extensão
            udp.sendto(extensao.encode(), dest) # envio da string codificada
            l = f.read(buffer_size) # lendo o primeiro pacotes de 1024 bytes
            while l:
                udp.sendto(l, dest) # enviando para a porta referenciada
                l = f.read(buffer_size) # ler os prox 1024 bytes do arq
            udp.sendto(b'', dest) # arquivo vazio para indicar fim

            print("Arquivo " + enderecoEnvio + " enviado com sucesso.")

        # recebendo o arquivo que o servidor enviou
        extention, servidor = udp.recvfrom(buffer_size)
        extention = extention.decode('utf-8')

        with open(f"{enderecoChegada}/arquivoNovo.{extention}", 'wb') as file: 
            while True:
                msg, servidor = udp.recvfrom(buffer_size)
                if not msg:
                    break
                file.write(msg)
                file.flush()

            print("Arquivo " + enderecoChegada + "enviado com sucesso.\n")

        
if __name__ == "__main__":
    main()  
