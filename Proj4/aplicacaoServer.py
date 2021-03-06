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
import crcmod



# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)
ocioso = True
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


def handshake(com, f):
    current_time = time.localtime()

    global ocioso
   
    header, nH = com.getData(10)
        
    if len(header) != 0 and header[0] == 1:
        if header[2] == 56:
            print("PRONTO PARA RECEBER")
            ocioso = False
            pacote, lenPacote = com.getData(1)
            eop, lenEop= com.getData(4)
            f.write("{0}/{1}/{2} {3}:{4}:{5} / receb / 1 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(header+pacote+eop)))
            print("-"*30)
            print("{} pacotes a serem resgatados\n".format(header[3]))
        else:
            print("NAO EH PRA MIM")
    return header
    

def main():
    global ocioso
    try:
        _CRC_FUNC = crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xffff) #CRC
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
        
        f= open("Server.txt","w+")

        
        #INICIO DO HANDSHAKE 
        while ocioso:
            header = handshake(com, f)
            time.sleep(1)
        if ocioso == False:
            pacoteHandshake = criaPacote(bytes([0]),1,2)
            print("Pacote handshake {}".format(pacoteHandshake))
            current_time = time.localtime()
            f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 2 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(pacoteHandshake)))
            com.sendData(pacoteHandshake)

            pacoteFinal = bytes([])

            cont = 1
            timer1 = 0 #SET TIMER 1
            timer2 = 0 #SET TIMER 2
            
            contTotal = header[3]
            listaPacotes = [0]*contTotal

            while cont <= contTotal and ocioso == False:

                print("ESPERANDO PACOTE {}".format(cont))
                timer1 += 0.5
                timer2 += 0.5
                header, nH = com.getData(10)
                
                
                
                
                if nH != 0 and header[0] == 3: 
                    current_time = time.localtime()

                    pacote, nP = com.getData(header[5])
                    eop, nE = com.getData(4)
                    
                    crc = bytes([header[8]]) + bytes([header[9]])
                    resp = _CRC_FUNC(pacote)
                    c = resp.to_bytes(2,'big')
                    

                    f.write("{0}/{1}/{2} {3}:{4}:{5} / receb / {6} / {7}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], header[0], len(header+pacote+eop)))

                    print(nP)
                    if cont == header[4] and nP == header[5] and crc==c:
                        print("lenPacote {}".format(nP))
                        print("ID do pacote {}".format(header[4]))
                        print("Pacote OK")
                        listaPacotes[cont-1] = pacote
                        print(cont)
                        resposta = criaPacote(bytes([0]), cont, 4)
                        print("***Envia Resposta t4***")
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 4 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resposta)))

                        com.sendData(resposta)
                        cont += 1
                        timer1 = 0
                    
                    elif cont != header[4]:
                        print("CHEGOU {}".format(header[4]))
                        resposta = criaPacote(bytes([0]), cont, 6)
                        print("Envia Resposta t6")
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 6 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resposta)))
                        com.sendData(resposta)
                        cont = header[6]
                    elif(nP == 0):
                        cont = header[6]
                        print("PACOTE CHEGOU VAZIO")
                        resposta = criaPacote(bytes([0]), cont, 6)
                        print("Envia Resposta t6")
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 6 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resposta)))

                        com.sendData(resposta)
                    

                else:
                    time.sleep(1)
                    if timer2 > 20:
                        ocioso = True
                        resposta = criaPacote(bytes([0]), 1, 5)
                        print("OCIOSO")
                        print("Envia Resposta t5")
                        f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 5 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resposta)))
                        com.sendData(resposta)
                        break

                    else:
                        if timer1 > 2:
                            resposta = criaPacote(bytes([0]), cont, 4)
                            print("Envia Resposta t4 do pacote {}".format(cont))
                            f.write("{0}/{1}/{2} {3}:{4}:{5} / envio / 4 / {6}\n".format(current_time[2],current_time[1],current_time[0],current_time[3],current_time[4],current_time[5], len(resposta)))
                            com.sendData(resposta)
                            timer1 = 0
                

                if nH != 0 and header[0] == 5:
                    print("Timeout")
                    break
            
                    
                print("* "*20)
            if cont-1 == contTotal:
                for i in listaPacotes:
                    pacoteFinal+=i
                print("SUCESSO!")
                print("Len Pacote Final --> {}".format(len(pacoteFinal)))
            else: 
                print("ALGUM ERRO OCORREU")

            

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
