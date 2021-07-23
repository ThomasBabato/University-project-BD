from flask import Flask, render_template, flash, request
from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select, tuple_, \
    text
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean
from  sqlalchemy_utils.functions import database
from sqlalchemy_utils.types import email
import db
from utils_db import *
from db import utenti,locali,lezioni,corsi_seguiti,engine,corsi,prenotazioni
from flask_login import LoginManager, login_required, login_user, UserMixin, login_manager, logout_user, current_user
from  utils_db import *
from flask_login import user_loaded_from_request
from flask import Flask
from flask import redirect, abort, url_for
import re



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

con = engine.connect()

#populate(False)


@login_manager.user_loader
def load_user(user):
    return User.get_userwithid(user)


class User(UserMixin):
    def __init__(self,idx, nomes,cognomes,emails,passwo):
        id = idx,
        nome=nomes,
        cognome=cognomes,
        email=emails,
        passw=passwo,
        tampome= False
        ruolo = db.Ruoli.Cliente

    def get_userwithid(self):
        if self is not None:
            self.exits = True
            return self
        else:
            return None



@app.route("/")
def nologin_Home():
    return render_template("nologin_homepage.html")

@app.route("/attivita")
def nologin_Attivita():
    return render_template("nologin_attivita.html")

@app.route("/locali")
def nologin_Locali():
    return render_template("nologin_locali.html")

@app.route("/contatti")
def nologin_Contatti():
    return render_template("nologin_contatti.html")


# LOGIN PAGE
@app.route("/login")
def Login():
    return render_template("loginPage.html")

# REGISTRATI
@app.route("/registrati")
def Register():
    return render_template("register.html")


@app.route("/registratiFunzione", methods=['GET', 'POST'])
def RegisterFunction():
    global engine
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
            return render_template("loginPage.html")
            con.execute("ROLLBACK")
            con.close()
    else:
        return "Qualcosa è andato storto: " \
           "Cause:" \
           "       Mail già registrata" \
           "       Non tutti i campi sono stati compilati."


@app.route('/loginfunzione', methods=['GET', 'POST'])
def LoginFunction():
    global engine
    con = engine.connect()
    ru = select([utenti]).where(tuple_(utenti.c.email, utenti.c.password).in_([(request.form['email'], request.form['password'])]))
    u = con.execute(ru).fetchone()
    if u == None:
        con.close()
        return "utente non  registrato, registarsi prima."
    else:
        utente = User(u[0], u[1], u[2], u[3], u[4])
        if load_user(utente):
            return redirect(url_for("areaRiservata_leMiePrenotazioni"))
        else:
            return "campi sbagliati"

# Questa funzione serve per ridirezionare l'utente appena loggato alla sua pagina
# in una fase successiva del progetto ci permetterà di mandare i due tipi di utenti diversi alle pagine
#destinate per i loro ruoli
@app.route('/areaRiservata', methods=["GET","POST"])
@login_required #richiede login
def areaRiservata():
    return redirect(url_for('areaRiservata_leMiePrenotazioni'))


#############################
# PAGINE PER UTENTI LOGGATI #
#############################


@app.route('/areaRiservata_leMiePrenotazioni')
#   @login_required
def areaRiservata_leMiePrenotazioni():
    con = engine.connect() #apro una connessione
    # query = inserire query per vedere le prenotazioni dei diversi clienti
    # result = con.execute( ... )   <- esecuzione della query e salvataggio della risposta in result
    con.close() #chiusura connessione
    return render_template("areaRiservata_leMiePrenotazioni.html")
