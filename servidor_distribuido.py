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

import socket		
from gpiozero import LED,Button
import RPi.GPIO as GPIO
import time
import json
from adaf import read_dht22
from threading import Thread

states = dict()
dist_server_data = dict()

def getjson():
    # Opening JSON file
    f = open('configuracao_sala_01.json')

    json_string = f.read()
    #print(type(json_string))
    data = json.loads(json_string)
    f.close()

    return data,json_string

def setup_server_dist():
    data,json_string = getjson()
    #print(data)
    return data

def read_temp(data):

    for temp in data['sensor_temperatura']:
        temp_gpio = temp['gpio']
        tag = temp['tag']

    temperatura,umidade,dhtDevice = read_dht22(temp_gpio,dhtDevice)
    dhtDevice.exit()
    if temperatura != -1:
        print("Leitura bem sucedida")
        dht22_dict['nome'] = temp['tag']
        dht22_dict['temperatura'] = temperatura
        dht22_dict['umidade'] = umidade

    return dht22_dict


def setup_state():
    dhtDevice = None
    data,json_string = getjson()
    outputs = dict()
    inputs = dict()
    dht22_dict = dict()
    global states

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for output in data["outputs"]:
        gpio = int(output["gpio"])
        GPIO.setup(gpio, GPIO.OUT)
        outputs[output["tag"]] = GPIO.input(gpio)

    for entrada in data["inputs"]:
        gpio = int(entrada["gpio"])
        GPIO.setup(gpio, GPIO.OUT)
        inputs[entrada["tag"]] = GPIO.input(gpio)
    
    print("Cheguei")

    states["inputs"] = inputs
    states["outputs"] = outputs

    return states

def socketando(setup_server_dist):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', setup_server_dist['porta_servidor_central']))
        s.listen(5)

        while True:    
            print("Esperando conexão . . .")
            conn, addr = s.accept()
            print("Conexão aceita . . .")
            print(f"Connected by {addr}")
            print("Esperando dados . . .")
            data = conn.recv(1024).decode()
            # tratar o json recebido e fazer o que ele manda

            if data[0] == '1':
                gpio = int(data[2:])
                print(f"Quero ligar {gpio}")
                GPIO.output(gpio,GPIO.HIGH)
                print(f"Liguei State = {GPIO.input(gpio)}")
                conn.send('1'.encode())

            elif data[0] == '0':
                gpio = int(data[2:])
                print(f"Quero apagar {gpio}")
                GPIO.output(gpio,GPIO.LOW)
                print(f"State = {GPIO.input(gpio)}")
                conn.send('1'.encode())
            
            elif data == 'EXPLAIN':
                print("Recebi EXPLAIN")
                #print(data)
                states = setup_state()
                #print(states)
                print("Enviando Respostas . . .")
                # usar json.dumps
                #gpio_s = str(states).replace("\'", "\"")
                gpio_s = json.dumps(states)
                print(type(gpio_s))
                conn.send(gpio_s.encode())
                print("Respostas enviadas . . .")

            elif data == 'TEMP':
                temp_s = read_temp(dist_server_data)
                temp_s = json.dumps(dht22_dict)
                conn.send(temp_s.encode())

            else:
                print("Mensagem não reconhecida\nEnvie novamente . . .")

            #print(f"Recebi {data}")
            #conn.send(data.encode())

def watch_smoke(gpio_pin):
    smoke_sensor = Button(int(gpio_pin),pull_up = False)
    print("to monitorando !!!!!!!!")
    smoke_sensor.wait_for_press()
    print("foi caceta !!!!!!!!")
    print('puta que pariu, pegou fogo')
    conn.send('TOCA O ALARMEEEEEEEE !!!!!!!!'.encode())
    smoke_sensor.close()
    

def watch_sensors(dist_server_info):

    print('hello from watch sensors')
    
    for entrada in dist_server_info['inputs']:
        if entrada['type'] == 'fumaca':
            gpio = entrada['gpio']
            break
    print(f"pino foi :{gpio}")
    watch_smoke(gpio)

if __name__ == '__main__':
    dist_server_data = setup_server_dist()
    
    watching_thread = Thread(target = watch_sensors,args = (dist_server_data,))
    listening_thread = Thread(target = socketando,args = (dist_server_data,))
    
    listening_thread.start()
    watching_thread.start()
    
    print('alguma thread veio')
    listening_thread.join()
    watching_thread.join()
