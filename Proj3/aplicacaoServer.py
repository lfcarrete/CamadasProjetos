#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)

def criaPacote(payload, i):
    pacote = bytes([])

    header = [bytes([0])]*10
    
    header[0] = bytes([len(payload)])
    header[1] = bytes([i])

    eop = [bytes([255])]*4

    listPayload = []

    for i in payload:
        listPayload.append(bytes([i]))
    
    for i in header + listPayload + eop:
        pacote += i

    return pacote



def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()
        

        print("Conexão Estabelecida")
        print("-"*20)
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        print("###Buscando Header###")
        header, nRx = com.getData(10, False)
        pacote, lenPacote = com.getData(header[0], False)
        eop, lenEop= com.getData(4, False)


        handshake = criaPacote(str.encode("vivo"), 0)
        print(handshake)
        print("Pacote handshake {}".format(handshake))
        com.sendData(handshake)
        print("-"*30)

        pacoteFinal = bytes([])
        
        cont = 0
        while eop != str.encode("LAST"):
            
            header, nH = com.getData(10, False)
            pacote, nP = com.getData(header[1], False)
            eop, nE = com.getData(4, False)
            print("lenPacote {}".format(nP))
            print("ID do pacote {}".format(cont))
            
            if header[1] == cont and header[0] == nP:
                resposta = criaPacote(bytes([50]), 0)
                com.sendData(resposta)
            else:
                if header[1] != cont:
                    print("Pacote fora de ordem")
                if header[0] != nP:
                    print("Tamanho real do pacote diferente do informado")

            print("* "*20)
            cont += 1
            pacoteFinal += pacote

        print(len(pacoteFinal))

            


        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except:
        print("ops! :-\\")
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
