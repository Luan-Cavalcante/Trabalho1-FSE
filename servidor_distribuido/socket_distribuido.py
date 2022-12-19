def send_data_through_socket(msg,porta,ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(porta)))
    s.send(msg.encode())
    
    data_S = s.recv(2048).decode()

def setup_server_dist():
    data,json_string = getjson()
    #print(data)
    return data


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
    
pessoas_na_sala = 0

def sub_person():
    global pessoas_na_sala

    pessoas_na_sala-=1

def add_person():
    global pessoas_na_sala

    pessoas_na_sala+=1

def watch_sensors(dist_server_info : dict):
    fumaca_flag = 0
    sensor_flag = 0

    GPIO.add_event_detect(mapa_dict['Sensor de Contagem de Pessoas Entrada'], GPIO.RISING, callback=add_person,bouncetime=200)   
    GPIO.add_event_detect(mapa_dict['Sensor de Contagem de Pessoas Saída'], GPIO.RISING, callback=sub_person,bouncetime=200)   
        
    while True:
        print('hello from watch sensors')
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 0 and fumaca_flag == 1:
            print("tava ligado e desligou")
            fumaca_flag = 0
            send_data_through_socket('F-INCENDIO',dist_server_data['porta_servidor_distribuido'],'127.0.0.1')

        # checa fumaça
        if GPIO.input(mapa_dict['Sensor de Fumaça']) == 1 and fumaca_flag == 0:
            print("tava desligado e ligou")
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
                global to_na_thread
                if to_na_thread == 0:
                    timer = Thread(target = timer_th,args = [3],daemon = True)
                    timer.start()
        
        time.sleep(0.5)

