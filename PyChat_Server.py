from socket import *
from select import select
from threading import *

def puhasta_järjend(järjend, sõne):
    for i in range(len(järjend)):
        if i == sõne:
            del järjend[i]

def server(port,servnimi,algatajanimi): #Siit algab iga eraldi chatroom
    s = socket()
    hostname = gethostname()
    host = gethostbyname(hostname) #Loob ja seob socketi
    s.bind((host,port))
    print(hostname,host,port)
    s.listen(5)
    socketid = {} #Siia lisatakse socketid ja kasutajate nimed kujul nimi:socket

    def uus_ühendus(): #Siin tegeletakse iga uue inimesega, kes ühendub selle toaga
        while True:
            (uus, addr) = s.accept()
            nimi = uus.recv(1024).decode("utf-8")
            uus.send(bytes(str(list(socketid)),"utf-8"))
            kasutajad = []
            for i in socketid: #Moodustatakse järjend kasutajatest ja antakse ühendunutele teada, et on uus ühenduja
                kasutajad.append(i)
                try:
                    socketid[i].send(bytes(nimi + " liitus vestlusega!", "utf-8"))
                except ConnectionError: #Kui mõni kasutaja ei ole enam ühendunud, asendatakse socketi info sõnega
                    socketid[i] = "PUUDUB"
                    del peasocketid[i]
                    puhasta_järjend(kasutajanimed, i)

            while "PUUDUB" in socketid.values(): #Vabanetakse vajaduse korral kadunud socketist
                for i in socketid:
                    if socketid[i] == "PUUDUB":
                        del socketid[i]
                        #for n in range(len(kasutajanimed)):
                         #   if kasutajanimed[n] == i:
                          #      del(kasutajanimed[n])
                           #     break
                        break

            uus.send(bytes('Tere tulemast vestlusesse "'+servnimi+'"\n', "utf-8")) #Tervitatakse ühendujat ja saadetakse juba ühendunute nimekiri
            uus.send(bytes("Teiega vestlevad: " + str(kasutajad).strip("[]") + "\n", "utf-8"))
            socketid[nimi] = uus

    (uus, addr) = s.accept() #Lisame toa looja andmed järjenditesse
    uus.send(bytes('Tere tulemast vestlusesse "' + servnimi + '"', "utf-8"))
    socketid[algatajanimi] = uus

    kuula_thread = Thread(target=uus_ühendus) #Käivitame lõime, mis lisab uusi ühendujaid vestlusesse
    kuula_thread.daemon = True
    kuula_thread.start()

    while True:
        if len(socketid) == 0: #Kui toas pole kedagi, siis tuba eemaldatakse
            del serverid[servnimi]
            break

        for i in list(socketid):
            jutustab = select([socketid[i]],[],[],0.1) #Kontrollib, kas clienti socketilt on võimalik lugeda
            if jutustab[0]: #Kui socketilt on võimalik lugeda, siis saadetaks kõikidele ühendunutele vastav info
                try:
                    tekst = socketid[i].recv(1024).decode("utf-8")
                    if tekst == "/////TAGASI":
                        socketid[i].send(bytes("/////TAGASI","utf-8"))
                        print("server() funktsioonis tagasi",tekst)

                        for n in list(socketid):
                            try:  # Anname märku, et keegi on vestlusest lahkunud
                                socketid[n].send(bytes(i + " lahkus vestlusest!", "utf-8"))
                            except ConnectionError:
                                pass
                            #global main
                            #uus, addr = main.accept()
                            print("Ühendus loodi")
                            #peasocketid[i].send(bytes("Testin ühendust","utf-8"))
                        kasutajathread = Thread(target=määra_tuba, args=[peasocketid[i], addr, 1, i])  # Loo ja käivita lõim, mis kliendiga tegeleb
                        kasutajathread.daemon = True
                        kasutajathread.start()
                        socketid[i] = "PUUDUB"
                    else:
                        print(tekst)
                        for n in list(socketid):
                            try:
                                socketid[n].send(bytes(i+": "+tekst,"utf-8"))
                            except ConnectionError:
                                socketid[n] = "PUUDUB"
                                del peasocketid[n]
                                puhasta_järjend(kasutajanimed, n)
                except ConnectionError: #Kui mõni ühendus on kadunud, asendatakse socket järjendis sõnega ja eemaldatakse hiljem.
                    socketid[i] = "PUUDUB"
                    del peasocketid[i]
                    puhasta_järjend(kasutajanimed, i)

                    for n in list(socketid):
                        try: # Anname märku, et keegi on vestlusest lahkunud
                            socketid[n].send(bytes(i + " lahkus vestlusest!", "utf-8"))
                        except AttributeError:
                            pass
        while "PUUDUB" in socketid.values(): #Korrastame socketite ja ühenduste järjendi
            for n in socketid:
                if socketid[n] == "PUUDUB":
                    del socketid[n]
                    #for i in range(len(kasutajanimed)):
                     #   if kasutajanimed[i] == n:
                      #      del (kasutajanimed[i])
                       #     break
                    break



def leia_port(): #Katsetab porte, tagastab esimese vaba porti
    temps = socket()
    hostname = gethostname()
    host = gethostbyname(hostname)
    port = 12347
    while True:
        try:
            temps.bind((host, port))
            break
        except OSError:
            port += 1
    temps.close()
    return(port)


