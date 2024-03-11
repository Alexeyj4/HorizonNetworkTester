title="Receiver"

from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
import serial
import configparser
import time

com_port_opened = 0 #com port opened flag

rx_freq_min=134
rx_freq=rx_freq_min
rx_freq_step=5
rx_freq_max=174
rx_freq_prev=rx_freq_min
channel_width=0
fake_tx_freq=174
squelch=0

mode=["freq_set","get_rssi"]
current_mode=0

window = Tk()
window.title(title)

config = configparser.ConfigParser()  # создаём объекта парсера
try:
    config.read("settings.ini")  # читаем конфиг    
    port=config["settings"]["port"]  
except:
    messagebox.showerror("Ошибка","Ошибка в файле settings.ini")

def open_com_port():
    global com_port_opened    
    if(com_port_opened==0):
        try:
            global ser
            ser = serial.Serial(port,9600)
            com_port_opened=1
        except:
            messagebox.showerror("Ошибка!","Не удалось открыть COM-порт ")
            com_port_opened=0

def writeln(s):
    ser.write(s.encode('ascii'))
    ser.write('\r'.encode('ascii')) #cr
    ser.write('\n'.encode('ascii')) #lf    
    #stx_monitor.insert(INSERT,s+'\r'+'\n')

def write(s):
    ser.write(s.encode('ascii'))   
    #stx_monitor.insert(INSERT,s)
   

window.title(title+" - "+port)

frm_monitor=Frame(window,  bd = 5, relief = RAISED)
stx_monitor=scrolledtext.ScrolledText(frm_monitor,width = 50,height = 30)
lbl_monitor=Label(frm_monitor,text="Монитор. [+DMOSETGROUP:0] - успешная запись")
lbl_monitor.pack()
stx_monitor.pack()
frm_monitor.pack(fill="both")


def loop1():
    global com_port_opened
    global rx_freq_min
    global rx_freq
    global rx_freq_step
    global rx_freq_max
    global channel_width
    global fake_tx_freq
    global squelch
    global current_mode
    global rx_freq_prev

    if (mode[current_mode]=="freq_set"):

        stx_monitor.insert(INSERT,rx_freq_prev) 
        while(ser.inWaiting()>0):                
            stx_monitor.insert(INSERT,ser.read()) #этот предыдущий ответ надо вывести на экран - где запрашивали RSSI
        
        write("AT+DMOSETGROUP=")
        write(str(channel_width))
        write(",")
        write(str('%.4f' % fake_tx_freq))
        write(",")
        write(str('%.4f' % rx_freq))
        write(",0000,")
        write(str(squelch))
        writeln(",0000")    

        rx_freq_prev=rx_freq
        rx_freq=rx_freq+rx_freq_step
        if rx_freq>rx_freq_max:
            rx_freq=rx_freq_min            


    if (mode[current_mode]=="get_rssi"):
        while(ser.inWaiting()>0):
            ser.read()  #предыдущий ответ не надо выводить. Просто стираем буфер приёма

        writeln("RSSI?");


    current_mode=current_mode+1
    if(current_mode>=len(mode)):
        current_mode=0
        
        

    window.after(500, loop1) #через таймаут чередуются операции изменения частоты приёма, измерения RSSI
    
open_com_port()
loop1()

window.mainloop()
