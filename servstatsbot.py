from tokens import *
import matplotlib
matplotlib.use("Agg") # has to be before any other matplotlibs imports to set a "headless" backend
import matplotlib.pyplot as plt
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from netaddr import IPAddress
from fastcli import fastcli
import operator
import collections
import time
import telepot
import nmap
import requests
# import sys
# import os

info_pasta ='''
📄 Comandos:
/info — proporciona estadísticas sumadas sobre la memoria, disk, procesos;
/disk — informacion sobre todas las unidades conectadas;
/ip — muestra su dirección IP externa;
/lan — escanea todos los dispositivos conectados a la red local;
/temperatura — muestra información de la temperatura de la CPU;
/shell — entra en el modo de ejecutar comandos de shell y le envía la salida;
/speedtest — herramienta de análisis de velocidad de banda ancha;
/setmem — establece el umbral de la memoria (%) para monitorear y notificar si el uso de la memoria está por encima;
/setpoll — establece el intervalo de sondeo en segundos (superior a 10);
/memgraph — traza un gráfico del uso de la memoria de un período pasado y le envía una imagen del gráfico.'''

shell_pasta ='''📝 Lista de comandos básicos disponibles:
                     
𝗱𝗳 -𝗵 —  muestra el lugar libre y ocupado en las secciones;
𝗳𝗿𝗲𝗲 — información de uso de la memoria;
𝗳𝗱𝗶𝘀𝗸 -𝗹 — informacion sobre todas las unidades conectadas;
𝘂𝗻𝗮𝗺𝗲 -𝗿 — muestra la vercion del kernel de Linux;
𝗰𝗮𝘁 <𝘥𝘪𝘳𝘦𝘤𝘤𝘪𝘰𝘯>  — ver el contenido del archivo;
𝗽𝘄𝗱 — mostrar directorio actual;
𝗵𝗱𝗽𝗮𝗿𝗺 -𝗶 /𝗱𝗲𝘃/𝘀𝗱𝗮 — mostrar las especificaciones del disco duro;
𝗽𝘀 — lista de procesos en ejecucion;
𝘀𝗲𝗿𝘃𝗶𝗰𝗲 <𝘯𝘰𝘮𝘣𝘳𝘦 𝘥𝘦𝘭 𝘱𝘳𝘰𝘤𝘦𝘴𝘰> 𝘀𝘁𝗮𝗿𝘁/𝘀𝘁𝗼𝗽/𝗿𝗲𝘀𝘁𝗮𝗿𝘁 — realizar una accion con este servicio;
𝗸𝗶𝗹𝗹𝗮𝗹𝗹 <𝘯𝘰𝘮𝘣𝘳𝘦 𝘥𝘦𝘭 𝘱𝘳𝘰𝘤𝘦𝘴𝘰> — matar el proceso por su nombre;
𝗶𝗳𝘂𝗽/𝗶𝗳𝗱𝗼𝘄𝗻 𝗲𝘁𝗵𝟬 — activar/desactivar la interfaz eth0;
𝗿𝗼𝘂𝘁𝗲 -𝗻 — mostrat la tabla de enrutamiento local;
𝗶𝗽 𝗹𝗶𝗻𝗸 𝘀𝗵𝗼𝘄 — mostrar el estado de todas las interfaces;
𝗼𝗽𝗸𝗴 𝘂𝗽𝗱𝗮𝘁𝗲/𝘂𝗽𝗴𝗿𝗮𝗱𝗲/𝗶𝗻𝘀𝘁𝗮𝗹𝗹 — trabajocon paquetes;
𝗿𝗲𝗯𝗼𝗼𝘁 — reinicie el sistema;
𝗻𝗲𝘁𝘀𝘁𝗮𝘁 -𝘁𝘂𝗽𝗻 — muestra todas las conexiones de red establecidas utilizando los protocolos TCP y UDP ;
𝗻𝗺𝗮𝗽 -𝗣𝗻 -𝗔 — escanear los hosts en la red;
                                                                  
...Más...'''

memorythreshold = 85  # If memory usage more this %
poll = 300  # seconds

shellexecution = []
servicepool = []
timelist = []
memlist = []
xaxis = []
settingmemth = []
setpolling = []
graphstart = datetime.now()

hide_keyboard = {'hide_keyboard': True}
service={'keyboard': [['start', 'restart', 'stop', 'status']]}
markup= {'keyboard': [['/info', '/disk', '/ip', '/lan'], [ '/temperatura', '/shell', '/speedtest'], ['/setmem', '/setpoll', '/memgraph']]}
stopmarkup = {'keyboard': [['Salir']]}

def clearall(chat_id):
    if chat_id in shellexecution:
        shellexecution.remove(chat_id)
    if chat_id in settingmemth:
        settingmemth.remove(chat_id)
    if chat_id in setpolling:
        setpolling.remove(chat_id)

