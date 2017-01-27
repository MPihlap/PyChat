from socket import*
from threading import *
from select import select
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from winsound import *



def sulgemine(): #Kontrollib sulgemist
    if messagebox.askokcancel("Sulge", "Oled kindel, et tahad programmi sulgeda?"):
        sys.exit()

def tagasi(raam, eelmine_leht, server):
    try:
        raam.destroy()
    except:
        pass
    server.send(bytes("/////TAGASI","utf-8"))
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

    return kasutajanimi


s = socket()
serv = "10.0.102.77"
#serv = "40.69.82.163"
host = gethostname()
port = 12345
server = create_connection((serv, port))
toad = []


def uustuba(raam, nimi, nupuraam, toad): #juhul kui kasutaja teeb uue toa

    #allpool widgetide ja labelite loomine
    nupuraam.destroy()

    nimiraam=Frame()
    nimiraam.grid(row=2, column=0)

    nimitekst=ttk.Label(nimiraam, text="Sisesta toa nimi: ", font=("Helvetica", 10, "bold"))
    nimikast=ttk.Entry(nimiraam)
    niminupp=ttk.Button(raam, text="Sisene", command=lambda: chatituba("<Return>"))


    nimitekst.grid(row=1, column=0, sticky=(W), padx=5, pady=2)
    nimikast.grid(row=2, column=0, sticky=(W), padx=5, pady=5)
    niminupp.grid(row=2, column=1, padx=5, sticky=(S), pady=5)


    def chatituba(event): #funktsioon chatitoa kuvamiseks

        serv_nimi=nimikast.get()
        if serv_nimi in toad:
            messagebox.showerror("Error","Sellise nimega tuba on juba olemas!")
        elif len(serv_nimi)!=0:
            server.send(bytes("y", "utf-8"))  # Saadan vastuse, kas tahan või ei taha teha tuba
            server.send(bytes(serv_nimi, "utf-8"))  # Saadan nime
            uusport = int(server.recv(1024).decode("utf-8"))  # Võtan vastu porti, mille määrab server
            #kasutajad = server.recv(1024).decode("utf-8")
            connection = create_connection((serv, uusport))

            def loe(connection):
                while True:
                    serv_räägib = select([connection], [], [], 0.1) #ootab serverilt tagasisidet
                    #allpool kuvatakse serverilt saadud info tekstikasti
                    if serv_räägib[0]:
                        sõnum = connection.recv(1024).decode("utf-8")
                        textbox.tag_configure("BOLD",  background="#d1e4ff") #stiliseerib kasutaja sõnumi ära
                        sisendkast.configure(state="normal") #muudab sisendkasti tagasi redigeeritavaks (kuna kirjuta funktsioonis allpool see muudetakse mitteredigeeritavaks ühe teatud kala vältimiseks)
                        textbox.configure(state="normal")#tekstikasti muudetakse redigeeritavaks, et saaks sinna sõnum sisestada

                        if kasutajanimi == sõnum[0:len(kasutajanimi)] and sõnum[len(kasutajanimi)]==":": #tuvastab ära kliendipoolse kasutajanime
                            textbox.insert(INSERT, sõnum, ("BOLD"))

                        else:
                            if sisendkast == sisendkast.focus_get() or sõnum=='Tere tulemast vestlusesse "' + serv_nimi + '"': #juhul kui ei ole fokuseeritud
                                textbox.insert(INSERT, sõnum)
                            else:
                                Beep(440, 150)  # teeb heli siis, kui on fokuseeritud aknale
                                textbox.insert(INSERT, sõnum)


                        textbox.insert(END, "\n")
                        textbox.configure(state="disabled") #tagasi mitteredigeeritavaks
                        textbox.see("end") #näitab kohe viimast sõnumit

                    if sisendkast.cget("state")=="disabled": #juhul kui kasutaja sisestab tühja sõnumi
                        sisendkast.configure(state="normal")


            def clear_text(entry): #kasutatakse sisendkasti sõnumi kustutamiseks
                entry.delete("1.0", END)

            def kirjuta(connection): #saadab sisendkasti teksti serverile
                sõnum=sisendkast.get("1.0","end-1c")

                while True:

                    connection.send(bytes(sõnum, "utf-8"))
                    break
                clear_text(sisendkast)
                sisendkast.configure(state="disabled")
                textbox.see("end")

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

            thread1 = Thread(target=lambda: loe(connection))
            thread1.daemon = True
            thread1.start()







    nimikast.bind('<Return>', chatituba)


