from socket import*
from threading import *
from select import select
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.colorchooser import *
from time import *
from winsound import *


def clear_text(entry):  # kasutatakse sisendkasti sõnumi kustutamiseks
    entry.delete("1.0", END)

def sulgemine():  # Kontrollib sulgemist
    if messagebox.askokcancel("Sulge", "Oled kindel, et tahad programmi sulgeda?"):
        sys.exit()

def tagasi(raam, eelmine_leht, chatserv, n, socket):
    try:
        raam.destroy()
    except:
        pass
    if n == 0:
        print("n = 0")
        global kasutajanimi
        kasutajanimi = ""
    if n != 2:
        chatserv.send(bytes("/////TAGASI", "utf-8"))
    if n == 2:
        socket.send(bytes("/////TAGASI","utf-8"))
        socket.close()

    eelmine_leht()

def menu():

    #Raami koostamine
    raam = Tk()
    raam.title("PyChat")
    raam.resizable(width=False, height=False)

    #Kontrollib, et kasutajanime pikkus ei oleks rohkem kui 16 tähe
    def pikkuskontroll(nimi, raam):
        while True:
            nimepikkus = len(nimi.get())
            if nimepikkus > 16:
                return messagebox.showerror("Error", "Nimi on liiga pikk (" + str(nimepikkus) + " tähte.)")
            elif nimepikkus==0:
                return messagebox.showerror("Error", "Sisestage palun nimi.")

            else:
                server.send(bytes(nimi.get(),"utf-8"))
                if server.recv(1024).decode("utf-8") == "y":
                    global kasutajanimi
                    kasutajanimi += nimi.get() #kasutaja poolt valitud nimi
                    print(kasutajanimi)
                    break
                else:
                    return messagebox.showerror("Error", "Nimi on juba kasutuses.")
        raam.destroy()
    siseraam = Frame() #raam, kuhu läheb nn login screeni widgetid ja labelid
    siseraam.grid(row=0, column=0)

    Grid.rowconfigure(raam, (0, 1), weight=1)
    Grid.columnconfigure(raam, (0), weight=1)

    tervitus = ttk.Label(siseraam, text="Tere tulemast!")
    kirjeldus = ttk.Label(siseraam, text="Sisestage oma nimi (kuni 16 tähemärki):")

    tervitus.config(font=("Helvetica", 20))
    kirjeldus.config(font=("Helvetica", 11))

    tervitus.grid(column=0, row=0)
    kirjeldus.grid(column=0, row=1, padx=5)

    nimi = Entry(siseraam, width=30)
    nimi.grid(column=0, row=2, padx=5, pady=5)
    nimi.bind('<Return>', lambda event: pikkuskontroll(nimi, raam))


    nimenupp = ttk.Button(siseraam, text="Sisene", command=lambda: (pikkuskontroll(nimi, raam)))
    nimenupp.grid(column=0, row=3, pady=5)

    raam.protocol("WM_DELETE_WINDOW",sulgemine) #küsib üle lahkumist, et kogemata kinni ei panda

    raam.mainloop()


s = socket()
serv = "172.19.24.127"
host = gethostname()
port = 12345
server = create_connection((serv, port))
toad = []


