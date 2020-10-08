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
vivo = False

def criaPacote(payload, i, tipo_mensagem, Handshake, numTotalPacotes):
    pacote = bytes([])

    header = [bytes([0])]*10
    
    header[0] = bytes([tipo_mensagem]) #tipo de mensagem
    header[1] = bytes([123]) #id do sensor
    header[2] = bytes([56]) #id do servidor
    header[3] = bytes([numTotalPacotes]) #numero total de pacotes do arquivo
    header[4] = bytes([i]) #Numero do pacote enviado
    
    if Handshake:
        header[5] = bytes([111]) # id do arquivo
    else:
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
    
def estaVivo(com, numTotalPacotes, f):
    current_time = time.localtime()
    txBuffer = criaPacote(bytes([0]), 1, 1, True, numTotalPacotes) 
    com.sendData(txBuffer)
    f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 1 / {6} / 0 / {7}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(txBuffer),txBuffer[3]))


    temp = 0
    nH = 0
    while temp < 5 and nH == 0:
        header, nH = com.getData(10)
        temp += 0.5
    
        

    if nH != 0 and header[0] == 2:
        rxBuffer, nRx = com.getData(header[5])
        eop, nE = com.getData(4)
        f.write("{0}/{1}/{2} {3}:{4}:{5} / receb / 2 /{6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(header+rxBuffer+eop)))
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
        

        f= open("Client.txt","w+")
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        

        #Mensagem teste (está vivo?)
        msg = bytes([255]*3333)

        parsed = parsePacote(msg)
        pacotePronto = []

        numPacote = 1
        for i in parsed:
            pacotePronto.append(criaPacote(i, numPacote, 3, False, len(parsed))) 
            numPacote += 1

        lenEnvio = len(pacotePronto)

        vivo = estaVivo(com, len(pacotePronto), f)
        if vivo == False:
            retry = input("Servidor inativo. Tentar novamente? S/N: ")
            print(retry)
            if retry == "S" or retry =="s":
                vivo = estaVivo(com, len(pacotePronto), f)
                if vivo == False:
                    print("-------------------------")
                    print("Comunicação encerrada")
                    print("-------------------------")
                    com.disable()
                
        else:
            print("####Handshake Estabelecido####")
        
        if vivo:

            
            print("Qnt de pacotes a serem enviados {}\n".format(lenEnvio))
            print("Tamanho de envio: {}".format(len(msg)))
            cont = 0

            timer1 = 0 #SET TIMER 1
            timer2 = 0 #SET TIMER 2
            
            current_time = time.localtime()

            com.sendData(pacotePronto[cont])
            f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 3 / {6} / {7} / {8}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(pacotePronto[cont]), pacotePronto[cont][4], pacotePronto[cont][3]))
            print("Pacote ID:{} Enviado".format(pacotePronto[cont][4]))
            test = True 
            while cont < len(pacotePronto):      
                if test:
                    cont = 1
                    test = False        
                current_time = time.localtime()
                header, nR = com.getData(10)  
                
                timer1 += 1
                timer2 += 1
                

                if nR != 0:
                    pacote, nP = com.getData(header[5])           
                    eop, nE = com.getData(4)
                    f.write("{0}/{1}/{2} {3}:{4}:{5} / receb / 4 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(header + pacote + eop)))

                    if  header[0] == 4:
                        cont += 1
                        print("----------------Pacote chegou OK!-----------------")
                        com.sendData(pacotePronto[cont])

                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 3 / {6} / {7} / {8}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(pacotePronto[cont]), pacotePronto[cont][4], pacotePronto[cont][3]))


                        print("Pacote ID:{} Enviado".format(pacotePronto[cont][4]))
                        timer1 = 0
                        timer2 = 0

                    elif header[0] == 6:
                        
                        print("-----------------Pacote com erro 6---------------")
                        cont = pacotePronto[cont][6] - 1
                        com.sendData(pacotePronto[cont]) 
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 3 / {6} / {7} / {8}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(pacotePronto[cont]), pacotePronto[cont][4], pacotePronto[cont][3]))

                        timer1 = 0
                        timer2 = 0
                    
                else:
                    if timer1 > 5:
                        print(cont)
                        com.sendData(pacotePronto[cont]) 
                        print("-----------------REENVIO PACOTE {}------------------".format(cont))
                        
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 3 / {6} / {7} / {8}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(pacotePronto[cont]), pacotePronto[cont][4], pacotePronto[cont][3]))

                        timer1 = 0
                        

                    if timer2 > 20:
                        resp = criaPacote(bytes([0]), 1, 5,False, 0)
                        com.sendData(resp)
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 5 / {6} \n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resp)))
                        f.close()
                        print("-----------------Timeout--------------------")
                        break


                print("* "*20)
                print(cont)
                 
        f.close()
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
