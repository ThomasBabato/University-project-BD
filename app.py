import flask_login
from flask import Flask
from flask import redirect, url_for
from flask import render_template, flash, request
from flask_login import LoginManager, login_required, UserMixin,current_user
from sqlalchemy import tuple_

import db
from utils_db import *

app = Flask(__name__)
app.config['SECRET_KEY']='THIS IS SECRET KEY1121312'




#generic config for mysqldb
#
#NOTA : stimao usando sqlalchemy core, visto che con orm l'altra volta stavamo avendo problemi e appunto era una punto
#       extra, per ora ho ricreato quasi tutto con core, me lo devo Vedere ancora un pò per quanto riguarda le fk
# per connettersi con mysql  bisogna usare il dialect pmysql quindi nel momento in cui si crea l'istanza dell'engine :
# engie = create_engine("mysql+pymysql://user:passuser@localhost/dbname")
#controlliamo che al primo avvio della web app sul pc, il db esista o meno. in caso negativo lo si crea.
#crare i vari utenti/ruolisulla propria macchian in mysql.
#Nota : ho creato sulla mia macchina un utente anonimo che potrà vedere le varie info della web app senza registrarsi.


# NO LOGIN PAGES


'''
sezione login
'''
login_manager = LoginManager()
login_manager.init_app(app)
global utenti, locali, lezioni, corsi_seguiti, engine, corsi, prenotazioni,con

#engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")

#con = engine.connect()



@login_manager.user_loader
def load_user(user):
    return User.get_userwithid(user)


class User(UserMixin):
    def __init__(self,idx, nomes,cognomes,emails,passwo):
        self.id =idx,
        self.nome=nomes,
        self.cognome=cognomes,
        self.email=emails,
        self.passw=passwo,
        self.tampome= False
        self.ruolo = "Cliente"

    def get_id(self):
        return self.id


    def get_ruolo(self):
        return self.ruolo

    def get_email(self):
        return self.email


    def get_userwithid(self):
        if self is not None:
            #self.exits = True
            return self
        else:
            return None




######################
# PAGINE SENZA LOGIN #
######################

# funzione evocata al momento della compilazione del form sulla pagina principale
# funzione necessaria per recuperare le credenziali del db
@app.route("/accediDb", methods=['GET', 'POST'])
def accediDb():
    nome = request.form['username']
    paswd = request.form['password']
    db = create_db(nome,paswd)
    global utenti, locali, lezioni, corsi_seguiti, engine, corsi, prenotazioni,con
    utenti = db[0]
    locali = db[1]
    lezioni = db[2]
    corsi_seguiti = db[3]
    engine = db[4]
    corsi = db[5]
    prenotazioni = db[6]
    con = db[7]
    # codice per accedere al db con le credenziali passate dall'html
    return render_template("register.html")  # appena inseriti i dati ho fatto che porta l'utente alla pagina di registrazione

# pagina home
@app.route("/")
def nologin_Home():
    return render_template("nologin_homepage.html")

# pagina di login
@app.route("/login")
def Login():
    return render_template("loginPage.html")

# pagina di registrazione
@app.route("/registrati")
def Register():
    return render_template("register.html")

# funzione per registrare un nuovo utente
# funzione chiamata dopo la compilazione del form presente sulla pagina register
@app.route("/registratiFunzione", methods=['GET', 'POST'])
def RegisterFunction():
    engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")

    con = engine.connect()  # connessione aperta
    con.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")  # livello di isolamento SERIALIZABLE
    con.execute("START TRANSACTION")  # inizio transazione

    # ricerco prima la mail usando una select, poi successivamente provo a inserire i dati nel databases;
    q = text("select utenti.email from utenti where email = :x")
    r = con.execute(q, {"x":request.form['email']}).first()
    if r==None:
            s = utenti.insert().values(nome=request.form['nome'], cognome=request.form['cognome'],
                                       email=request.form['email'], telefono=request.form['telefono'],
                                       password=request.form['password'], tampone=False, ruolo=db.Ruoli.Cliente)
            con.execute(s)
            ru = select([utenti]).where(
                tuple_(utenti.c.email, utenti.c.password).in_([(request.form['email'], request.form['password'])]))
            u = con.execute(ru).fetchone()

            con.execute("create user "+"'"+u[3]+"'"+"@'localhost' identified by "+"'"+u[4]+"';")
            con.execute("flush privileges ")
            con.execute("grant 'Cliente'@'localhost' to "+"'"+u[3]+"'"+"@'localhost'")
            con.execute("flush privileges ")
            con.execute("commit")
            return render_template("loginPage.html")

    else:
        return "Qualcosa è andato storto: " \
           "Cause:" \
           "       Mail già registrata" \
           "       Non tutti i campi sono stati compilati."


