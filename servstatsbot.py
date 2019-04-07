from tokens import *
import matplotlib
matplotlib.use("Agg") # has to be before any other matplotlibs imports to set a "headless" backend
import matplotlib.pyplot as plt
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator
import collections
import time
import telepot
# import sys
# import os

memorythreshold = 85  # If memory usage more this %
poll = 300  # seconds

shellexecution = []
timelist = []
memlist = []
xaxis = []
settingmemth = []
setpolling = []
graphstart = datetime.now()

stopmarkup = {'keyboard': [['Stop']]}
hide_keyboard = {'hide_keyboard': True}

markup= {'keyboard': [['/info', '/ip', '/shell', '/temperatura'], ['/setmem', '/setpoll', '/disk', '/memgraph'], ['Stop']]}

def clearall(chat_id):
    if chat_id in shellexecution:
        shellexecution.remove(chat_id)
    if chat_id in settingmemth:
        settingmemth.remove(chat_id)
    if chat_id in setpolling:
        setpolling.remove(chat_id)

def bytes2human(n):
# Credits: http://code.activestate.com/recipes/578019
#thank you fabaff !
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def plotmemgraph(memlist, xaxis, tmperiod):
    # print(memlist)
    # print(xaxis)
    plt.xlabel(tmperiod)
    plt.ylabel('% Used')
    plt.title('⚡️ Memory Usage Graph')
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

class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Do your stuff according to `content_type` ...
        print("Your chat_id:" + str(chat_id)) # this will tell you your chat_id
        if chat_id in adminchatid:  # Store adminchatid variable in tokens.py
            if content_type == 'text':
                if msg['text'] == '/start' and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "Hola estoy esperando a tu orden...")
                    time.sleep(1)
                    bot.sendMessage(chat_id, text='''
📄 Comandos:
/info — proporciona estadísticas sumadas sobre la memoria, disk, procesos;
/shell — entra en el modo de ejecutar comandos de shell y le envía la salida;
/memgraph — traza un gráfico del uso de la memoria de un período pasado y le envía una imagen del gráfico;
/setmem — establece el umbral de la memoria (%) para monitorear y notificar si el uso de la memoria está por encima;
/setpoll — establece el intervalo de sondeo en segundos (superior a 10).''', reply_markup=markup)
                elif msg['text'] == "/ip" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen('curl ifconfig.me', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
                    output = p.stdout.read()
                    output = output[:-1]
                    bot.sendMessage(chat_id, str("🌍 Mi direccion ip externa : " + str(output, 'utf-8')), reply_markup=markup)
                elif msg['text'] == "/disk" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    def disks():
                        global bytes2human
                        templ = "%-20s %8s %8s %8s \n"
                        disks = templ % ("Device", "Total", "Used", "Free")
                        for part in psutil.disk_partitions(all=False):
                            usage = psutil.disk_usage(part.mountpoint)
                            disks = disks + templ % (part.device,
                                                bytes2human(usage.total),
                                                bytes2human(usage.used),
                                                bytes2human(usage.free))
                        return str(disks)
                    bot.sendMessage(chat_id, disks(), reply_markup=markup)    
                elif msg['text'] == "/temperatura" and chat_id:
                    bot.sendChatAction(chat_id, 'typing')
                    cpupercent = str(psutil.sensors_temperatures()) 
                    reply = cpupercent.find('current=')
                    reply += 8
                    bot.sendMessage(chat_id, "🔥 Temperatura de la CPU: " + str(reply) + "°C" , reply_markup=markup)
                elif msg['text'] == '/info' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
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
                    bot.sendMessage(chat_id, reply, reply_markup=markup)
                elif msg['text'] == "Stop":
                    clearall(chat_id)
                    bot.sendMessage(chat_id, "⛔️ Todas las operaciones se detuvieron.", reply_markup=markup)
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
                            bot.sendMessage(chat_id, "✅ Todo listo!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Por favor envíe un valor numérico apropiado mayor que 10:")
                elif msg['text'] == "/shell" and chat_id not in shellexecution:
                    bot.sendMessage(chat_id, text='''📝 Lista de comandos básicos disponibles:
                     
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
𝘀𝗵𝘂𝘁𝗱𝗼𝘄𝗻 -𝗵 𝗻𝗼𝘄 — detener el sistema;
𝗿𝗲𝗯𝗼𝗼𝘁 — reinicie el sistema;
𝗻𝗺𝗮𝗽 -𝗣𝗻 -𝗔 — escanear los hosts en la red;
...Más...
    ''')
                    time.sleep(1)
                    bot.sendMessage(chat_id, "✍️ Envíame un comando de 𝘀𝗵𝗲𝗹𝗹 para ejecutar:", reply_markup=stopmarkup)
                    shellexecution.append(chat_id)
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
                            bot.sendMessage(chat_id, "✅ Todo listo!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Por favor envíe un valor numérico adecuado por debajo de 100.")

                elif chat_id in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, reply_markup=markup)
                    else:
                        bot.sendMessage(chat_id, "❌ No hay datos de salida.", reply_markup=markup)
                elif msg['text'] == '/memgraph':
                    bot.sendChatAction(chat_id, 'typing')
                    tmperiod = "Last %.2f hours" % ((datetime.now() - graphstart).total_seconds() / 3600)
                    bot.sendPhoto(chat_id, plotmemgraph(memlist, xaxis, tmperiod))


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
    time.sleep(10)  # 10 seconds
    tr += 10
