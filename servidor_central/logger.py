from datetime import datetime, timezone,timedelta


def log(acao,gpio,confi):
    acao = str(acao)
    gpio = str(gpio)
    confi = str(gpio)
    diferenca = timedelta(hours=-3)
    fuso_horario = timezone(diferenca)
    data_e_hora_atuais = datetime.now()
    data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
    data_e_hora_sao_paulo_em_texto = data_e_hora_sao_paulo.strftime("%d/%m/%Y, %H:%M")
    if acao == '1':
        acao = 'Ligou'
    elif acao == '0':
        acao = 'Desligou'
    else:
        print("Tentativa errada")
        return 

    with open("log.csv","a") as f:
        f.write(data_e_hora_sao_paulo_em_texto+','+acao+','+gpio+','+confi+'\n')
        f.close()
    
