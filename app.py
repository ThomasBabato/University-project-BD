from flask import Flask, render_template, flash, request
from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select, tuple_, \
    text
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean
from  sqlalchemy_utils.functions import database
from sqlalchemy_utils.types import email
from db import *
from flask_login import LoginManager, login_required, login_user, UserMixin, login_manager, logout_user, current_user
from  utils_db import *
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

manager_login = LoginManager().__init__(app)

class User(UserMixin):
    def __init__(self, id, nome,cognome,email,passw,ruolo):
        self.id = id,
        self.nome=nome,
        self.cognome=cognome,
        self.email=email,
        self.passw=passw
        self.ruolo = ruolo

    def get_id(self):
        return self.id
'''



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
    con = engine.connect()  # connessione aperta
    # ricerco prima la mail usando una select, poi successivamente provo a inserire i dati nel databases;
    a = select([utenti]).where(tuple_(utenti.c.email).in_([(request.form['email'])]))

    r = con.execute(a).first()
    if r != None:
        s = utenti.insert().values(nome=request.form['nome'], cognome=request.form['cognome'],
                                   email=request.form['email'], telefono=request.form['telefono'],
                                   password=request.form['password'])
        try:
            con.execute(s)
            #db-w = text("create user :codice@'localhost' identified by ")
            con.close()
            delete_all()
            return "Registrato!"
        except:
            con.execute("ROLLBACK")
            con.close()
    else:
        con.execute("ROLLBACK")
        con.close()
        return "Qualcosa è andato storto: " \
               "Cause:" \
            "       Mail già registrata" \
            "       Non tutti i campi sono stati compilati." \
            ""

@app.route('/loginfunzione', methods=['GET', 'POST'])
def LoginFunction():
    global engine
    con = engine.connect()
    utente = select([utenti]).where(tuple_(utenti.c.email).in_([request.form['email']]))
    r_utente = con.execute(utente).first()
    if r_utente == None:
        return "Controlla le credenziali, email o password sbagliate."
    #user = User(utente['password'], utente['password'])
    return "login"

