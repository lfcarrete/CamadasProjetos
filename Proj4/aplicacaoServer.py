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
serialName = "COM3"                  # Windows(variacao de)

def criaPacote(payload, i, tipo_mensagem):
    pacote = bytes([])

    header = [bytes([0])]*10
    
    header[0] = bytes([tipo_mensagem]) #tipo de mensagem
    header[1] = bytes([123]) #id do sensor
    header[2] = bytes([56]) #id do servidor
    header[4] = bytes([i]) #Numero do pacote enviado
    header[5] = bytes([len(payload)]) #Len do pacote
    header[6] = bytes([i-1]) #Pacote para recomeco quando erro no envio
    header[7] = bytes([i-1]) #Ultimo pacote recebido com sucesso
    header[8] = bytes([0]) #CRC
    header[9] = bytes([0]) #CRC
    
    eop = [bytes([255])]*4
    eop[1] = bytes([170])
    eop[3] = bytes([170])

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
        
        
        header, nH = com.getData(0)
        while len(header)==0:
            header, nH = com.getData(10)
            
        
        pacote, lenPacote = com.getData(1)
        eop, lenEop= com.getData(4)
        
        print(pacote)

        handshake = criaPacote(bytes([0]),1,2)
        print("Pacote handshake {}".format(handshake))
        com.sendData(handshake)
        print("-"*30)
        print("{} pacotes a serem resgatados\n".format(header[3]))

        pacoteFinal = bytes([])

        cont = 1
        numPacotes = 1

        

        while numPacotes <= header[3]:
            resposta = criaPacote(bytes([0]), cont, 4)
            timer = 0

            nH = 0
            header, nH = com.getData(0)
            while nH == 0:
                header, nH = com.getData(10)         
            pacote, nP = com.getData(header[5])
            eop, nE = com.getData(4)

           
            print("lenPacote {}".format(nP))
            print("ID do pacote {}".format(header[4]))
                   
            if header[4] == cont and header[5] == nP:
                print("Envia Resposta")
                com.sendData(resposta)
            else:
                if header[4] != cont:
                    print("Pacote fora de ordem")
                if header[5] != nP:
                    
                   print("Tamanho real do pacote diferente do informado")
                  
            print("* "*20)
            cont += 1
            numPacotes += 1
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