def uustuba(raam, pearaam): #juhul kui kasutaja teeb uue toa
    server.send(bytes("y","utf-8"))

    #allpool widgetide ja labelite loomine
    pearaam.destroy()

    nimiraam=Frame()
    nimiraam.grid(row=0, column=0)

    nimitekst=ttk.Label(nimiraam, text="Sisestage uue toa nimi: ", font=("Helvetica", 14, "bold"))
    nimitekst.grid(row=1, column=0, sticky=(W), padx=5, pady=2)

    nimikast=ttk.Entry(nimiraam)
    nimikast.grid(row=2, column=0, sticky=(W, E), padx=5, pady=5)

    niminupp=ttk.Button(nimiraam, text="Sisene", command=lambda: chatituba("<Return>"))
    niminupp.grid(row=3, column=0, padx=5, sticky=(W, E), pady=3)


    tagasinupp=ttk.Button(nimiraam, text="Tagasi", command= lambda:tagasi(raam, chatiruum, server,1,""))
    tagasinupp.grid(row=4, column=0, padx=5, pady=3, sticky=(W, E))


    def chatituba(event): #funktsioon chatitoa kuvamiseks
        kas_sobib = ""
        serv_nimi=nimikast.get()
        if serv_nimi == "":
            messagebox.showerror("Error","Sisestage palun nimi!")
        else:
            server.send(bytes(serv_nimi,"utf-8"))
            kas_sobib = server.recv(1024).decode("utf-8")
        if kas_sobib == "n":
            messagebox.showerror("Error","Sellise nimega tuba on juba olemas!")

        else:
            uusport = int(server.recv(1024).decode("utf-8"))  # Võtan vastu porti, mille määrab server
            connection = create_connection((serv, uusport))

            def loe(connection):
                textbox.tag_configure("BOLD", background="#d1e4ff")  # stiliseerib kasutaja sõnumi ära
                while True:
                    aeg = "[" + asctime(localtime()).split()[3] + "]"
                    serv_räägib = select([connection], [], [], 0.1) #ootab serverilt tagasisidet
                    #allpool kuvatakse serverilt saadud info tekstikasti
                    if serv_räägib[0]:
                        try:
                            sõnum = connection.recv(1024).decode("utf-8")
                            if sõnum == "/////TAGASI":
                                break
                        except OSError:
                            break
                        sisendkast.configure(state="normal") #muudab sisendkasti tagasi redigeeritavaks (kuna kirjuta funktsioonis allpool see muudetakse mitteredigeeritavaks ühe teatud kala vältimiseks)
                        textbox.configure(state="normal")#tekstikasti muudetakse redigeeritavaks, et saaks sinna sõnum sisestada

                        if kasutajanimi == sõnum[0:len(kasutajanimi)] and sõnum[len(kasutajanimi)]==":": #tuvastab ära kliendipoolse kasutajanime
                            textbox.insert(INSERT, aeg+" "+sõnum, ("BOLD"))

                        else:
                            helivalik=valik.get()
                            print(helivalik)
                            if sisendkast == sisendkast.focus_get() or sõnum=='Tere tulemast vestlusesse "' + serv_nimi + '"': #juhul kui ei ole fokuseeritud
                                textbox.insert(INSERT, sõnum)
                            else:
                                if helivalik == 1:
                                    Beep(440, 150)  # teeb heli
                                    textbox.insert(INSERT, aeg+" "+sõnum)
                                else:
                                    textbox.insert(INSERT, aeg+" "+sõnum)

                        textbox.insert(END, "\n")
                        textbox.configure(state="disabled") #tagasi mitteredigeeritavaks
                        textbox.see("end") #näitab kohe viimast sõnumit

                    if sisendkast.cget("state")=="disabled": #juhul kui kasutaja sisestab tühja sõnumi
                        sisendkast.configure(state="normal")




            def kirjuta(connection): #saadab sisendkasti teksti serverile
                sõnum=sisendkast.get("1.0","end-1c")

                while True:

                    connection.send(bytes(sõnum, "utf-8"))
                    break
                clear_text(sisendkast)
                sisendkast.configure(state="disabled")
                textbox.see("end")

            def värv(valikud):
                värv = askcolor(parent=valikud)
                return textbox.tag_configure("BOLD", background=värv[1])

            try: #hävitab ebavajalikud widgetid ja raamid
                while nimiraam.winfo_exists()==1:
                    nimiraam.destroy()
                niminupp.destroy()
                poletuba_silt.destroy()

            except NameError:
                pass

            tekstiraam=Frame()

            raam.title(serv_nimi) #muudab programmi nime toa nimeks

            tekstiraam.grid(row=3, column=0)

            textbox=Text(tekstiraam, height=10, width=50, padx=5, state="disabled", wrap=WORD) #tekstikast, kuhu saabuvad sõnumid
            textbox.grid(row=0, column= 0)

            scrollbar=Scrollbar(tekstiraam, command=textbox.yview) #teeb tekstikasti scrollitavaks
            textbox['yscrollcommand']=scrollbar.set

            sisendkast=Text(tekstiraam, height=5, width=50, padx=5, wrap=WORD) #sisendkast, kuhu kasutaja sisestab sõnumi
            sisendkast.grid(row=1, column=0)
            sisendkast.bind('<Return>', lambda event: kirjuta(connection)) #seob funktsiooni enteri klahvile



            sisendnupp = ttk.Button(tekstiraam, text="Saada", command=lambda: kirjuta(connection)) #seob funktsiooni enteri klahvile
            sisendnupp.grid(column=0, row=2, padx=5, sticky=(W), pady=5)

            def valikukontroll(valikud, valik):
                valiknupp.configure(state=NORMAL)
                valikud.destroy()

                return valik


            def valikuaken(valik):

                valiknupp.configure(state=DISABLED)

                valikud=Tk()
                valikud.title("Valikud")
                valikud.resizable(width=False, height=False)
                valikud.wm_attributes("-topmost", 1)
                valikud.focus_force()


                värvinupp = ttk.Button(valikud, text="Teksti värv", command=lambda: värv(valikud))
                värvinupp.grid(row=0, column=0, padx=10, pady=5, sticky=(W, E))

                helinupp = ttk.Checkbutton(valikud, text="Heli", variable=valik)

                helinupp.grid(row=1, column=0, padx=10, pady=5)

                valikutagasinupp=ttk.Button(valikud, text="Sulge", command=lambda: valikukontroll(valikud, valik))
                valikutagasinupp.grid(row=2, column=0, pady=10)

                valikud.protocol("WM_DELETE_WINDOW", lambda: valikukontroll(valikud, valik))

            valik = IntVar()
            valik.set(1)

            valiknupp=ttk.Button(tekstiraam, text="Valikud", command=lambda: valikuaken(valik))
            valiknupp.grid(row=2, column=0, padx=5, pady=5)

            tagasinupp = ttk.Button(tekstiraam, text="Tagasi", command=lambda: tagasi(raam, chatiruum, server, 2, connection))
            tagasinupp.grid(row=2, column=0, padx=5, pady=5, sticky=E)

            thread1 = Thread(target=lambda: loe(connection))
            thread1.daemon = True
            thread1.start()


    nimikast.bind('<Return>', chatituba)


