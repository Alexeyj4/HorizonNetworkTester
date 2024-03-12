title="Tranceiver"

from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
import serial
import configparser
import time

com_port_opened = 0 #com port opened flag

tx_freq_min=134
tx_freq=tx_freq_min
tx_freq_step=5
tx_freq_max=174
channel_width=0
fake_rx_freq=174
squelch=1
timeslot_duration=1000

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
    stx_monitor.insert(INSERT,s+'\r'+'\n')

def write(s):
    ser.write(s.encode('ascii'))   
    stx_monitor.insert(INSERT,s)
   

window.title(title+" - "+port)

frm_monitor=Frame(window,  bd = 5, relief = RAISED)
stx_monitor=scrolledtext.ScrolledText(frm_monitor,width = 50,height = 30)
lbl_monitor=Label(frm_monitor,text="Монитор. [+DMOSETGROUP:0] - успешная запись")
lbl_monitor.pack()
stx_monitor.pack()
frm_monitor.pack(fill="both")


def loop1():
    global com_port_opened
    global tx_freq_min
    global tx_freq
    global tx_freq_step
    global tx_freq_max
    global channel_width
    global fake_rx_freq
    global squelch
    global timeslot_duration
    
    if(com_port_opened==1):
        while(ser.inWaiting()>0):            
            stx_monitor.insert(INSERT,ser.read())
    
    write("AT+DMOSETGROUP=")
    write(str(channel_width))
    write(",")
    write(str('%.4f' % tx_freq))
    write(",")
    write(str('%.4f' % fake_rx_freq))
    write(",0000,")
    write(str(squelch))
    writeln(",0000")    

    tx_freq=tx_freq+tx_freq_step
    if tx_freq>tx_freq_max:
        tx_freq=tx_freq_min
        stx_monitor.delete('1.0',END)
        
        

    window.after(timeslot_duration, loop1)
    
open_com_port()
loop1()

window.mainloop()
