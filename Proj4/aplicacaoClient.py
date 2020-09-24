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
vivo = False

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
    
def estaVivo(com):
    txBuffer = criaPacote(bytes([255]),2)

    com.sendData(txBuffer)
    
    
    header, nH = com.getData(10, True)
    
    if len(header) != 0:
        rxBuffer, nRx = com.getData(header[0], True)
        eop, nE = com.getData(4, True)
        return True
    else: 
        return False

def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  return int(hours), int(mins), int(sec)

def parsePacote(payload):
    maxlen = 114
    new_payload = payload
    pac = bytes([])
    total = []
    
    while(len(new_payload)>=114):
        for i in new_payload:
            pac += bytes([i])
            if len(pac) == maxlen:
                new_payload = new_payload[114:]
                total.append(pac)
                pac = bytes([])
                break
    if len(new_payload) < 114:
        for i in new_payload:
            pac += bytes([i])
        total.append(pac)
    
    return total


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()
        com.rx.clearBuffer()

    
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        

        #Mensagem teste (está vivo?)

        vivo = estaVivo(com)
        if vivo == False:
            retry = input("Servidor inativo. Tentar novamente? S/N: ")
            print(retry)
            if retry == "S" or retry =="s":
                vivo = estaVivo(com)
                if vivo == False:
                    print("-------------------------")
                    print("Comunicação encerrada")
                    print("-------------------------")
                    com.disable()
                
        else:
            print("####Handshake Estabelecido####")

        if vivo:
            msg = bytes([255]*2578)

            #imageR = ("./imgs/computer.png")

            #msg = open(imageR, "rb").read()
            
            print("Tamanho de envio: {}".format(len(msg)))

            parsed = parsePacote(msg)
            pacotePronto = []

            numPacote = 0
        
            for i in parsed:
            
                pacotePronto.append(criaPacote(i, numPacote))
                numPacote += 1

            lenEnvio = len(pacotePronto)

            pacotePronto[lenEnvio-1] = pacotePronto[lenEnvio-1][:-4]
            pacotePronto[lenEnvio-1] += str.encode("LAST")

            for i in pacotePronto:
                print("Pacote ID:{} Enviado".format(i[1]))

                com.sendData(i)
                header, nR = com.getData(10, False)
                pacote, nP = com.getData(header[0], False)
                eop, nE = com.getData(4, False)
            
        
        
    
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