main = socket()  # Siin luuakse n-ö server hubi socket, mis hakkab ühendujaid suunama
mainhostname = gethostname()
mainhost = gethostbyname(mainhostname)
print(mainhostname, mainhost)
mainport = 12345
main.bind((mainhost, mainport))
main.listen(5)
peasocketid = {}

serverid = {} #Loome sõnastiku, millesse hakkame lisama tubade nimesid koos vastavate portidega
kasutajanimed = [] #Loome järjendi, kuhu paneme kasutajanimed, et nimed ei korduks

def määra_tuba(socket,aadress, n, kasutajanimi): #Tegeleb uute klientide otsimisega ja neile vastavalt vajadusele kas uue toa tegemisega või suunamisega
    (uus, addr) = socket,aadress
    if n == 0:
        while True:
            try:
                nimi = uus.recv(1024).decode("utf-8") #Võta vastu kliendi valitud kasutajanimi
            except ConnectionResetError:
                break
            if nimi in kasutajanimed:
                uus.send(bytes("n","utf-8"))
            else:
                uus.send(bytes("y","utf-8"))
                kasutajanimed.append(nimi)
                break
        peasocketid[nimi] = uus
    else:
        nimi = kasutajanimi

    try:
        global serverid
        print("Enne serverit")
        uus.send(bytes(str(serverid), "utf-8")) #Saadame uuele ühendujale serverite sõnastiku, mille põhjal saab klient soovi korral olemasoleva toaga ühenduda
        print("Pärast serverit")
        try:
            tahanteha = uus.recv(1024).decode("utf-8")
            print("Tahan teha",tahanteha)
            if tahanteha == "n" and len(serverid) >=1:
                sulgemise_kontroll = uus.recv(1024).decode("utf-8")
                print("Sulgemise kontroll", sulgemise_kontroll)
                if sulgemise_kontroll == "":
                    for i in range(len(kasutajanimed)):
                        if kasutajanimed[i] == nimi:
                            del (kasutajanimed[i])
                elif sulgemise_kontroll == "/////TAGASI":
                    määra_tuba(uus,addr,1,nimi)
            elif tahanteha == "":
                for i in range(len(kasutajanimed)):
                    if kasutajanimed[i] == nimi:
                        del (kasutajanimed[i])
            elif tahanteha == "/////TAGASI":
                for i in range(len(kasutajanimed)):
                    if kasutajanimed[i] == nimi:
                        del (kasutajanimed[i])
                määra_tuba(uus,addr,0,"")
            else:  # Kui kasutaja soovib teha tuba, käivita uue toa funktsioon server()
                print("Siia saime")
                try:
                    serv_saab = uus.recv(1024).decode("utf-8")
                    if serv_saab == "/////TAGASI":
                        print("saime siia")
                        määra_tuba(uus, addr, 1, nimi)
                    elif serv_saab == "y":  # Kui kliendilt saabub tühi sõne, siis on klient järelikult oma akna sulgenud.
                        servnimi = uus.recv(1024).decode("utf-8")
                        port = leia_port()
                        uus.send(bytes(str(port), "utf-8"))
                        serverid[servnimi] = port
                        server(port, servnimi, nimi)
                    else:
                        for i in range(len(kasutajanimed)):
                            if kasutajanimed[i] == nimi:
                                del (kasutajanimed[i])
                except ConnectionResetError:
                    for i in range(len(kasutajanimed)):
                        if kasutajanimed[i] == nimi:
                            del (kasutajanimed[i])
        except ConnectionAbortedError: #Kui kasutaja akna sulgeb, mine eluga edasi
            for i in range(len(kasutajanimed)):
                if kasutajanimed[i] == nimi:
                    del(kasutajanimed[i])
    except ConnectionAbortedError:  # Kui kasutaja akna sulgeb, mine eluga edasi
        for i in range(len(kasutajanimed)):
            if kasutajanimed[i] == nimi:
                del (kasutajanimed[i])
                break
"""
        else:  #Kui kasutaja soovib teha tuba, käivita uue toa funktsioon server()
            print("Siia saime")
            try:
                serv_saab = uus.recv(1024).decode("utf-8")
                if serv_saab == "/////TAGASI":
                    print("saime siia")
                    määra_tuba(uus,addr,1,nimi)
                elif serv_saab == "y": #Kui kliendilt saabub tühi sõne, siis on klient järelikult oma akna sulgenud.
                    servnimi = uus.recv(1024).decode("utf-8")
                    port = leia_port()
                    uus.send(bytes(str(port),"utf-8"))
                    serverid[servnimi] = port
                    server(port,servnimi,nimi)
                else:
                    for i in range(len(kasutajanimed)):
                        if kasutajanimed[i] == nimi:
                            del (kasutajanimed[i])
            except ConnectionResetError:
                for i in range(len(kasutajanimed)):
                    if kasutajanimed[i] == nimi:
                        del (kasutajanimed[i])
"""


def uus_klient():
    (uus, addr) = main.accept() #Võta vastu uus ühendus
    kasutajathread = Thread(target=määra_tuba, args=[uus,addr,0,""]) #Loo ja käivita lõim, mis kliendiga tegeleb
    kasutajathread.daemon = True
    kasutajathread.start()
while True: #Võetakse vastu uusi ühendujaid ja luuakse nende jaoks eraldi Thread
    uus_klient()