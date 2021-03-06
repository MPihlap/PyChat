from socket import *
from select import select
from threading import *

def puhasta_järjend(järjend, sõne):
    for i in range(len(järjend)):
        if järjend[i] == sõne:
            del järjend[i]
            break

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
            nimi = uus.recv(1024).decode("utf-8") #Võetakse vastu kliendi kasutajanimi
            kasutajad = []
            for i in socketid: #Moodustatakse järjend kasutajatest ja antakse ühendunutele teada, et on uus ühenduja
                kasutajad.append(i)
                try:
                    socketid[i].send(bytes(nimi + " liitus vestlusega!\n", "utf-8"))
                except ConnectionError: #Kui mõni kasutaja ei ole enam ühendunud, asendatakse socketi info sõnega
                    socketid[i] = "PUUDUB"
                    del peasocketid[i]
                    puhasta_järjend(kasutajanimed, i)

            while "PUUDUB" in socketid.values(): #Vabanetakse vajaduse korral kadunud socketist
                for i in socketid:
                    if socketid[i] == "PUUDUB":
                        del socketid[i]
                        break

            uus.send(bytes('Tere tulemast vestlusesse "'+servnimi+'"\n', "utf-8")) #Tervitatakse ühendujat ja saadetakse juba ühendunute nimekiri
            uus.send(bytes("Teiega vestlevad: " + str(kasutajad).strip("[]") + "\n", "utf-8"))
            socketid[nimi] = uus

    (uus, addr) = s.accept() #Lisame toa looja andmed järjenditesse
    uus.send(bytes('Tere tulemast vestlusesse "' + servnimi + '"\n', "utf-8"))
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
                        for n in list(socketid):
                            try:  # Anname märku, et keegi on vestlusest lahkunud
                                socketid[n].send(bytes(i + " lahkus vestlusest!\n", "utf-8"))
                            except ConnectionError:
                                pass

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
                            socketid[n].send(bytes(i + " lahkus vestlusest!\n", "utf-8"))
                        except AttributeError:
                            pass
        while "PUUDUB" in socketid.values(): #Korrastame socketite ja ühenduste järjendi
            for n in socketid:
                if socketid[n] == "PUUDUB":
                    del socketid[n]
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
peasocketid = {} #Loome sõnastiku, kus hoitakse main serveriga liitunud socketeid

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
            if nimi in kasutajanimed: #Kui nimi on võetud, nõua uut katset
                uus.send(bytes("n","utf-8"))
            else:
                uus.send(bytes("y","utf-8"))
                kasutajanimed.append(nimi)
                break
        peasocketid[nimi] = uus
    else:
        nimi = kasutajanimi

    try:
        tahanteha = uus.recv(1024).decode("utf-8") #Kliendi otsus toa tegemise soovi kohta
        if tahanteha == "n" and len(serverid) >= 1:
            uus.send(bytes("y", "utf-8"))
            uus.send(bytes(str(serverid), "utf-8"))
            sulgemise_kontroll = uus.recv(1024).decode("utf-8") #Serverile saadetakse teatud sõnum veendumaks, et klient pole vahepeal akent sulgenud
            if sulgemise_kontroll == "": #Kui vastuseks on tühi sõne, siis on klient akna sulgenud
                del peasocketid[nimi]
                puhasta_järjend(kasutajanimed, nimi)
            elif sulgemise_kontroll == "/////TAGASI": #Kui klient vajutas Tagasi nuppu, käivita funktsioon uuesti
                määra_tuba(uus, addr, 1, nimi)
        elif tahanteha == "":
            del peasocketid[nimi]
            puhasta_järjend(kasutajanimed, nimi)
        elif tahanteha == "/////TAGASI":
            puhasta_järjend(kasutajanimed, nimi)
            määra_tuba(uus, addr, 0, "")
        else:  # Kui kasutaja soovib teha tuba või kui pole tube, millega liituda, käivita uue toa funktsioon server()
            if tahanteha == "n": #Kui klient tahab teha uut, aga see ei ole võimalik, saada vastav sõnum
                uus.send(bytes("n","utf-8"))
                tahanteha = uus.recv(1024).decode("utf-8")
            while True: #Küsib serveri nime ja kontrollib, kas see on kasutuses
                try:
                    serv_nimi = uus.recv(1024).decode("utf-8")
                    if serv_nimi == "/////TAGASI":
                        määra_tuba(uus, addr, 1, nimi)
                        break
                    if serv_nimi == "":
                        del peasocketid[nimi]
                        puhasta_järjend(kasutajanimed, nimi)
                        break
                    if serv_nimi in list(serverid):
                        uus.send(bytes("n", "utf-8"))
                    else: #Kui ei ole kasutuses ja klient ei taha tagasi minna, leia vaba port, käivita uus tuba ja saada kliendile port
                        uus.send(bytes("y", "utf-8"))
                        port = leia_port()
                        uus.send(bytes(str(port), "utf-8"))
                        serverid[serv_nimi] = port
                        server(port, serv_nimi, nimi)
                        break
                except ConnectionError:
                    del peasocketid[nimi]
                    puhasta_järjend(kasutajanimed, nimi)

    except ConnectionError: #Kui kasutaja akna sulgeb, mine eluga edasi
        del peasocketid[nimi]
        puhasta_järjend(kasutajanimed, nimi)

def uus_klient():
    (uus, addr) = main.accept() #Võta vastu uus ühendus
    kasutajathread = Thread(target=määra_tuba, args=[uus,addr,0,""]) #Loo ja käivita lõim, mis kliendiga tegeleb
    kasutajathread.daemon = True
    kasutajathread.start()
while True: #Võetakse vastu uusi ühendujaid ja luuakse nende jaoks eraldi Thread
    uus_klient()
