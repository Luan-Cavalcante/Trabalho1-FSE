'''
Placa 	Sala 	IP / Porta 	Dashboard
rasp42 	01 	164.41.98.16 / 13508 	Link do Dashboard - Sala 01
rasp44 	02 	164.41.98.26 / 13508 	Link do Dashboard - Sala 02
rasp46 	03 	164.41.98.28 / 13508 	Link do Dashboard - Sala 03
rasp43 	04 	164.41.98.15 / 13508 	Link do Dashboard - Sala 04

ssh luancavalcante@164.41.98.16 -p 13508

conta pessoas
sair
atualizar toda hora

'''

import json
import socket
import time
from logger import log
import os
from threading import Thread
from socket_central import send_data_through_socket,receive_data_through_socket,match_sala

sala_data =  dict()
salas = []
data = dict()

def getjson():
    # Opening JSON file
    f = open('salas.json')

    json_string = f.read()
    #print(type(json_string))
    data = json.loads(json_string)
    f.close()

    return data

 
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
    print("1-Ação\n2-Trocar de sala\n3-Sair\n")

    entrada = input(">")
                
    if entrada == '1':
        mapa = dict()
        print("Painel de Controle de saídas")
        i = 1
        for output,state in data['outputs'].items():
            print(f"{i} - {output} == {state}\n")
            mapa[i] = output
            i+=1

        print(f"{i} - Para todos os dispositivos acima.")
        
        print("1-Ligar\n0-Desligar\n>")
        acao = input()
        if acao != 1 or acao != 0:
            print("opção errada")
            menu()
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

    elif entrada == '2':
        match_sala()
    elif entrada == '3':
        exit(0);
    else:
        print("Lê caralho !!")

def ask_ask():
    data = send_data_through_socket('EXPLAIN','config',sala_data["porta_servidor_central"],'127.0.0.1')
    pretty_print(data)
    
    count_people = 0
    for sala in salas.values():
        count_people += send_data_through_socket('PEOPLE','config',sala["porta_servidor_central"],'127.0.0.1')
    
    
    sleep(0.5)

if __name__ == "__main__":
    
    salas = getjson()
    data = match_sala()
    
    thread_send = Thread(target = ask_ask,daemon = True)
    thread_interface = Thread(target = menu,args=(data,),daemon = True)
    thread_receive = Thread(target = receive_data_through_socket,args = (sala_data,),daemon = True)

    thread_interface.start()
    thread_receive.start()
    thread_send.start()

    thread_interface.join()
    thread_receive.join()
    thread_send.join()
