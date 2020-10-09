from socket import AF_INET, socket, SOCK_STREAM,SOCK_DGRAM
from threading import Thread
import tkinter
import tkinter.ttk
import json
import time
import random
import sys


def recibirTCP():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            listaEntrada = json.loads(msg)
            if type(listaEntrada) is dict:
                conectados = listaEntrada.copy()
                menuConectados['values'] = list(conectados.keys())
            else:
                if 'Selecciona a quien enviar y que método. Bienvenido' == listaEntrada:
                    entry_field.pack()
                    send_button.pack()
                    menuConectados.pack()
                    entry_field.pack()
                    tcpRadioBoton.pack()
                    udpRadioBoton.pack()
                    loginBoton.pack_forget()
                    registerBoton.pack_forget()
                    user.pack_forget()
                    password.pack_forget()
                    listaEntrada = 'Selecciona a quien enviar y que método. Bienvenido ' + miUsuario.get()+"."
                    msg_list.insert(tkinter.END, listaEntrada)
                if 'Inicia sesion o registrate para chatear' == listaEntrada:
                    msg_list.insert(tkinter.END, listaEntrada)
                if 'ERROR: Ya existe usuario, intente de nuevo' == listaEntrada:
                    msg_list.insert(tkinter.END, listaEntrada)
                if 'ERROR: No existe usuario o contraseña incorrecta, intente de nuevo' == listaEntrada:
                    msg_list.insert(tkinter.END, listaEntrada)
                if listaEntrada == 'Un nuevo usuario se ha conectado, checar abajo':
                    msg_list.insert(tkinter.END, listaEntrada)
                if listaEntrada == 'Un usuario ha dejado el chat, checar abajo':
                    msg_list.insert(tkinter.END, listaEntrada)
                if listaEntrada[0] == 'Enviar a':
                    cadena = listaEntrada[2] +" : "+listaEntrada[3]
                    msg_list.insert(tkinter.END, cadena)
        except OSError: 
            break

def recibirUDP():
    while True:
        data, addr = UDPSERVER.recvfrom(BUFSIZ)
        listaEntrada = json.loads(data)
        cadena = listaEntrada[2] +" : "+listaEntrada[3]
        msg_list.insert(tkinter.END, cadena)


def send(event=None):
    msg = my_msg.get()
    msg_list.insert(tkinter.END, miUsuario.get()+"(YO) : "+msg)
    listaSalida = ['Enviar a',menuConectados.get(),miUsuario.get(),msg]
    my_msg.set("")
    if switcher.get() == 1:
        client_socket.send(bytes(json.dumps(listaSalida), "utf8"))
    else:
        UDPSERVER.sendto( bytes( json.dumps (listaSalida) ,"utf-8"), (HOST, UDPPORTSERVER))
        
def login():
    miNombre=miUsuario.get()
    listaSalida = ['Login',miUsuario.get(), miContrasena.get(),UDPPORTCLIENTE]
    client_socket.send(bytes(json.dumps(listaSalida), "utf8"))
    
def register():
    miNombre=miUsuario.get()
    listaSalida = ['Register',miUsuario.get(), miContrasena.get(),UDPPORTCLIENTE]
    client_socket.send(bytes(json.dumps(listaSalida), "utf8"))
    
def salir(event=None):
    listaSalida = ['*Salir*',miUsuario.get()]
    client_socket.send(bytes(json.dumps(listaSalida), "utf8"))
    top.destroy()
    

top = tkinter.Tk()
top.title("YisusChat")
top.iconbitmap('chat.ico')

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  
my_msg.set("Escribe tu mensaje aquí")
miUsuario = tkinter.StringVar() 
miUsuario.set("Usuario")
miContrasena = tkinter.StringVar()  
miContrasena.set("Contraseña")

scrollbar = tkinter.Scrollbar(messages_frame)

msg_list = tkinter.Listbox(messages_frame, height=30, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

user = tkinter.Entry(top, textvariable=miUsuario)
user.bind("<Return>", login, register)
user.pack()

password = tkinter.Entry(top, textvariable=miContrasena)
password.bind("<Return>", login, register)
password.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)

send_button = tkinter.Button(top, text="Enviar", command=send)

menuConectados = tkinter.ttk.Combobox(top)

salir_button = tkinter.Button(top, text="Salir", command=send)

loginBoton = tkinter.Button(top, text="Login", command=login)
loginBoton.pack()

registerBoton = tkinter.Button(top, text="Register", command=register)
registerBoton.pack()

switcher = tkinter.IntVar(value=1)

tcpRadioBoton = tkinter.Radiobutton(top, text="TCP", state="normal", value="1", variable=switcher)
udpRadioBoton = tkinter.Radiobutton(top, text="UDP", state="normal",value="2", variable=switcher)


top.protocol("WM_DELETE_WINDOW", salir)

HOST = '192.168.1.70'
MIIP = '192.168.1.70'
TCPPORT = 22222
UDPPORTSERVER = 33333

UDPPORTCLIENTE = random.randint(10000,60000)

BUFSIZ = 1024

ADDR = (HOST, TCPPORT)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

ADDR = (MIIP, UDPPORTCLIENTE)
UDPSERVER = socket(AF_INET, SOCK_DGRAM)
UDPSERVER.bind(ADDR)

conectados = {}

recibirTCPHilo = Thread(target=recibirTCP)
recibirUDPHilo = Thread(target=recibirUDP)

recibirTCPHilo.start()
recibirUDPHilo.start()

tkinter.mainloop()  
