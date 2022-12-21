<<<<<<< HEAD:servidor_distribuido.py
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

'''

import socket		
from gpiozero import LED,Button
=======
import json
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py
import RPi.GPIO as GPIO
import socket		
from threading import Thread
import time
from adaf import read_dht22

states = dict()
dist_server_data = dict()
mapa_dict = dict()
ALARME = 0
pessoas_na_sala = 0

def send_data_through_socket(msg,porta,ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(porta)))
    s.send(msg.encode())
    
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

def receive_data_through_socket(setup_server_dist):
    global ALARME
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(setup_server_dist)
        s.bind(('0.0.0.0', setup_server_dist['porta_servidor_distribuido']))
        s.listen(socket.INADDR_ANY)

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

            elif data == 'ALARMON':
                try:
                    ALARME = 1
                    print("RECEBI LIGAR O ALARME")
                    conn.send('1'.encode())
                except:
                    conn.send('0'.encode())
            
            elif data == 'ALARMOFF':
                try:
                    ALARME = 0
                    print("RECEBI LIGAR O ALARME")
                    conn.send('1'.encode())
                except:
                    conn.send('0'.encode())

            elif data == 'PEOPLE':
                try:
                    conn.send(str(pessoas_na_sala).encode())
                except:
                    print("não consegui devolver")
                    conn.send('0'.encode())
            else:
                print("Mensagem não reconhecida\nEnvie novamente . . .")

to_na_thread = 0

def timer_th(tempo):
    global to_na_thread
    to_na_thread = 1
    GPIO.output(mapa_dict['Lâmpada 01'],1)
    GPIO.output(mapa_dict['Lâmpada 02'],1)

    time.sleep(tempo)

    GPIO.output(mapa_dict['Lâmpada 01'],0)
    GPIO.output(mapa_dict['Lâmpada 02'],0)

    to_na_thread = 0

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
        GPIO.setup(gpio, GPIO.IN)
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

    except Exception as e: 
        print('Não consegui fazer leitura')
        print(e)
        time.sleep(1)
        dht22_dict['nome'] = temp['tag']
        dht22_dict['temperatura'] = -1
        dht22_dict['umidade'] = -1
        
    #print("Cheguei")

    states["inputs"] = inputs
    states["outputs"] = outputs
    states['sensor_temp'] = dht22_dict
    states['qntd_pessoas'] = pessoas_na_sala
    states['ALARME'] = ALARME

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
<<<<<<< HEAD:servidor_distribuido.py
    
def receive_data_through_socket(setup_server_dist):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #print(setup_server_dist)
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

            elif data[:7] == 'EXPLAIN':
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
=======
        
def sub_person(oi):
    global pessoas_na_sala
    print(f"uma pessoa a menos{pessoas_na_sala}")
    pessoas_na_sala-=1
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py

def add_person(oi):
    global pessoas_na_sala
    print(f"uma pessoa a mais{pessoas_na_sala}")
    pessoas_na_sala+=1

<<<<<<< HEAD:servidor_distribuido.py
    if data_S == '1':
        print("BEM INFORMADO")

def timer_th(tempo):
    time.sleep(tempo)
=======
def watch_sensors(dist_server_info):
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py

    global dist_server_data
    global ALARME
    dist_server_data = dist_server_info
    fumaca_flag = 0
    sensor_flag = 0
    

    GPIO.add_event_detect(mapa_dict['Sensor de Contagem de Pessoas Entrada'], GPIO.RISING, callback=add_person,bouncetime=50)   
    GPIO.add_event_detect(mapa_dict['Sensor de Contagem de Pessoas Saída'], GPIO.RISING, callback=sub_person,bouncetime=50)   
        
    while True:
        print('hello from watch sensors')
<<<<<<< HEAD:servidor_distribuido.py
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 0 and fumaca_flag == 1:
            print("tava ligado e desligou")
            fumaca_flag = 0
            send_data_through_socket('F-INCENDIO',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
=======
        print(ALARME)
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py
        # checa fumaça
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 1:
            print("tava desligado e ligou")
            print("ALARMEE !!!!!!")
            print('puta que pariu, pegou fogo')
<<<<<<< HEAD:servidor_distribuido.py
            fumaca_flag = 1
            send_data_through_socket('INCENDIO',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')
            
=======
            send_data_through_socket('INCENDIO',dist_server_data['porta_servidor_central'],dist_server_data['ip_servidor_central'])
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py
            print('sinal enviado')

        # se o alarme tiver ativo e tiver movimento em algum sensor 
        # dispara buzzer
        if ALARME == 1:
            # Verifica sensor janela 

            print("Modo de segurança ON")
<<<<<<< HEAD:servidor_distribuido.py
            for entrada in dist_server_data['inputs']:
                print(entrada)
                if GPIO.input(mapa_dict[entrada['tag']]) == 1:
                    print(f"OPA, Tem ladrão na {entrada['tag']} !!!")
                #send_data_through_socket('ALARM-'+entrada['tag'],dist_server_data['porta_servidor_distribuido'],'127.0.0.1')

=======
            if GPIO.input(mapa_dict['Sensor de Janela']) == 1:
                #print("OPA, Tem ladrão na janela !!!")
                send_data_through_socket('ALARM-janela',dist_server_data['porta_servidor_central'],dist_server_data['ip_servidor_central'])
            if GPIO.input(mapa_dict['Sensor de Presença']) == 1:
                #print("OPA, Tem ladrão na sala !!!")
                send_data_through_socket('ALARM-presenca',dist_server_data['porta_servidor_central'],dist_server_data['ip_servidor_central'])
            if GPIO.input(mapa_dict['Sensor de Porta']) == 1:
                #print("OPA, Tem ladrão na porta !!!")
                send_data_through_socket('ALARM-porta',dist_server_data['porta_servidor_central'],dist_server_data['ip_servidor_central'])
>>>>>>> arquitetura_nova:servidor_distribuido/socket_distribuido.py
        else:
            #print("DESLIGADÃO !!!")
            if GPIO.input(mapa_dict['Sensor de Presença']) == 1:
                #print("OPA, Tem gente, liga a luz aí amigão!!")
                global to_na_thread
                if to_na_thread == 0:
                    timer = Thread(target = timer_th,args = [3],daemon = True)
                    timer.start()
        
        time.sleep(0.09)
