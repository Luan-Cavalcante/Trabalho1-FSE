# Trabalho1-FSE

## Automação Predial

O objetivo do Trabalho 1 era fazer um sistema de automação predial simulado em 4 placas RaspberryPi, cada uma simulando uma sala do prédio.

A imagem da arquitetura do projeto é representada abaixo e a comunicação entre os servidores foi o protocolo TCP/IP.
![Screenshot from 2022-12-21 11-29-53](https://user-images.githubusercontent.com/67024690/208928889-11bf91c1-705e-4ef4-8840-000195dce2be.png)

## Meu Trabalho. 

### Link para apresentação 

https://youtu.be/AthoX-WZbuo

### Interface

A minha interface seguiu um modelo simples, que monitora em tempo real uma sala por vez, com a opção de troca de sala, onde o central procura por salas disponíveis e se todas estiverem disponíveis ele segue a ordem da numeração da sala.
![Screenshot from 2022-12-21 11-43-25](https://user-images.githubusercontent.com/67024690/208931711-7a6d567c-7ebf-4250-9a2f-833e1de4c184.png)


Acima, temos a interface, onde se você clica nas primeiras oções há a mudança de estado das outputs, ou seja, se está ligada e você clica a output desliga e vice-versa.

Temos também a opção de Ligar tudo e desligar todas as outputs.

Existe a opção de ligar e desligar o sistema de segurança que é representado por uma variável global.

E a opção de troca de sala.

### Funcionamento 

Para executar o programa, você precisa estar via ssh conectado em alguma Rasp e pode subir o central e o distribuído na mesma máquina.

Primeiramente, clone o repositório :
  
  git clone https://github.com/Luan-Cavalcante/Trabalho1-FSE.git

Para as dependências :

  pip install -r requirements.txt

Para o **servidor distribuído**:

  cd Trabalho1-FSE/servidor_distribuido
  python3 servidor_distribuido.py
  
Depois, para o **servidor central** :

  cd Trabalho1-FSE/servidor_central
  python3 servidor_central.py
  
Se quiser que funcione o central para mais rasps, é só ir subindo o servidor distribuído nas outras salas que o central será capaz de identificá-los e trocar para eles.
 
### Conclusão

A conclusão é de que o trabalho foi muito interessante e proveitoso, com dificuldades, mas deu tudo certo no final e com certeza a gente fica inspirado pra seguir criando projetos nessa área. Ansioso para os próximos.
