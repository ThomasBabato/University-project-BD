from flask import request, render_template

import  app,query_gym
from db import create_db


@app.route("/accediDb", methods=['GET', 'POST'])
def accediDb():
    nome = request.form['username']
    paswd = request.form['password']
    db = create_db(nome,paswd)
    global utenti, locali, lezioni, corsi_seguiti, g_engine, corsi, prenotazioni,con
    utenti = db[0]
    locali = db[1]
    lezioni = db[2]
    corsi_seguiti = db[3]
    g_engine = db[4]
    corsi = db[5]
    prenotazioni = db[6]
    con = db[7]
    #codice per accedere al db con le credenziali passate dall'html
    return render_template("register.html")  # appena inseriti i dati ho fatto che porta l'utente alla pagina di registrazione