# funzione per permettere ad un utente già registrato di accedere alla sua area riservata
# funzione chiamata dopo la compilazione del form presente sulla pagina login
@app.route('/loginfunzione', methods=['GET', 'POST'])
def LoginFunction():
    global utenti, locali, lezioni, corsi_seguiti, engine, corsi, prenotazioni, con
    engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")
    con = engine.connect()  # connessione aperta
    con.connect()

    ru = select([utenti]).where(tuple_(utenti.c.email, utenti.c.password).in_([(request.form['email'], request.form['password'])]))
    u = con.execute(ru).fetchone()
    if u == None:
        return "utente non  registrato, registarsi prima."
    else:
        utente = User(u[0], u[1], u[2], u[3],u[4])
        if load_user(utente):
            engine.connect("mysql+pymysql://"+str(utente.email)+":"+str(utente.passw)+"@localhost/gym")
            flask_login.login_user(utente)
            q = ("select * from prenotazioni where prenotazioni.utente = ':x' ")
            resul = con.execute(q, {"x":utente.get_id()})
            return render_template("areaRiservataUtente_leMiePrenotazioni.html", current_user=current_user.is_authenticated,result=resul
                                   )
        else:
            return "utente non autenticato"


# QUI RISULTA NECESSARIO SVILUPPARE QUESTA FUNZIONE SOTTOSTANTE AL MEGLIO!!!!!!!

# Questa funzione serve per ridirezionare l'utente appena loggato alla sua pagina
# in una fase successiva del progetto ci permetterà di mandare i due tipi di utenti diversi alle pagine
#destinate per i loro ruoli
#TODO: aggiungere if per ruolo e indirizzare in modo corretto
#@app.route('/areaRiservata', methods=["GET","POST"])
#@login_required #richiede login
def areaRiservata():
    return redirect(url_for('areaRiservataUtente_leMiePrenotazioni'))





#############################
# PAGINE PER UTENTI LOGGATI #
#############################

# per andare nella pagina dell'utente per visualizzare le sue prenotazioni
@app.route('/areaRiservataUtente_leMiePrenotazioni')
@login_required
def areaRiservataUtente_leMiePrenotazioni():
    global engine, current_user
    con = engine.connect() #apro una connessione
    # query = inserire query per vedere le prenotazioni dei diversi clienti
    # result = con.execute( ... )   <- esecuzione della query e salvataggio della risposta in result
    #if current_user.is_authenticated == True:
    q = select([prenotazioni]).where(prenotazioni.c.utente).in_('1')
    resul = con.execute(q)
    return render_template('areaRiservataUtente_leMiePrenotazioni',current_user=current_user.is_authenticated)

# per andare alla pagina dove è possibile effettuare una nuova prenotazione
@app.route('/areaRiservataUtente_nuovaPrenotazione')
@login_required
def areaRiservataUtente_nuovaPrenotazione():
    render_template('areaRiservataUtente_nuovaPrenotazione.html')

# funzione per effettuare una nuova prenotazione
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataUtente_nuovaPrenotazione
@app.route('/utenteEffettuaPrenotazione', methods=['GET', 'POST'])
# @login_required
def utenteEffettuaPrenotazione():
    # effettuare una prenotazione della lezione, dall'html mi ritorna l'id della lezione da prenotare
    flash("prenotazione effettuata con successo")
    return

# per andare alla pagina delle impostazioni
@app.route('/areaRiservataUtente_impostazioni')
@login_required
def areaRiservataUtente_impostazioni():
    # recuperare l'ultimo tampone effettuato dall'utente con data e risultato
    # per passare il risultato si dovrebbe salvare il risultato della query in una variabile e poi passarla dentro a render_template insieme alla pagina html
    # sezione di codice in cui viene stampato a video il risultato dell'ultimo tampone è commentato per far in modo che funzioni. Appena è finito, decommentare il codice nell'html!!!
    return render_template("areaRiservataUtente_impostazioni.html")

