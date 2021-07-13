from flask import Flask, render_template
from sqlalchemy import create_engine,MetaData,inspect,ForeignKeyConstraint,PrimaryKeyConstraint
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean
from  sqlalchemy_utils.functions import database

app = Flask(__name__)


#generic config for mysqldb
#
#NOTA : stimao usando sqlalchemy core, visto che con orm l'altra volta stavamo avendo problemi e appunto era una punto
#       extra, per ora ho ricreato quasi tutto con core, me lo devo Vedere ancora un pò per quanto riguarda le fk
# per connettersi con mysql  bisogna usare il dialect pmysql quindi nel momento in cui si crea l'istanza dell'engine :
# engie = create_engine("mysql+pymysql://user:passuser@localhost/dbname")
#controlliamo che al primo avvio della web app sul pc, il db esista o meno. in caso negativo lo si crea.
#crare i vari utenti/ruolisulla propria macchian in mysql.
#Nota : ho creato sulla mia macchina un utente anonimo che potrà vedere le varie info della web app senza registrarsi.

engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost", echo=True)

if not database.database_exists("mysql+pymysql://anonimo:Anonimo1%@localhost//University-project-BD/gym"):
    con = engine.connect()
    con.execute("commit")
    con.execute("create database gym")
    con.execute("set global activate_all_roles_on_login = on")  # attivazione di tutti i ruoli
    con.close()
else:
    #TODO: da elimianre? momentaneamente lascio, può tornare utile.
    print("il database esiste già")

engine = create_engine("mysql+pymysql://anonimo:Anonimo1%@localhost/gym")
metadata = MetaData()

###########
#sezione dedicata alla creaazione delle tabelle in mysql tramite sql alchemy core:
#TODO: aggiungere la colonna corsi.
utenti = Table('utenti',metadata,
               Column('id_utente',Integer,primary_key=True,autoincrement=True),
               Column('nome',String(25)),
               Column('cognome',String(25)),
               Column('email',String(30)),
               Column('telefono',String(15)),
               Column('Tampone',Boolean),
               #Column('ruolo',enumerate((0,'gestore'),(1,'iStruttori'),('2','utenti')))
               )
#TODO: aggiungere colonne istruttore id e istruttre
corsi = Table('corsi',metadata,
              Column('id_corso', Integer,autoincrement=True),
              Column('nome', String(25)),
              PrimaryKeyConstraint('id_corso','nome',name='corsi_pk'),
              Column('descrizione', String(150))
              )

corsi_seguiti = Table('corsi_seguiti',metadata,
                    Column('utente',None,ForeignKey('utenti.id_utente'),nullable=False),
                    Column('corso_id',None,ForeignKey('corsi.id_corso')),
                    )


#TODO :
locali = Table('locali',metadata,
               Column('id_locale', Integer, primary_key=True, autoincrement=True),
               Column('nome', String(25)),
               Column('mq', Float),
               Column('capienza', Integer)
              )
#TODO: aggiungere i collegamenti tra corso e id
lezioni = Table('lezioni',metadata,
                Column('id_lezione', Integer, primary_key=True, autoincrement=True),
                Column('descrizione', String(120)),
                Column('giorno',Date),
                Column('ora',DateTime)
                )

corso_

metadata.create_all(engine)

###########



@app.route("/helloworld")
def hello_world():
    return "<p>Hello, World!</p>"


# NO LOGIN PAGES

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
