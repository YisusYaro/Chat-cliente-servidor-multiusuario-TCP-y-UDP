from socket import AF_INET, socket, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import json
import time
import sys
import pickle

def aceptarConexionesTCP():
    while True:
        client, client_address = TCPSERVER.accept()
        print("Un nuevo cliente se ha conectado con",client_address)
        salida = 'Inicia sesion o registrate para chatear'
        listaSalida = salida
        client.send(bytes(json.dumps(listaSalida), "utf8"))
        addresses[client] = client_address
        Thread(target=manejarClienteTCP, args=(client,)).start()


def manejarClienteTCP(client):

    listaEntrada = json.loads(client.recv(BUFSIZ).decode("utf8"))
    name = listaEntrada[1]
    print(name)

    if listaEntrada[0] == 'Login':
        while True:
            if iniciarSesion(listaEntrada[1],listaEntrada[2]) == False:
                salida = 'ERROR: No existe usuario o contraseña incorrecta, intente de nuevo'
                listaSalida = salida
                client.send(bytes(json.dumps(listaSalida), "utf8"))
                listaEntrada = json.loads(client.recv(BUFSIZ).decode("utf8"))
            else:
                break
    if listaEntrada[0] == 'Register':
        while True:
            if registrar(listaEntrada[1]) == True:
                salida = 'ERROR: Ya existe usuario, intente de nuevo'
                listaSalida = salida
                client.send(bytes(json.dumps(listaSalida), "utf8"))
                listaEntrada = json.loads(client.recv(BUFSIZ).decode("utf8"))
            else:
                break
    name = listaEntrada[1]
    usuarios[listaEntrada[1]]=listaEntrada[2]
    puertos[listaEntrada[1]]=listaEntrada[3]
    
    guardarDatos() 
    welcome = 'Selecciona a quien enviar y que método. Bienvenido'
    listaSalida=welcome
    client.send(bytes(json.dumps(listaSalida), "utf8"))

    
    msg = 'Un nuevo usuario se ha conectado, checar abajo'
    listaSalida=msg

    clientsAddr[name] = addresses[client]
    
    broadcast(listaSalida)
    clients[client] = name


    while True:
        
        msg = client.recv(BUFSIZ)
        listaEntrada = json.loads(msg)

        if listaEntrada[0] == 'Enviar a':
            enviarTCP(listaEntrada,listaEntrada[1])

        if listaEntrada[0] == '*Salir*':
            listaSalida = 'Un usuario ha dejado el chat, checar abajo'
            del clients[client]
            del clientsAddr[name]
            broadcast(listaSalida)
            break

def enviarTCP(lista,name):
    for sock in clients:
        print(clients[sock])
        if name == clients[sock]:
            sock.send(bytes(json.dumps(lista), "utf8"))

def broadcast(listaSalida):
    for sock in clients:
        sock.send(bytes(json.dumps(listaSalida), "utf8"))
        
def conectados():
    i=0
    while True:
        time.sleep(1)
        i=i+1;
        print("Trabajando",i)
        for sock in clients:
            sock.send(bytes(json.dumps(clientsAddr), "utf8"))

def registrar(usuario):
    if usuario in usuarios:
        return True
    else:
        return False
def iniciarSesion(usuario, contraseña):
    if usuario in usuarios:
        if usuarios[usuario] == contraseña:
            return True
        else:
            return False
    else:
        return False

def manejarClientesUDP():
    while True:
        data, addr = UDPSERVER.recvfrom(BUFSIZ) 
        listaEntrada = json.loads(data)
        enviarUDP(listaEntrada, listaEntrada[1])

def enviarUDP(listaSalida, name):
    UDPSERVER.sendto( bytes( json.dumps (listaSalida) ,"utf-8"), (clientsAddr[name][0], puertos[name]))
    
    
def cargarDatos():
    with open('numbers.txt', 'r') as f:
        return json.load(f)
        
def guardarDatos():
    with open('numbers.txt', 'w') as f:
        json.dump(usuarios, f)
        

def salir():
    sys.exit()


clients = {}
addresses = {}
clientsAddr = {}
usuarios = cargarDatos()
puertos = {}

HOST = '192.168.1.70'

TCPPORT = 22222
UDPPORTSERVER = 33333

BUFSIZ = 1024

ADDR = (HOST, TCPPORT)
TCPSERVER = socket(AF_INET, SOCK_STREAM)
TCPSERVER.bind(ADDR)

ADDR = (HOST, UDPPORTSERVER)
UDPSERVER = socket(AF_INET, SOCK_DGRAM)
UDPSERVER.bind(ADDR)

if __name__ == "__main__":
    
    TCPSERVER.listen(5)
    
    print("Esperando conexiones")
    
    aceptarTCPHilo = Thread(target=aceptarConexionesTCP)
    conectadosHilo = Thread(target=conectados)
    manejarUDPHilo = Thread(target=manejarClientesUDP)
    
    aceptarTCPHilo.start()
    conectadosHilo.start()
    manejarUDPHilo.start()
    
    aceptarTCPHilo.join()
    
    TCPSERVER.close()
    UDPSERVER.close()
