import json
import socket
import time
from logger import log
import os
from threading import Thread

sala_data =  dict()
salas = []
data = dict()

def send_data_through_socket(msg,tipo,porta,ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
            ##print(type(data))
            ##print("Recebi os dados")
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
        s.bind(('0.0.0.0',sala_data['porta_servidor_central']))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.listen(socket.INADDR_ANY)

        while True:
            #print("Esperando conexão . . .")
            conn, addr = s.accept()
            #print("Conexão aceita . . .")
            #print(f"Connected by {addr}")
            #print("Esperando dados . . .")
            data = conn.recv(1024).decode()

            if data == 'INCENDIO':
                #print('Dispando alarme ! ! !')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(data,-1,confirmation)
                
            if data == 'ALARM-janela':
                acao = 'Alarme da janela'
                #print('Alarme da janela disparouuuu')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(acao,'Sirene do Alarme',confirmation)

            if data == 'ALARM-porta':
                acao = 'Alarme da porta'
                #print('Alarme da porta disparouuuu')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(acao,'Sirene do Alarme',confirmation)

            if data == 'ALARM-presenca':
                #print('Alarme da janela disparouuuu')
                confirmation = send_data_through_socket('1'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(acao,'Sirene do Alarme',confirmation)