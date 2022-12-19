
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
            if data == 'F-INCENDIO':
                print("Incendio acabou no prédio.")
                confirmation = send_data_through_socket('0'+"-"+'Sirene do Alarme','action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(data,-1,confirmation)
                
def ask_temp_thought_socket(porta,ip):
    while True:
        print("to pedindo por temperatura")
        data_temp = send_data_through_socket("TEMP",'temp',porta,ip)
        print('recebi essa parada')
        #pretty_print(data)
        print(f"Temperatura : {data_temp['temperatura']}°C\nUmidade : {data_temp['umidade']}")
        sleep(2)

def match_sala():
    print("Qual sala ?\n1-Sala 1\n")
    sala = input()
    f = open("salas.json","r")
    dados_sala = json.load(f)
    f.close()
    
    if sala == '1':
        global sala_data
        
        sala_data = dados_sala['sala1']
        print(sala_data)
        data = send_data_through_socket("EXPLAIN",'config',sala_data["porta_servidor_central"],'127.0.0.1')
        #thread_temp = Thread(target = ask_temp_thought_socket,args =(sala_data["porta_servidor_distribuido"],sala_data['ip_servidor_distribuido']))
        #thread_temp.start()

        return data