def olemastuba(raam, server, pearaam): #juhul kui kasutaja tahab olemasoleva toaga liituda
    server.send(bytes("n","utf-8"))
    kas_saab = server.recv(1024).decode("utf-8")
    uued_toad = eval(server.recv(1024).decode("utf-8"))
    toa_nimed = list(uued_toad)
    toanimed = str(toa_nimed).strip("[]")

    if kas_saab != "y": #juhul kui tube pole, läheb uustoa funktsiooni
        global poletuba_silt
        messagebox.showinfo("Error", "Paistab, et hetkel pole saadaval ühtegi tuba. Loon uue toa...")
        uustuba(raam, pearaam)

    else:
        pearaam.destroy()

        nimiraam = Frame()
        nimiraam.grid(row=2, column=0)

        toanimesilt=ttk.Label(nimiraam, text="Olemasolevad toad:")
        toanimesilt.grid(row=0, column=0)

        toanimed=ttk.Label(nimiraam, text=toanimed)
        toanimed.grid(row=1 ,column=0)

        nimitekst = ttk.Label(nimiraam, text="Sisesta toa nimi, millega soovid liituda:", font=("Helvetica", 10, "bold"))
        nimitekst.grid(row=2, column=0, padx=5, pady=2)

        toakast = ttk.Entry(nimiraam, width=35) #kasutaja saab sisestada toanime, millega soovib liituda
        toakast.grid(row=3, column=0, padx=5, pady=7, sticky=(W, E))

        nupuraam=Frame()
        nupuraam.grid(row=3, column=0)

        niminupp = ttk.Button(nimiraam, text="Sisene", command=lambda: chatituba("<Return>"))
        niminupp.grid(row=4, column=0, padx=5,pady=2, sticky=(W, E))

        tagasinupp = ttk.Button(nimiraam, text="Tagasi", command=lambda: tagasi(raam, chatiruum, "",1,""))
        tagasinupp.grid(row=5, column=0, padx=5, pady=2, sticky=(W, E))

    def chatituba(event):
        server.send(bytes("Suvaline sõne","utf-8"))

        tuba=toakast.get() #võtab kasutaja sisestatud toa nime

        #kontrollitakse toanime
        try:
            uusport = uued_toad[tuba]
        except KeyError:
            return messagebox.showerror("Error", "Sellist toanime ei leidu.")

        connection = create_connection((serv, uusport)) #luuakse ühendus
        connection.send(bytes(kasutajanimi,"utf-8"))

        # allpool olevad funktsioonid on sarnaselt olemas uustuba funktsiooni all, vt sealt täpsemalt seletust

        def loe(connection,serv_nimi):
            textbox.tag_configure("BOLD", background="#d1e4ff")  # stiliseerib kasutaja sõnumi ära
            while True:
                aeg = "[" + asctime(localtime()).split()[3] + "]"
                serv_räägib = select([connection], [], [], 0.1)
                if serv_räägib[0]:
                    try:
                        sõnum = connection.recv(1024).decode("utf-8")
                        if sõnum == "/////TAGASI":
                            break
                    except OSError:
                        break

                    sisendkast.configure(state="normal")
                    textbox.configure(state="normal")
                    if kasutajanimi == sõnum[0:len(kasutajanimi)] and sõnum[len(kasutajanimi)] == ":":
                        textbox.insert(INSERT, aeg+" "+sõnum, ("BOLD"))
                    else:
                        helivalik = valik.get()
                        if sisendkast == sisendkast.focus_get() or 'Tere tulemast vestlusesse "' + serv_nimi + '"' in sõnum[:28+len(sõnum)]:  # juhul kui ei ole fokuseeritud
                            textbox.insert(INSERT, sõnum)
                        else:
                            if helivalik==1:
                                Beep(440, 150)  # teeb heli
                                textbox.insert(INSERT, aeg+" "+sõnum)
                            else:
                                textbox.insert(INSERT, aeg+" "+sõnum)


                    textbox.insert(END, "\n")
                    textbox.configure(state="disabled")
                    textbox.see("end")
                if sisendkast.cget("state") == "disabled":
                    sisendkast.configure(state="normal")

        def kirjuta(connection):
            sõnum = sisendkast.get("1.0", "end-1c")

            while True:
                connection.send(bytes(sõnum, "utf-8"))
                break

            clear_text(sisendkast)
            sisendkast.configure(state="disabled")
            textbox.see("end")

        def värv(valikud):
            värv = askcolor(parent=valikud)
            return textbox.tag_configure("BOLD", background=värv[1])


        nupuraam.destroy()
        nimiraam.destroy()

        tekstiraam = Frame()
        tekstiraam.grid(row=3, column=0)

        raam.title(tuba)

        textbox = Text(tekstiraam, height=10, width=50, padx=5, state="disabled", wrap=WORD)
        textbox.grid(row=0, column=0)

        scrollbar = Scrollbar(tekstiraam, command=textbox.yview)
        textbox['yscrollcommand'] = scrollbar.set

        sisendkast = Text(tekstiraam, height=5, width=50, padx=5, wrap=WORD)
        sisendkast.grid(row=1, column=0)
        sisendkast.bind('<Return>', lambda event: kirjuta(connection))

        sisendnupp = ttk.Button(tekstiraam, text="Saada", command=lambda: kirjuta(connection))
        sisendnupp.grid(column=0, row=2, padx=5, sticky=(W), pady=5)

        def valikukontroll(valikud, valik):
            valiknupp.configure(state=NORMAL)
            valikud.destroy()

            return valik

        def valikuaken(valik):

            valiknupp.configure(state=DISABLED)

            valikud = Tk()
            valikud.title("Valikud")
            valikud.resizable(width=False, height=False)
            valikud.wm_attributes("-topmost", 1)
            valikud.focus_force()

            värvinupp = ttk.Button(valikud, text="Teksti värv", command=lambda: värv(valikud))
            värvinupp.grid(row=0, column=0, padx=10, pady=5, sticky=(W, E))

            helinupp = ttk.Checkbutton(valikud, text="Heli", variable=valik, state=ACTIVE)
            helinupp.grid(row=1, column=0, padx=10, pady=5)

            valikutagasinupp = ttk.Button(valikud, text="Sulge", command=lambda: valikukontroll(valikud, valik))
            valikutagasinupp.grid(row=2, column=0, pady=10)

            valikud.protocol("WM_DELETE_WINDOW", lambda: valikukontroll(valikud, valik))

        valik = IntVar()
        valik.set(1)

        valiknupp = ttk.Button(tekstiraam, text="Valikud", command=lambda: valikuaken(valik))
        valiknupp.grid(row=2, column=0, padx=5, pady=5)

        tagasinupp = ttk.Button(tekstiraam, text="Tagasi", command=lambda: tagasi(raam, chatiruum, server,2,connection))
        tagasinupp.grid(row=2, column=0, padx=5, pady=5, sticky=E)


        #eraldi thread loe funktsiooni jaoks, et saaks pidevalt andmeid vastu võtta
        thread1 = Thread(target=lambda: loe(connection,tuba))
        thread1.daemon = True
        thread1.start()

    try:
        toakast.bind('<Return>',chatituba) #seotakse chatituba funktsioon enteri klahviga
    except UnboundLocalError:
        pass

def chatiruum(): #valikmenüü peale nn 'sisselogimismenüüd'
    if kasutajanimi == "":
        menu()
    raam = Tk()
    raam.title("PyChat")
    raam.resizable(width=False, height=False)

    pearaam= Frame()
    pearaam.grid(column=0, row=0)
    nupuraam=Frame(master=pearaam)
    nupuraam.grid(column=0, row=0)

    uustubanupp=ttk.Button(nupuraam, text="Loo uus tuba", command= lambda: uustuba(raam, pearaam))
    uustubanupp.grid(column=0, row=0, padx=5, sticky=(W),pady=5 )

    olemastoanupp=ttk.Button(nupuraam, text="Liitu olemasolevaga",command=lambda:olemastuba(raam,server, pearaam))
    olemastoanupp.grid(column=1, row=0, padx=5, sticky=(W),pady=5 )

    tagasiraam=Frame(master=pearaam)
    tagasiraam.grid(row=1, column=0)

    tagasinupp=ttk.Button(tagasiraam, text="Tagasi", command= lambda:tagasi(raam, chatiruum, server,0,""))
    tagasinupp.grid(column=0, row=0, padx=5, pady=5, sticky=W+E)


    raam.mainloop()

kasutajanimi = ""
chatiruum()