def bytes2human(n):
# Credits: http://code.activestate.com/recipes/578019
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def disks():
  #global bytes2human
  templ = "%-10s %8s %8s %8s \n"
  disks = templ % ("💾 Device", "Total", "Used", "Free")
  for part in psutil.disk_partitions(all=False):
      usage = psutil.disk_usage(part.mountpoint)
      disks = disks + templ % (part.device,
                          bytes2human(usage.total),
                          bytes2human(usage.used),
                          bytes2human(usage.free))
  return str(disks)
                                              
def plotmemgraph(memlist, xaxis, tmperiod):
    plt.xlabel(tmperiod)
    plt.ylabel('% Used')
    plt.title('⚡️ Memory Usage Graph ⚡️')
    plt.text(0.1*len(xaxis), memorythreshold+2, 'Threshold: '+str(memorythreshold)+ ' %')
    memthresholdarr = []
    for xas in xaxis:
        memthresholdarr.append(memorythreshold)
    plt.plot(xaxis, memlist, 'b-', xaxis, memthresholdarr, 'r--')
    plt.axis([0, len(xaxis)-1, 0, 100])
    plt.savefig('/tmp/graph.png')
    plt.close()
    f = open('/tmp/graph.png', 'rb')  # some file on local disk
    return f

def info():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boottime = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    timedif = "Online for: %.1f Hours" % (((now - boottime).total_seconds()) / 3600)
    memtotal = "Total memory: %.2f GB " % (memory.total / 1000000000)
    memavail = "Available memory: %.2f GB" % (memory.available / 1000000000)
    memuseperc = "Used memory: " + str(memory.percent) + " %"
    diskused = "Disk used: " + str(disk.percent) + " %"
    cpupercent = "Cpu usage: " + str(psutil.cpu_percent(1)) + " %"
    pids = psutil.pids()
    pidsreply = ''
    procs = {}
    for pid in pids:
        p = psutil.Process(pid)
        try:
            pmem = p.memory_percent()
            if pmem > 0.5:
                if p.name() in procs:
                    procs[p.name()] += pmem
                else:
                    procs[p.name()] = pmem
        except:
            print("Hm..")
    sortedprocs = sorted(procs.items(), key=operator.itemgetter(1), reverse=True)
    for proc in sortedprocs:
        pidsreply += proc[0] + " " + ("%.2f" % proc[1]) + " %\n"
    reply = timedif + "\n" + \
            memtotal + "\n" + \
            memavail + "\n" + \
            memuseperc + "\n" + \
            diskused + "\n" + \
            cpupercent + "\n\n" + "Top procesos:"+ "\n" + \
            pidsreply
    return reply

def speedtest():
    try:                             
        r = requests.get('https://fast.com')
        if r.status_code == 200:
            data = fastcli.main()
            return str(round(data, 2))
    except:
        return str("Eror 404, try to reconnect!")

def recupTemp():
    #print(psutil.sensors_temperatures())
    sensors_raw = psutil.sensors_temperatures()
    sensors_coretemp = str(sensors_raw['coretemp'])
    tmp = []
    testlabel = ''
    temperatures = dict()
    myCores = ['Core 0', 'Core 1']
    for labelneeded in myCores:
        while testlabel != labelneeded:
            index = sensors_coretemp.find(labelneeded)
            tempString = sensors_coretemp
            tmp = tempString[index:]
            tmp = tempString.split("'")
            for testlabel in tmp:
                if testlabel == labelneeded:
                    tmpp = str(tmp)
                    indext = tmpp.find('current=')
                    indext += 8
                    tmpp = tmpp[indext:]
                    temperatures[testlabel] = int(tmpp.split('.')[0])
                    break
    return temperatures['Core 0']

def scan():
    ip_range = "192.168.8.*" + "/" + str(IPAddress("255.255.255.0").netmask_bits())
    try:
        nm = nmap.PortScanner()
        scan = nm.scan(hosts=ip_range, arguments='-sP')
    except:
        return "CRASH"
    hosts = []
    for host in scan["scan"]:
        if "mac" in scan["scan"][host]["addresses"]:
            if "hostnames" in scan["scan"][host] and "name" in scan["scan"][host]["hostnames"][0] and not scan["scan"][host]["hostnames"][0]["name"] == "":
                name = scan["scan"][host]["hostnames"][0]["name"]
                if len(name) > 15:
                    name = name[:15] + "..."
                hosts.append([host, scan["scan"][host]["addresses"]["mac"], name ])
            else:
                hosts.append([host, scan["scan"][host]["addresses"]["mac"]])

    textline = "🖥️ Devices online:\n"
    temp_latest_scan = hosts[:]
    temp_latest_scan = sorted(temp_latest_scan, key=lambda x: x[0])
    for host in temp_latest_scan:
            if len(host) > 2:
                textline += host[0] + " ➖ " + host[1] + " ➖ " + host[2] + "\n"
            else:
                textline += host[0] + " ➖ " + host[1] + "\n"
    return textline

