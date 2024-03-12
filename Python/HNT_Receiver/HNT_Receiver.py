title="Receiver"
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
import serial
import configparser
import time
from tkinter import Canvas

com_port_opened = 0 #com port opened flag

rx_freq_min=134
rx_freq=rx_freq_min
rx_freq_step=5
rx_freq_max=174
channel_width=0
fake_tx_freq=174
squelch=0
timeslot_duration=1000
sync_timeout_divider=10 #для этапа синхронизации ставим мальнький таймаут
timeout=int(timeslot_duration/2)
rssi_sync_threshold=70 #когда нет сигнала - примерно 20, когда максимум - примерно 110 

cnvs_width=150 #размер полотна для рисования графиков
cnvs_heigth=55 #размер полотна для рисования графиков

mode_dict={'idle':0, 'sync':1, 'freq_set':2, 'get_rssi':3}
mode_dict_iterator=mode_dict['idle']

window = Tk()
window.title(title)

config = configparser.ConfigParser()  # создаём объекта парсера
try:
    config.read("settings.ini")  # читаем конфиг    
    port=config["settings"]["port"]  
except:
    messagebox.showerror("Ошибка","Ошибка в файле settings.ini")

def start():
    global mode_dict_iterator    
    global timeout
    cnvs.delete('all')
    mode_dict_iterator=mode_dict["sync"]
    timeout=int(timeslot_duration/sync_timeout_divider)
    stx_monitor.delete('1.0',END)
    stx_monitor.insert(INSERT,'Синхронизация..')   

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

def freq_set():
    ser_clear()
    write("AT+DMOSETGROUP=")
    write(str(channel_width))
    write(",")
    write(str('%.4f' % fake_tx_freq))
    write(",")
    write(str('%.4f' % rx_freq))
    write(",0000,")
    write(str(squelch))
    writeln(",0000")    

def get_rssi():
    ser_clear()
    writeln("RSSI?")
    rssi=ser.readline()[5:8]
    return int(rssi)

def ser_clear():
    while(ser.inWaiting()>0):
        ser.read()

window.title(title+' - '+port)

frm_control=Frame(window, bd = 5, relief = RAISED)
btn_start=Button(frm_control,text='Старт',command=start)
btn_start.pack()
frm_control.pack(fill='both')

frm_monitor=Frame(window,  bd = 5, relief = RAISED)
stx_monitor=scrolledtext.ScrolledText(frm_monitor,width = 50,height = 30)
lbl_monitor=Label(frm_monitor,text='Результат:')
lbl_monitor.pack()
stx_monitor.pack()
frm_monitor.pack(fill='both')

frm_chart=Frame(window,  bd = 5, relief = RAISED)
cnvs=Canvas(frm_chart,width=cnvs_width,height=cnvs_heigth)
cnvs.pack()
frm_chart.pack(fill='both')


        

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
    global timeslot_duration
    global timeout
    global mode_dict
    global mode_dict_iterator
    global sync_timeout_divider
    global rssi_sync_threshold

    if mode_dict_iterator==mode_dict['idle']:
        timeout=int(timeslot_duration/2)
        rx_freq=rx_freq_min
        freq_set()

    if mode_dict_iterator==mode_dict['sync']:                                         
        stx_monitor.insert(INSERT,'.')        
        if get_rssi()>rssi_sync_threshold:
            timeout=int(timeslot_duration/2)
            stx_monitor.insert(INSERT,'\n\r')
            mode_dict_iterator=mode_dict["get_rssi"]        
            
    elif mode_dict_iterator==mode_dict["freq_set"]:                 
        freq_set()
        mode_dict_iterator=mode_dict["get_rssi"]

    elif mode_dict_iterator==mode_dict["get_rssi"]:        
        stx_monitor.insert(INSERT,str(rx_freq)+'МГц-')
        stx_monitor.insert(INSERT,get_rssi())
        stx_monitor.insert(INSERT,'\n\r')
        cnvs.create_line(1,1,20,50)
        rx_freq=rx_freq+rx_freq_step
        mode_dict_iterator=mode_dict["freq_set"]
        if rx_freq>rx_freq_max:
            rx_freq=rx_freq_min            
            mode_dict_iterator=mode_dict["idle"]                     
     
    window.after(timeout, loop1) #через таймаут чередуются операции изменения частоты приёма, измерения RSSI
    
open_com_port()
loop1()

window.mainloop()
