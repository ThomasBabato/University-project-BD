from flask import Flask, render_template, flash, request
from sqlalchemy import create_engine, MetaData, inspect, ForeignKeyConstraint, PrimaryKeyConstraint, select
from sqlalchemy import inspect,Table, Column, Integer, String, MetaData, ForeignKey,Float,DateTime,Date,Boolean
from  sqlalchemy_utils.functions import database
from sqlalchemy_utils.types import email
from db import *


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
    con=engine.connect() #connessione aperta
    #con.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE") #livello di isolamento SERIALIZABLE
    #con.execute("START TRANSACTION") #inizio transazione
    #controlliamo se esiste un utente registrato con la stessa email facendo una query al db
   # s= utenti.query.filter_by(utenti.c.email=email=request.form['email'])
    #result_checkEmail = con.execute ("Select * from utenti where utenti.id_utente=12")
    #verifichiamo se la query ha dato almeno un risultato
    #in caso positivo diamo un feedback all'utente e lo facciamo tornare alla pagina di registrazione
     #   flash("Email già usata da un altro utente")
     #   render_template("register.html")
    #creiamo la query per inserire il nuovo utente

    con = engine.connect()  # connessione aperta
    s = utenti.insert().values(nome=request.form['nome'], cognome=request.form['cognome'],
                               email=request.form['email'], telefono=request.form['telefono'],
                               password=request.form['password'])
    con.execute(s)
    #con.execute("delete from utenti")
    con.close()

    flash("Registrazione eseguito correttamente!")
    return "Registrato!"