class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print("Your chat_id:" + str(chat_id)) # this will tell you your chat_id
        if chat_id in adminchatid:  # Store adminchatid variable in tokens.py
            if content_type == 'text':
                if msg['text'] == '/start' and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "🤖 Hola estoy esperando a tu orden...")
                    time.sleep(1)
                    bot.sendMessage(chat_id, info_pasta, reply_markup=markup)
                elif msg['text'] == "/ip" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen('curl ifconfig.me', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
                    output = p.stdout.read()
                    output = output[:-1]
                    bot.sendMessage(chat_id, str("🌍 Mi direccion ip externa : " + str(output, 'utf-8')), reply_markup=markup)
                elif msg['text'] == "/lan" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, str("Scanning network... 🔎"))
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, scan(), reply_markup=markup)                                   
                elif msg['text'] == "/disk" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, disks(), reply_markup=markup) 
                elif msg['text'] == "/speedtest" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, str("Wait 1 min to scan the network speed...😴"))
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, str("Your Internet speed is:"))
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, speedtest() + " (Mbps)", reply_markup=markup)     
                elif msg['text'] == "/temperatura" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "🔥 Temperatura de la CPU: " + str(recupTemp()) + "°C" , reply_markup=markup)
                elif msg['text'] == '/info' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "ℹ️ Informacion: \n" + info(), reply_markup=markup)
                elif msg['text'] == "Salir":
                    clearall(chat_id)
                    bot.sendMessage(chat_id, "🔙 La operacion se detuvo.", reply_markup=markup)
                elif msg['text'] == '/setpoll' and chat_id not in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    setpolling.append(chat_id)
                    bot.sendMessage(chat_id, "¿Enviarme un nuevo intervalo de sondeo en segundos? (superior a 10)", reply_markup=stopmarkup)
                elif chat_id in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global poll
                        poll = int(msg['text'])
                        if poll > 10:
                            bot.sendMessage(chat_id, "✅ Los cambios aplicados!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Por favor envíe un valor numérico apropiado mayor que 10:")
                elif msg['text'] == "/shell" and chat_id not in shellexecution:
                    bot.sendMessage(chat_id, shell_pasta)
                    time.sleep(1)
                    bot.sendMessage(chat_id, "✍️ Envíame un comando de 𝘀𝗵𝗲𝗹𝗹 para ejecutar:", reply_markup=stopmarkup)
                    shellexecution.append(chat_id) 
                elif chat_id in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, reply_markup=stopmarkup)
                    else:
                        bot.sendMessage(chat_id, "❌ No hay datos de salida.", reply_markup=stopmarkup)
                elif msg['text'] == "/setmem" and chat_id not in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    settingmemth.append(chat_id)
                    bot.sendMessage(chat_id, "¿Enviarme un nuevo umbral de memoria para monitorear?", reply_markup=stopmarkup)
                elif chat_id in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global memorythreshold
                        memorythreshold = int(msg['text'])          
                        if memorythreshold < 100:
                            bot.sendMessage(chat_id, "✅ Los cambios aplicados!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Por favor envíe un valor numérico adecuado por debajo de 100.")
                elif msg['text'] == '/memgraph':
                    bot.sendChatAction(chat_id, 'typing')
                    tmperiod = "Last %.2f hours" % ((datetime.now() - graphstart).total_seconds() / 3600)
                    bot.sendPhoto(chat_id, plotmemgraph(memlist, xaxis, tmperiod))
                elif msg['text'] == '/help':
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, info_pasta)                  
                else:
                    bot.sendMessage(chat_id, "⚠️ Sorry, I didn't understand that command. Type /help to get a list of available commands.", reply_markup=markup)


TOKEN = telegrambot

bot = YourBot(TOKEN)
bot.message_loop()
tr = 0
xx = 0
# Keep the program running.
while 1:
    if tr == poll:
        tr = 0
        timenow = datetime.now()
        memck = psutil.virtual_memory()
        mempercent = memck.percent
        if len(memlist) > 300:
            memq = collections.deque(memlist)
            memq.append(mempercent)
            memq.popleft()
            memlist = memq
            memlist = list(memlist)
        else:
            xaxis.append(xx)
            xx += 1
            memlist.append(mempercent)
        memfree = memck.available / 1000000
        if mempercent > memorythreshold:
            memavail = "Memoria disponible: %.2f GB" % (memck.available / 1000000000)
            graphend = datetime.now()
            tmperiod = "Último %.2f horas" % ((graphend - graphstart).total_seconds() / 3600)
            for adminid in adminchatid:
                bot.sendMessage(adminid, "⚠️ ¡CRÍTICO MEMORIA BAJA! ⚠️ \n" + memavail)
                bot.sendPhoto(adminid, plotmemgraph(memlist, xaxis, tmperiod))
    time.sleep(10)  # wait 10 seconds
    tr += 10
