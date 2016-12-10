from socket import*
from threading import *
from select import select
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import sleep
#from testclient import *

def sulgemine():
    if messagebox.askokcancel("Sulge", "Oled kindel, et tahad programmi sulgeda?"):
        sys.exit()


def clear_text(entry):
    entry.delete(1.0,END)
def menu():
    #global kasutajanimi
    #kasutajanimi = ""
    raam = Tk()
    raam.title("UTChat")
    raam.resizable(width=False, height=False)

    def pikkuskontroll(nimi, raam):
        while True:
            nimepikkus = len(nimi.get())
            if nimepikkus > 16:
                return messagebox.showerror("Error", "Nimi on liiga pikk (" + str(nimepikkus) + " tähte.)")
            elif nimepikkus==0:
                return messagebox.showerror("Error", "Sisestage palun nimi.")

            else:
                global kasutajanimi
                kasutajanimi += nimi.get()
                print(kasutajanimi)
                break
        raam.destroy()
    siseraam = Frame()

    siseraam.grid(row=0, column=0)

    Grid.rowconfigure(raam, (0, 1), weight=1)
    Grid.columnconfigure(raam, (0), weight=1)

    tervitus = ttk.Label(siseraam, text="Tere tulemast!")
    kirjeldus = ttk.Label(siseraam, text="Sisestage oma nimi (kuni 16 tähemärki):")
    tervitus.config(font=("", 20))
    kirjeldus.config(font=("", 11))
    tervitus.grid(column=0, row=0)
    kirjeldus.grid(column=0, row=1, padx=5)

    nimi = Entry(siseraam, width=30)
    nimi.grid(column=0, row=2, padx=5, pady=5)
    nimenupp = ttk.Button(siseraam, text="Sisene", command=lambda: (pikkuskontroll(nimi, raam)))
    nimenupp.grid(column=0, row=3, pady=5)
    nimi.bind('<Return>', lambda event: pikkuskontroll(nimi, raam))

    print("kasutajanimi:",kasutajanimi)

    raam.protocol("WM_DELETE_WINDOW",sulgemine)

    raam.mainloop()
    return kasutajanimi


s = socket()
serv = "192.168.1.132"
host = gethostname()
print(host)
port = 12345
server = create_connection((serv, port))
toad = []
#nimi = "asd"
#server.send(bytes(nimi.encode("utf-8")))

def uustuba(raam, nimi, nupuraam):
    nupuraam.destroy()

    nimiraam=Frame()
    nimiraam.grid(row=2, column=0)

    nimitekst=ttk.Label(nimiraam, text="Sisesta toa nimi:")
    nimikast=ttk.Entry(nimiraam)

    nimitekst.grid(row=2, column=0, sticky=(W))
    nimikast.grid(row=2, column=1, sticky=(W))


    def func(event):
        serv_nimi=nimikast.get()
        if len(serv_nimi)!=0:
            server.send(bytes("y", "utf-8"))  # Saadan vastuse, kas tahan või ei taha teha tuba
            server.send(bytes(serv_nimi, "utf-8"))  # Saadan nime
            uusport = int(server.recv(1024).decode("utf-8"))  # Võtan vastu porti, mille määrab server
            print("uusport:", uusport)
            print(serv, uusport)
            cd = create_connection((serv, uusport))

            def loe(cd):
                while True:
                    serv_räägib = select([cd], [], [], 0.1)
                    if serv_räägib[0]:
                        a = cd.recv(1024).decode("utf-8")
                        textbox.tag_configure("BOLD",  background="#F3F6FA")

                        print(a)
                        sisendkast.configure(state="normal")
                        textbox.configure(state="normal")
                        if kasutajanimi in a[0:len(kasutajanimi)]:
                            textbox.insert(INSERT, a, ("BOLD"))
                        else:
                            textbox.insert(INSERT, a)

                        #textbox.insert(INSERT, nimi + ":" + " " + a)
                        textbox.insert(END, "\n")
                        textbox.configure(state="disabled")
                        textbox.see("end")

            thread1 = Thread(target=lambda:loe(cd))
            thread1.daemon = True
            thread1.start()

            def clear_text(entry):
                entry.delete("1.0", END)

            def kirjuta(cd):
                a=sisendkast.get("1.0","end-1c")
                #textbox.insert(INSERT, nimi+":"+" "+a)
                #textbox.insert(END, "\n" )
                while True:
                    cd.send(bytes(a, "utf-8"))
                    break
                clear_text(sisendkast)
                sisendkast.configure(state="disabled")
                textbox.see("end")


            try:
                while nimiraam.winfo_exists()==1:
                    nimiraam.destroy()
                poletuba_silt.destroy()
            except NameError:
                pass

            tekstiraam=Frame()

            tekstiraam.grid(row=3, column=0)

            textbox=Text(tekstiraam, height=10, width=50, padx=5, state="disabled")
            textbox.grid(row=0, column= 0)

            scrollbar=Scrollbar(tekstiraam, command=textbox.yview)
            textbox['yscrollcommand']=scrollbar.set

            sisendkast=Text(tekstiraam, height=5, width=50, padx=5)
            sisendkast.grid(row=1, column=0)
            sisendkast.bind('<Return>', lambda event: kirjuta(cd))



            sisendnupp = ttk.Button(tekstiraam, text="Saada", command=lambda: kirjuta(cd))
            sisendnupp.grid(column=0, row=2, padx=5, sticky=(W), pady=5)




            #return cd, func('<Return>')




    nimikast.bind('<Return>', func)


