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
from socket_central import send_data_through_socket,receive_data_through_socket
import curses
from cursesmenu import CursesMenu
from curses import panel
import curses.textpad

sala_data =  dict()
salas = []
data = dict()
sala_atual = 0
def match_sala():
    global sala_atual
    global sala_data
    f = open("salas.json","r")
    dados_sala = json.load(f)
    f.close()
    while True:
        try:
            sala_atual+=1
            if sala_atual > 4:
                sala_atual = 1
            
            #print(sala_atual)
            #print('sala'+str(sala_atual))

            #print("Qual sala ?\n1-Sala 1\nSala 2\nSala 3\nSala 4")
            sala_temp = dados_sala['sala'+str(sala_atual)]
            #print(sala_data)
            data = send_data_through_socket("EXPLAIN",'config',sala_temp["porta_servidor_distribuido"],sala_temp["ip_servidor_distribuido"])
            #print("DATA : ")
            #print(data)
            sala_data = sala_temp
            return data

        except Exception as e:
            #print('deu merda')
            #print(e)
            pass
                        
        #thread_temp = Thread(target = ask_temp_thought_socket,args =(sala_data["porta_servidor_distribuido"],sala_data['ip_servidor_distribuido']))
        #thread_temp.start()
        time.sleep(0.05)

def getjson():
    # Opening JSON file
    f = open('salas.json')

    json_string = f.read()
    ##print(type(json_string))
    data = json.loads(json_string)
    #print(data)
    f.close()

    return data

class Menu(object):
    def __init__(self, items, stdscreen,y):
        self.window = stdscreen
        self.y = y
        self.position = 0
        self.items = items

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display(self):
        curses.curs_set(0)
        global outro_menu
        global current_menu

        for index, item in enumerate(self.items):
            if index == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            msg =  f"{item}"
            self.window.addstr( index, 1 + self.y, msg, mode)

        key = self.window.getch()

        if key in [curses.KEY_ENTER, ord("\n")]:
            if self.position == 0:
                pass
            elif self.position == 1:
                state = not data['outputs']['Lâmpada 01']
                state = str(int(state))
                send_data_through_socket(state+'-Lâmpada 01','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            
            elif self.position == 2:
                state = not data['outputs']['Lâmpada 02']
                state = str(int(state))
                send_data_through_socket(state+'-Lâmpada 02','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            
            elif self.position == 3:
                state = not data['outputs']['Projetor Multimidia']
                state = str(int(state))
                send_data_through_socket(state+'-Projetor Multimidia','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            
            elif self.position == 4:
                state = not data['outputs']['Ar-Condicionado (1º Andar)']
                state = str(int(state))
                send_data_through_socket(state+'-Ar-Condicionado (1º Andar)','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            
            elif self.position == 5:
                state = not data['outputs']['Sirene do Alarme']
                state = str(int(state))
                send_data_through_socket(state+'-Sirene do Alarme','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            elif self.position == 6:
                send_data_through_socket('1-ALL','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            elif self.position == 7:
                send_data_through_socket('0-ALL','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            elif self.position == 8:
                if data['ALARME'] == 0:
                    send_data_through_socket('ALARMON','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
                else:
                    send_data_through_socket('ALARMOFF','action',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
            elif self.position == 9:
                match_sala()
        elif key == curses.KEY_UP:
            self.navigate(-1)

        elif key == curses.KEY_DOWN:
            self.navigate(1)
        
def interface_window(s):
    s.keypad(True)
    s.nodelay(True)
    position = 20
    opcoes = [
            "O que vc deseja fazer ?",
            "Ligar/Desligar output",
            "Ligar/Desligar output",
            "Ligar/Desligar output",
            "Ligar/Desligar output",
            "Ligar/Desligar output",
            "Ligar Tudo",
            "Desligar tudo",
            "Ligar/Desligar alarme",
            "Trocar de sala",
            "Sair"
            ]

    main_menu = Menu(opcoes, s,50)

    while True:
        s.erase()
        s.addstr(0,0,"OUTPUTS")
        for i,(output,state) in enumerate(data['outputs'].items(),1):
            if state == 1:
                s.addstr(i,0,f"{output}".ljust(40, '.')+'ON')
            elif state == 0:
                s.addstr(i,0,f"{output}".ljust(40, '.')+'OFF')
                
        s.addstr(i+1,0,"INPUTS")
        for i,(entrada,state) in enumerate(data['inputs'].items(),i+2):
            if state == 1:
                s.addstr(i,0,f"{entrada}".ljust(40, '.')+'ON')
            elif state == 0:
                s.addstr(i,0,f"{entrada}".ljust(40, '.')+'OFF')
                
        s.addstr(i+2,0,f"Quantidade de pessoas na sala :{data['qntd_pessoas']}")
        s.addstr(i+3,0,f"ALARME = {data['ALARME']}")
        
        curses.curs_set(0)
        
        main_menu.display()

        s.refresh()

        curses.napms(100)

def ask_ask():
    global data
    while True:
        data = send_data_through_socket('EXPLAIN','config',sala_data["porta_servidor_distribuido"],sala_data["ip_servidor_distribuido"])
        #count_people = 0
        #for sala in salas.values():
        #    count_people += send_data_through_socket('PEOPLE','config',sala["porta_servidor_central"],sala_data["ip_servidor_distribuido"])
        
        #print(count_people)
        time.sleep(0.5)

if __name__ == "__main__":
    salas = getjson()
    data = match_sala()
    
    thread_send = Thread(target = ask_ask,daemon = True)
    #thread_interface = Thread(target = menu,args=(data,),daemon = True)
    thread_receive = Thread(target = receive_data_through_socket,args = (sala_data,),daemon = True)

    #thread_interface.start()
    thread_receive.start()
    thread_send.start()
    
    curses.wrapper(interface_window)

    #thread_interface.join()
    thread_receive.join()
    thread_send.join()
