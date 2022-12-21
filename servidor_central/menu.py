
def menu(data):

    while(True):
        print(f"######## Sala do Vegapunk ##########")
        print("O que vc deseja fazer ?")
        print("1-Ação\n2-Trocar de sala\n3-Sair")

        entrada = input(">")
                    
        if entrada == '1':
            mapa = dict()
            print("Painel de Controle de saídas")
            i = 1
            for output,state in data['outputs'].items():
                print(f"{i} - {output} == {state}\n")
                mapa[i] = output
                i+=1
            
            print(f"{i} - Para todos os dispositivos acima.\n")
            
            print("7 - Ligar modo de segurança")
            
            print("1-Ligar\n0-Desligar\n>")
            acao = input()
            if acao != '1' and acao != '0':
                print("opção errada")
                continue
            print("Dispositivo :")
            disp = int(input())

            if disp == 6:
                #print('DALL')
                disp = 'ALL' 
                gpio = disp
            elif disp == 7:
                if acao == '1':
                    acao = 'ALARMON'
                else:
                    acao = 'ALARMOFF'

                confirmation = send_data_through_socket(acao,'action',sala_data["porta_servidor_central"],'127.0.0.1')
                log(acao,'ALARME',confirmation)
                continue
            else:
                gpio = mapa[disp]
                #print(f" a lampada 1 tem gpio {gpio}")
            
            # enviar acao para gpio
            # chama socket, e envia essa porra
            confirmation = send_data_through_socket(acao+"-"+gpio,'action',sala_data["porta_servidor_central"],'127.0.0.1')
            log(acao,gpio,confirmation)

        elif entrada == '2':
            match_sala()
        elif entrada == '3':
            exit(0)
        else:
        print("Lê caralho !!")
            

if __name__ == "__main__":
    menu()