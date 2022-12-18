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
from gpiozero import LED,Button
import RPi.GPIO as GPIO
import time
import json
from adaf import read_dht22
from threading import Thread

states = dict()
dist_server_data = dict()
mapa_dict = dict()

def getjson():
    # Opening JSON file
    f = open('configuracao_sala_02.json')

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

    temperatura,umidade,dhtDevice = read_dht22(temp_gpio)
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
    global mapa_dict

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for output in data["outputs"]:
        gpio = int(output["gpio"])
        GPIO.setup(gpio, GPIO.OUT)
        outputs[output["tag"]] = GPIO.input(gpio)
        mapa_dict[output["tag"]] = gpio

    for entrada in data["inputs"]:
        gpio = int(entrada["gpio"])
        GPIO.setup(gpio, GPIO.OUT)
        inputs[entrada["tag"]] = GPIO.input(gpio)
        mapa_dict[entrada["tag"]] = gpio

    for temp in data['sensor_temperatura']:
        temp_gpio = temp['gpio']
        tag = temp['tag']
    
    print(mapa_dict)

    try:
        temperatura,umidade,dhtDevice = read_dht22(temp_gpio)
        dhtDevice.exit()
        if temperatura != -1:
            print("Leitura bem sucedida")
            dht22_dict['nome'] = temp['tag']
            dht22_dict['temperatura'] = temperatura
            dht22_dict['umidade'] = umidade
            states['sensor_temp'] = dht22_dict

    except: 
        print('Não consegui fazer leitura')
        dht22_dict['nome'] = temp['tag']
        dht22_dict['temperatura'] = -1
        dht22_dict['umidade'] = -1
    #print("Cheguei")

    states["inputs"] = inputs
    states["outputs"] = outputs
    states['sensor_temp'] = dht22_dict
    return states

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
    


def receive_data_through_socket(setup_server_dist):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(setup_server_dist)
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
                if data[2:] == 'ALL':
                    sucess = action_all(1)
                    print(f"deu certo {sucess}")
                    conn.send(str(sucess).encode())

                else:
                    try:
                        disp = data[2:]
                        print(f"Quero ligar {disp}")
                        print(f"Liguei State = {GPIO.input(mapa_dict[disp])}")
                        GPIO.output(mapa_dict[disp],GPIO.HIGH)
                        conn.send('1'.encode())
                    except:
                        print('Não consegui ligar!!!')
                        conn.send('0'.encode())

            elif data[0] == '0':
                if data[2:] == 'ALL':
                    sucess = action_all(0)
                    print(f"deu certo {sucess}")
                    conn.send(str(sucess).encode())
                else:
                    try :
                        gpio = data[2:]
                        print(f"Quero desligar {gpio}")
                        print(f"desliguei State = {GPIO.input(mapa_dict[gpio])}")
                        GPIO.output(mapa_dict[gpio],GPIO.LOW)
                        conn.send('1'.encode())
                    except:
                        print('Não consegui ligar!!!')
                        conn.send('0'.encode())

            elif data == 'EXPLAIN':
                print("Recebi EXPLAIN")
                states = setup_state()
                print("Enviando Respostas . . .")
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

def send_data_through_socket(msg,porta,ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(porta)))
    s.send(msg.encode())
    
    data_S = s.recv(2048).decode()

def timer_th(tempo):
    time.sleep(tempo)

def watch_sensors(dist_server_info : dict):
    
    fumaca_flag = 0
    to_na_thread = 0
    sensor_flag = 0

    while True:
        print('hello from watch sensors')
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 0 and fumaca_flag == 1:
            fumaca_flag = 0
            send_data_through_socket('F-INCENDIO',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')

        # checa fumaça
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 1 and fumaca_flag == 0:
            print("ALARMEE !!!!!!")
            print('puta que pariu, pegou fogo')
            fumaca_flag = 1
            send_data_through_socket('INCENDIO',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
            print('sinal enviado')

        # se o alarme tiver ativo e tiver movimento em algum sensor 
        # dispara buzzer 
        if GPIO.input(mapa_dict['Sirene do Alarme']) == 1:
            # Verifica sensor janela 
            print("Modo de segurança ON")
            if GPIO.input(mapa_dict['Sensor de Janela']) == 1:
                #print("OPA, Tem ladrão na janela !!!")
                send_data_through_socket('ALARM-janela',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
            if GPIO.input(mapa_dict['Sensor de Presença']) == 1:
                #print("OPA, Tem ladrão na sala !!!")
                send_data_through_socket('ALARM-presenca',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
            if GPIO.input(mapa_dict['Sensor de Porta']) == 1:
                #print("OPA, Tem ladrão na porta !!!")
                send_data_through_socket('ALARM-porta',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
        else:
            #print("DESLIGADÃO !!!")
            if GPIO.input(mapa_dict['Sensor de Presença']) == 1:
                #print("OPA, Tem gente, liga a luz aí amigão!!")
                GPIO.output(mapa_dict['Lâmpada 01'],1)
                GPIO.output(mapa_dict['Lâmpada 02'],1)
                if to_na_thread == 0:
                    to_na_thread = 1
                    timer = Thread(target = timer_th,args = [3])
                    timer.start()
                    #print("Acabei de contar carai")
                    timer.join()
                    to_na_thread = 0
                    GPIO.output(mapa_dict['Lâmpada 01'],0)
                    GPIO.output(mapa_dict['Lâmpada 02'],0)
            else:
                to_na_thread = 0
        
        time.sleep(0.5)

if __name__ == '__main__':

    setup_state()

    dist_server_data = setup_server_dist()

    watching_thread = Thread(target = watch_sensors,args = (dist_server_data,))
    listening_thread = Thread(target = receive_data_through_socket,args = (dist_server_data,))
    
    listening_thread.start()
    watching_thread.start()
    
    print('alguma thread veio')
    listening_thread.join()
    watching_thread.join()