def olemastuba(raam, server, nimi, toad, nupuraam): #juhul kui kasutaja tahab olemasoleva toaga liituda
    toa_nimed = []
    for i in toad:
        toa_nimed.append(i)
    toanimed = str(toa_nimed).strip("[]")

    if len(toad)==0: #juhul kui tube pole, läheb uustoa funktsiooni
        global poletuba_silt
        messagebox.showinfo("Error", "Paistab, et hetkel pole saadaval ühtegi tuba. Loon uue toa...")
        uustuba(raam,kasutajanimi, nupuraam, server)

    else:
        server.send(bytes("n", "utf-8")) # Saadan vastuse, et ei taha teha tuba
        nupuraam.destroy()

        nimiraam = Frame()
        nimiraam.grid(row=2, column=0)

        toanimesilt=ttk.Label(nimiraam, text="Toa nimed:")
        toanimesilt.grid(row=0, column=0)

        toanimed=ttk.Label(nimiraam, text=toanimed)
        toanimed.grid(row=1 ,column=0)

        nimitekst = ttk.Label(nimiraam, text="Sisesta toa nimi, millega soovid liituda:", font=("Helvetica", 10, "bold"))
        nimitekst.grid(row=2, column=0, padx=5, pady=2)

        toakast = ttk.Entry(nimiraam, width=35) #kasutaja saab sisestada toanime, millega soovib liituda
        toakast.grid(row=3, column=0, padx=5, pady=2)

        niminupp = ttk.Button(raam, text="Sisene", command=lambda: chatituba("<Return>"))
        niminupp.grid(row=3, column=0, padx=5,pady=1)

    def chatituba(event):

        tuba=toakast.get() #võtab kasutaja sisestatud toa nime

        #kontrollitakse toanime
        try:
            uusport = toad[tuba]
        except KeyError:
            return messagebox.showerror("Error", "Sellist toanime ei leidu.")


        connection = create_connection((serv, uusport)) #luuakse ühendus
        connection.send(bytes(kasutajanimi,"utf-8"))
        kasutajad = eval(connection.recv(1024).decode("utf-8"))

        # allpool olevad funktsioonid on sarnaselt olemas uustuba funktsiooni all, vt sealt täpsemalt seletust

        def loe(connection,serv_nimi):
            while True:
                serv_räägib = select([connection], [], [], 0.1)
                if serv_räägib[0]:
                    sõnum = connection.recv(1024).decode("utf-8")
                    textbox.tag_configure("BOLD",  background="#d1e4ff")

                    sisendkast.configure(state="normal")
                    textbox.configure(state="normal")
                    if kasutajanimi == sõnum[0:len(kasutajanimi)] and sõnum[len(kasutajanimi)] == ":":
                        textbox.insert(INSERT, sõnum, ("BOLD"))
                    else:

                        if sisendkast == sisendkast.focus_get() or sõnum == 'Tere tulemast vestlusesse "' + serv_nimi + '"': #juhul kui ei ole fokusseeritud
                            textbox.insert(INSERT, sõnum)
                        else:
                            Beep(440, 150)  # teeb heli
                            textbox.insert(INSERT, sõnum)

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

            def clear_text(entry):
                entry.delete("1.0", END)

            clear_text(sisendkast)
            sisendkast.configure(state="disabled")
            textbox.see("end")


        nupuraam.destroy()
        niminupp.destroy()
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


        #eraldi thread loe funktsiooni jaoks, et saaks pidevalt andmeid vastu võtta
        thread1 = Thread(target=lambda: loe(connection,tuba))
        thread1.daemon = True
        thread1.start()


    try:
        toakast.bind('<Return>',chatituba) #seotakse chatituba funktsioon enteri klahviga
    except UnboundLocalError:
        pass


def chatiruum(): #valikmenüü peale nn 'sisselogimismenüüd'

    menu()
    raam = Tk()
    raam.title("UTChat")
    raam.resizable(width=False, height=False)

    nupuraam= Frame()
    nupuraam.grid(column=0, row=0)
    #server.send(bytes(kasutajanimi,"utf-8")) #saadab kasutajanime
    toad = eval(server.recv(1024).decode("utf-8")) #saab serverilt olemasolevad toad koos vastavate portidega

    uustubanupp=ttk.Button(nupuraam, text="Tee uus tuba", command= lambda: uustuba(raam,kasutajanimi, nupuraam,toad))
    uustubanupp.grid(column=0, row=0, padx=5, sticky=(W),pady=5 )

    olemastoanupp=ttk.Button(nupuraam, text="Liitu olemasolevaga",command=lambda:olemastuba(raam,server,kasutajanimi,toad, nupuraam))
    olemastoanupp.grid(column=1, row=0, padx=5, sticky=(W),pady=5 )

    tagasinupp=ttk.Button(raam, text="Tagasi", command= lambda:tagasi(raam, chatiruum, server))
    tagasinupp.grid(column=0, row=1, padx=5, pady=5)



    raam.mainloop()



kasutajanimi = ""
chatiruum()

