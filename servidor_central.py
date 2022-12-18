'''
Placa 	Sala 	IP / Porta 	Dashboard
rasp42 	01 	164.41.98.16 / 13508 	Link do Dashboard - Sala 01
rasp44 	02 	164.41.98.26 / 13508 	Link do Dashboard - Sala 02
rasp46 	03 	164.41.98.28 / 13508 	Link do Dashboard - Sala 03
rasp43 	04 	164.41.98.15 / 13508 	Link do Dashboard - Sala 04

ssh luancavalcante@164.41.98.16 -p 13508
'''

import json
import socket
import time
from gpiozero import Button,LED
from logger import log
import os
from threading import Thread

sala_data =  dict()
data = dict()

def match_sala():
    print("Qual sala ?\n1-Sala 1\n")
    sala = input()
    f = open("salas.json","r")
    dados_sala = json.load(f)
    
    if sala == '1':
        global sala_data
        
        sala_data = dados_sala['sala1']
        print(sala_data)
        data = send_data_through_socket("EXPLAIN",'config',sala_data["porta_servidor_central"],'127.0.0.1')
        #thread_temp = Thread(target = ask_temp_thought_socket,args =(sala_data["porta_servidor_distribuido"],sala_data['ip_servidor_distribuido']))
        #thread_temp.start()

        return data

def ask_temp_thought_socket(porta,ip):
    while True:
        print("to pedindo por temperatura")
        data_temp = send_data_through_socket("TEMP",'temp',porta,ip)
        print('recebi essa parada')
        #pretty_print(data)
        print(f"Temperatura : {data_temp['temperatura']}°C\nUmidade : {data_temp['umidade']}")
        sleep(2)

def getjson():
    # Opening JSON file
    f = open('configuracao_sala_01.json')

    json_string = f.read()
    # returns JSON object a

    print(type(json_string))

    # a dictionary
    data = json.loads(json_string)
    # Iterating through the json
    f.close()

    return data,json_string

def pretty_print(data):
    #os.system('clear')
    print('Sensores:')
    for entrada,estado in data['inputs'].items():
        if(estado == 1):
            print(f"{entrada}".ljust(40, '.')+'ON')
        else:
            print(f"{entrada}".ljust(40, '.')+'OFF')

    print('Outputs: ')

    for saida,estado in data['outputs'].items():
        if(estado == 1):
            print(f"{saida}".ljust(40, '.')+'ON')
        else:
            print(f"{saida}".ljust(40, '.')+'OFF')

    print(f"Temperatura :{data['sensor_temp']['temperatura']} °C" )
    print(f"Umidade :{data['sensor_temp']['umidade']}")

def menu(data):
    print(f"######## Sala do Vegapunk ##########")
    
    pretty_print(data)
    print("O que vc deseja fazer ?")
    print("0-Ação\n5-Trocar de sala\n")

    entrada = input(">")
                
    if entrada == '0':
        mapa = dict()
        print("Painel de Controle de saídas")
        i = 1
        for output,state in data['outputs'].items():
            print(f"{i} - {output} == {state}\n")
            mapa[i] = output
            i+=1

        print(f"{i} - Para todos os dispositivos acima.")
        
        print("1-Ligar\n0-Desligar")
        acao = input()
        print("Dispositivo :")
        disp = int(input())

        if disp == 6:
            #print('DALL')
            disp = 'ALL' 
            gpio = disp
        else:
            gpio = mapa[disp]
            #print(f" a lampada 1 tem gpio {gpio}")
        
        # enviar acao para gpio
        # chama socket, e envia essa porra
        confirmation = send_data_through_socket(acao+"-"+gpio,'action',sala_data["porta_servidor_central"],'127.0.0.1')
        log(acao,gpio,confirmation)
        menu(data)

    elif entrada == '5':
        match_sala()
        
    else:
        print("Lê caralho !!")

def send_data_through_socket(msg,tipo,porta,ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(porta)))
    s.send(msg.encode())
    
    data_S = s.recv(2048).decode()
    if tipo == 'action':
        # tratar o data_s como 0 ou 1 de confirmação se a ação deu certo
        if data_S == '1':
            # significa que deu certo
            print("ação confirmada com sucesso")
        else:
            print("ação confirmada com error\nEnvie novamente.")

    elif tipo == 'config':
        # tratar o data_s como um json vindo com dados e states
        data = json.loads(data_S)
        print(type(data))
        print("Recebi os dados")
        s.close()
        return data

    elif tipo == 'temp':
        # tratar o data_s como um json de temperatura e umidade
        data_temp = json.loads(data_S)
        # atualizar dados de temperatura e umidade

        # 50 ms pessoas
        # 100 ms sensores
        return data_temp

    else:
        print('Protocolo sem confirmação de recebimento dos dados!!!')

def receive_data_through_socket(sala_data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1',sala_data['porta_servidor_distribuido']))
        
        s.listen(5)

        while True:
            print("Esperando conexão . . .")
            conn, addr = s.accept()
            print("Conexão aceita . . .")
            print(f"Connected by {addr}")
            print("Esperando dados . . .")
            data = conn.recv(1024).decode()

            if data == 'INCENDIO':
                print('Dispando alarme ! ! !')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(data,-1,confirmation)
            if data == 'ALARM-janela':
                print('Alarme da janela disparouuuu')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(acao,gpio,confirmation)

if __name__ == "__main__":
    
    data = match_sala()
    #print(data['inputs'])
    
    thread_interface = Thread(target = menu,args=(data,))
    thread_receive = Thread(target = receive_data_through_socket,args = (sala_data,))

    thread_interface.start()
    thread_receive.start()

    thread_interface.join()
    thread_receive.join()