def olemastuba(raam, server, nimi, toad, nupuraam):
    #server.send(bytes("n", "utf-8"))  # Saadan vastuse, kas tahan või ei taha teha tuba
    print(server)
    #toad = eval(server.recv(1024).decode("utf-8"))
    if len(toad)==0:
        global poletuba_silt
        messagebox.showinfo("Error", "Paistab, et hetkel pole saadaval ühtegi tuba. Loon uue toa...")
        #sleep(2)
        #poletuba_silt.destroy()
        uustuba(raam,kasutajanimi, nupuraam)
    else:
        server.send(bytes("n", "utf-8"))
        nupuraam.destroy()

        nimiraam = Frame()
        nimiraam.grid(row=2, column=0)

        toanimesilt=ttk.Label(nimiraam, text="Toa nimed:")
        toanimesilt.grid(row=0, column=0)

        toanimed=ttk.Label(nimiraam, text=toad)
        toanimed.grid(row=1 ,column=0)

        nimitekst = ttk.Label(nimiraam, text="Sisesta toa nimi, millega soovid liituda:")
        nimitekst.grid(row=2, column=0)

        toakast = ttk.Entry(nimiraam)
        toakast.grid(row=3, column=0, sticky=(W))




    def func(event):
        tuba=toakast.get()
        #server.send(bytes(tuba, "utf-8"))
        try:
            uusport = toad[tuba]
        except KeyError:
            return messagebox.showerror("Error", "Sellist toanime ei leidu.")

        print("uusport:", uusport)
        print(serv, uusport)
        cd = create_connection((serv, uusport))
        cd.send(bytes(kasutajanimi,"utf-8"))

        def loe(cd):
            while True:
                serv_räägib = select([cd], [], [], 0.1)
                if serv_räägib[0]:
                    a = cd.recv(1024).decode("utf-8")
                    textbox.tag_configure("BOLD",  background="#F3F6FA")

                    print(a)
                    sisendkast.configure(state="normal")
                    textbox.configure(state="normal")
                    if kasutajanimi in a[0:len(kasutajanimi)]:
                        textbox.insert(INSERT, a, ("BOLD"))
                    else:
                        textbox.insert(INSERT, a)

                    # textbox.insert(INSERT, nimi + ":" + " " + a)
                    textbox.insert(END, "\n")
                    textbox.configure(state="disabled")
                    textbox.see("end")

        #thread1 = Thread(target=lambda:loe(cd))
        #thread1.daemon = True
        #thread1.start()

        def kirjuta(cd):
            a = sisendkast.get("1.0", "end-1c")
            #textbox.insert(INSERT, nimi+":"+" "+a)
            #textbox.insert(END, "\n" )
            while True:
                cd.send(bytes(a, "utf-8"))
                break

            def clear_text(entry):
                entry.delete("1.0", END)

            clear_text(sisendkast)
            sisendkast.configure(state="disabled")
            textbox.see("end")

        nupuraam.destroy()
        nimiraam.destroy()

        tekstiraam = Frame()

        tekstiraam.grid(row=3, column=0)

        textbox = Text(tekstiraam, height=10, width=50, padx=5, state="disabled")
        textbox.grid(row=0, column=0)

        scrollbar = Scrollbar(tekstiraam, command=textbox.yview)
        textbox['yscrollcommand'] = scrollbar.set

        sisendkast = Text(tekstiraam, height=5, width=50, padx=5)
        sisendkast.grid(row=1, column=0)
        sisendkast.bind('<Return>', lambda event: kirjuta(cd))

        sisendnupp = ttk.Button(tekstiraam, text="Saada", command=lambda: kirjuta(cd))
        sisendnupp.grid(column=0, row=2, padx=5, sticky=(W), pady=5)

        thread1 = Thread(target=lambda: loe(cd))
        thread1.daemon = True
        thread1.start()


        #return cd, func('<Return>')
    try:
        toakast.bind('<Return>',func)
    except UnboundLocalError:
        pass


def chatiruum():
    menu()
    print("See on nimi elleroo",kasutajanimi)
    raam = Tk()
    raam.title("UTChat")
    raam.resizable(width=False, height=False)

    nupuraam= Frame()
    nupuraam.grid(column=0, row=1)
    server.send(bytes(kasutajanimi,"utf-8"))
    toad = eval(server.recv(1024).decode("utf-8"))

    uustubanupp=ttk.Button(nupuraam, text="Tee uus tuba", command= lambda: uustuba(raam,kasutajanimi, nupuraam))
    uustubanupp.grid(column=0, row=0, padx=5, sticky=(W),pady=5 )
    olemastoanupp=ttk.Button(nupuraam, text="Liitu olemasolevaga",command=lambda:olemastuba(raam,server,kasutajanimi,toad, nupuraam))
    olemastoanupp.grid(column=1, row=0, padx=5, sticky=(W),pady=5 )



    raam.mainloop()



kasutajanimi = ""
chatiruum()