# funzione per permettere ad un utente di inserire il risultato dell'ultimo tampone eseguito
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataUtente_impostazioni
@app.route('/inserisciRisultatoTampone', methods=['GET', 'POST'])
@login_required
def inserisciRisultatoTampone():
    # recureare le info dell'inserimento del tampone ed inviarla al db
    flash("Inserimento avvenuto correttamente") #Messaggio a schermo che avvisa l'utente del corretto inserimento del risultato del tampone
    return render_template("areaRiservata_importazioni.html")




##############################
# PAGINE PER GESTORE LOGGATO #
##############################

# per andare nella pagina di creazione Lezione e Corsi
@app.route("/areaRiservataGestore_crea")
@login_required
def areaRiservataGestore_crea():
    return render_template("areaRiservataGestore_crea.html")

# funzione per creare un nuovo corso
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataGestore_crea
@app.route("/gestoreCreaCorso", methods=['GET', 'POST'])
#@login.required
def gestoreCreaCorso():
    # recuperare i dati del form
    # inserirli nel database
    flash("Corso creato con successo")
    return render_template("areaRiservataGestore_crea.html")

# funzione per creare una nuova lezione di un corso già esistente
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataGestore_crea
@app.route("/gestoreCreaLezione", methods=['GET', 'POST'])
#@login.required
def gestoreCrealezione():
    # recuperare i dati del form
    # inserirli nel database
    flash("Lezione creata con successo")
    return render_template("areaRiservataGestore_crea.html")


# per andare nella pagina di eliminazione Lezione e Corsi
@app.route("/areaRiservataGestore_elimina.html")
#@login.required
def areaRiservataGestore_elimina():
    return render_template("areaRiservataGestore_elimina.html")

# funzione per eliminare una lezione
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataGestore_elimina
@app.route("/gestoreEliminaLezione", methods=['GET', 'POST'])
#@login.required
def gestoreEliminaLezione():
    # recuperare i dati passati dalla pagina web (basta l'id della lezione)
    # e poi eliminare la lezione dal db
    flash("Lezione eliminata con successo")
    return render_template("areaRiservataGestore_gestioneLezioneCorsi.html")

# funzione per eliminare una lezione
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataGestore_elimina
@app.route("/gestoreEliminaCorso", methods=['GET', 'POST'])
#@login.required
def eliminaCorso():
    # recuperare i dati passati dalla pagina web (basta l'id del corso)
    # e poi eliminare la lezione dal db
    flash("Corso eliminato con successo")
    return render_template("areaRiservataGestore_gestioneLezioneCorsi.html")




#################################
# PAGINE PER ISTRUTTORE LOGGATO #
#################################

# per andare nella pagina di creazione Lezione
@app.route("/areaRiservataIstruttore_creaLezione")
#@login.required
def areaRiservataIstruttore_creaLezione():
    return render_template("areaRiservataIstruttore_creaLezione.html")

# funzione per creare un nuovo corso
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataGestore_crea
@app.route("/istruttoreCreaLezione", methods=['GET', 'POST'])
#@login.required
def istruttoreCreaLezione():
    # recuperare i dati del form
    # inserirli nel database
    flash("Lezione creata con successo")
    return render_template("areaRiservataIstruttore_creaLezione.html")


# per andare nella pagina di eliminazione Lezione
@app.route("/areaRiservataIstruttore_eliminaLezione")
#@login.required
def areaRiservataIstruttore_eliminaLezione():
    return render_template("areaRiservataIstruttore_eliminaLezione.html")

# funzione per eliminare una lezione
# funzione chiamata dopo la compilazione del form presente sulla pagina areaRiservataIstruttore_eliminaLezione
@app.route("/istruttoreEliminaLezione", methods=['GET', 'POST'])
#@login.required
def istruttoreEliminaLezione():
    # recuperare i dati del form
    # inserirli nel database
    flash("Lezione eliminata con successo")
    return render_template("areaRiservataIstruttore_eliminaLezione.html")


# funzione per visualizzare tutte le lezioni dell'istruttore
# PER FARLO FUNZIONARE, DECOMMENTARE LA PARTE DI CODICE PRESENTE NELLA SUDDETTA PAGINA -->
@app.route("/areaRiservataIstruttore_visioneLezioni")
#@login.required
def areaRiservataIstruttore_visioneLezioni():
    # recuperare i dati da stampare
    return render_template("areaRiservataIstruttore_visioneLezioni.html")
