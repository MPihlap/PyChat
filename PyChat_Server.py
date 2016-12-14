from socket import *
from select import select
from threading import *


def server(port,servnimi,algatajanimi): #Siit algab iga eraldi chatroom
    #print("Siin ei leia",serverid)
    s = socket()
    hostname = gethostname()
    host = gethostbyname(hostname)
    s.bind((host,port))
    print(hostname,host,port)
    s.listen(5)
    ühendused = [] #Siia lisatakse socketite kasutajate nimed ja aadressid
    socketid = [] #Siia lisatakse socketid, mille poole hakatakse otse pöörduma aka kasutajate socketid
    #Need kaks luuakse nii, et socketite ja nimede indeksid kattuvad, et oleks lihtne pöörduda

    def uus_ühendus(algatajanimi):
        (uus, addr) = s.accept()
        nimi = uus.recv(1024).decode("utf-8")
        print("See on nimi elleroooo",nimi)
        for i in range(len(socketid)):
            try:
                socketid[i].send(bytes(nimi + " liitus vestlusega!", "utf-8"))
            except ConnectionResetError:
                socketid[i] = "PUUDUB"
        if "PUUDUB" in socketid:
            for i in range(len(socketid)):
                print(socketid[i])
                try:
                    if socketid[i] == "PUUDUB":
                        del socketid[i]
                except IndexError:
                    pass
        uus.send(bytes('Tere tulemast vestlusesse "'+servnimi+'"', "utf-8"))
        socketid.append(uus)
        nim = [addr, nimi]
        return nim

    def kuula(): #Thread, mis tegeleb uute ühenduste otsimisega (chatroomi sees)
        while True:
            connection = uus_ühendus(algatajanimi)
            ühendused.append(connection)
            print(ühendused)

    (uus, addr) = s.accept() #Lisame toa looja andmed järjenditesse
    nim = [addr, algatajanimi]
    uus.send(bytes('Tere tulemast vestlusesse "' + servnimi + '"', "utf-8"))
    socketid.append(uus)
    ühendused.append(nim)

    kuula_thread = Thread(target=kuula)
    kuula_thread.daemon = True
    kuula_thread.start()
    while True:
        if len(socketid) == 0:
            del serverid[servnimi]
            print("Kustutasin serveri",serverid)
            break
        for i in range(len(socketid)):
            try:
                jutustab = select([socketid[i]],[],[],0.1)
            except TypeError:
                pass

            if jutustab[0]:
                try:
                    tekst = socketid[i].recv(1024).decode("utf-8")
                    print(tekst)
                    for n in range(len(socketid)):
                        socketid[n].send(bytes(ühendused[i][1]+": "+tekst,"utf-8"))
                except ConnectionResetError:
                    socketid[i] = "PUUDUB"
                    for n in range(len(socketid)):
                        try:
                            socketid[n].send(bytes(ühendused[i][1] + " lahkus vestlusest!", "utf-8"))
                        except AttributeError:
                            pass
        if "PUUDUB" in socketid:
            for n in range(len(socketid)):
                try:
                    if socketid[n] == "PUUDUB":
                        del socketid[n]
                        del ühendused[n]
                except IndexError:
                    pass



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


main = socket()  # Siin luuakse n-ö server hub
mainhostname = gethostname()
mainhost = gethostbyname(mainhostname)
print(mainhostname, mainhost)
mainport = 12345
main.bind((mainhost, mainport))
main.listen(5)

serverid = {}

def uus_klient(): #Tegeleb uute klientide otsimisega ja neile vastavalt vajadusele kas uue toa tegemisega või suunamisega
    try:
        (uus, addr) = main.accept()
        nimi = uus.recv(1024).decode("utf-8")
        global serverid
        print("See on nimi:",nimi)
        print("Need on serverid:",serverid)
        uus.send(bytes(str(serverid), "utf-8"))
        print("Kas siit mööda?")
        try:
            if uus.recv(1024).decode("utf-8") == "n" and len(serverid) >=1:
                print(serverid)
        except ConnectionAbortedError:
            pass
        else:
    #if uus.recv(1024).decode("utf-8") == "y": #Siin toimub dialoog [DIA], luuakse uus server
            servnimi = uus.recv(1024).decode("utf-8")
            if servnimi != "":
                print("See on servnimi elleroo",servnimi)
                port = leia_port()
                print(port)
                uus.send(bytes(str(port),"utf-8"))
                serverid[servnimi] = port
                print("Need on serverid elleroo",serverid)
                mainthread = Thread(target=server,args=[port,servnimi,nimi])
                mainthread.daemon = True
                mainthread.start()
    except ConnectionResetError:
        pass






while True:
    uus_klient()

