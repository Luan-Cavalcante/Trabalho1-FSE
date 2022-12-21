# first of all import the socket library
'''
Manter os valores de temperatura e umidade atualizados a cada 2 segundos (Sendo requisitado pelo servidor central periodicamente ou enviado via mensagem push);

Acionar Lâmpadas, aparelhos de Ar-Condicionado e projetores (mantendo 
informação sobre seu estado) conforme comandos do Servidor Central e retornando uma mensagem de 
confirmação para o mesmo sobre o sucesso ou não do acionamento;

Manter o estado dos sensores de presença e abertura de portas/janelas informando
ao servidor central imediatamente (mensagem push) quando detectar o acionamento de 
qualquer um deles;

Manter o estado dos sensores de fumaça informando ao servidor central imediatamente 
(mensagem push) quando detectar o acionamento de qualquer um deles;

Efetuar a contagem de pessoas entrando e saindo da sala para controle de
 ocupação;

Cada instância dos servidores distribuídos deve ser iniciada conforme o 
arquivo descrição JSON disponível neste repositório (Somente a porta local 
de cada servidor deve ser modificada no arquivo para cada aluno conforme a 
distribuição de portas disponibilizada para a turma).
'''

'''
to do list sábado 

arrumar o jeito que as saídas saem para o servidor
dar um jeito de monitorar o alarme de incendio e voltá-lo ao normal
não apagar luz enquanto o sensor tiver ligado


'''
import socket		
import RPi.GPIO as GPIO
import time
import json
from adaf import read_dht22
from threading import Thread
from socket_distribuido import setup_state,watch_sensors,getjson,send_data_through_socket,receive_data_through_socket,setup_server_dist

states = dict()
dist_server_data = dict()
mapa_dict = dict()
ALARME = 0

def read_temp(data):
    for temp in data['sensor_temperatura']:
        temp_gpio = temp['gpio']
        tag = temp['tag']

    temperatura,umidade,dhtDevice = read_dht22(temp_gpio)
    dhtDevice.exit()
    if temperatura != -1:
        print("Leitura bem sucedida")
        dht22_dict['nome'] = temp['tag']
        dht22_dict['temperatura'] = temperatura
        dht22_dict['umidade'] = umidade

    return dht22_dict

def action_all(action):
    global mapa_dict
    
    action = int(action)

    try:
        for output in dist_server_data['outputs']:
            gpio = output['tag']
            print(gpio)
            print(f"State = {GPIO.input(mapa_dict[gpio])}")
            GPIO.output(mapa_dict[gpio],action)
        return 1
    except:
        return 0

pessoas_na_sala = 0

def add_person():
    global pessoas_na_sala

    pessoas_na_sala+=1

def sub_person():
    global pessoas_na_sala

    pessoas_na_sala-=1

def main():
    setup_state()

    dist_server_data = setup_server_dist()

    watching_thread = Thread(target = watch_sensors,args = (dist_server_data,),daemon = True)
    listening_thread = Thread(target = receive_data_through_socket,args = (dist_server_data,),daemon = True)
    

    listening_thread.start()
    watching_thread.start()
    
    listening_thread.join()
    watching_thread.join()

if __name__ == '__main__':
    main()