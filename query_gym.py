from select import select

import sqlalchemy

from app import *
from sqlalchemy import update, func, insert,delete,values,or_,select,and_
from flask_login import current_user
from select import *
from sqlalchemy.orm import sessionmaker
from db import Ruoli
from orm_automap import *

#TODO: tutte le query ritornano 1 o 0 solo per debug! rimuovre i ruturn quando si finisce

#prende un oggetto utente e controlla il ruolo.
def connect_user(utente):
    engine.connect("mysql+pymysql://" + str(utente.email) + ":" + str(utente.passw) + "@localhost/gym")
    return engine

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()

#passato un argomento se questo combacia con quello dell'utente allora ritorna falso!
#usarla come esclusione
def controlla_ruolo_utente(utente,*args):
    if utente.ruolo == args:
            return False
    else:
            return True


#query del gestore
#preso l'utente che effettua l'oprazione, controlla che abbia il permesso per effettuarla.
#passati l'id e il nuovo ruolo, questo lo cambia all'interno della tabella utenti
def change_role(utente,Id_utente,mail,new_role:String):
    Session = sessionmaker(bind=engine)
    session = Session()
    #if controlla_ruolo_utente(utente, Ruoli.Gestore):
        # session.execute(update(utenti,values={"ruolo" : "Cliente"})) funziona
        # session.commit()
    con.execute("revoke Cliente@'localhost' from"+"'"+mail+"'"+"@'localhost';")
    con.execute("grant '"+new_role+"'"+"@'localhost' to "+"'"+mail+"'"+"@'localhost'")
    session.query(utenti).filter(utenti.c.id_utente == Id_utente).update({utenti.c.ruolo: new_role})
    session.commit()
    session.execute("flush privileges")
    session.close()


#preso l'utente che effettua l'operazione [utente/gestore della palestra] cambia l'istruttore di un dato corso
def update_istruttore_corso(utente,corso_id,new_istruttore):
    if controlla_ruolo_utente(utente, Ruoli.Anonimo, Ruoli.Istruttore, Ruoli.Cliente):
        session = get_session()
        session.query(corsi).filter(corsi.c.id_corso == corso_id).update({corsi.c.istruttore: new_istruttore})
        session.commit()
    else:
        return "istruttore non aggiornato"


def update_locale_corso(utente,corso, new_locale):
    if controlla_ruolo_utente(utente, Ruoli.Anonimo, Ruoli.Istruttore, Ruoli.Cliente):
        session = get_session()
        session.query(corsi).filter(corsi.c.id_corso == corso).update({corsi.c.locale: new_locale})
        session.commit()
        session.close()
    else:
        return "locale non aggiornato"



def update_data_lezione(utente,lezione_id,ora):
    if controlla_ruolo_utente(utente, Ruoli.Anonimo, Ruoli.Cliente):
        session = get_session()
        session.query(lezioni).filter(lezioni.c.id_lezione == lezione_id).update({lezioni.c.ora :ora})
        session.commit()
        session.close()



def update_capienza_locali(utente,number,locali_id):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo,Ruoli.Istruttore,Ruoli.Cliente):
        s =get_session().query(locali).filter(locali.c.id_locali==locali_id).update({locali.c.capienza_massima:number})
        s.commit()
        s.close()

def insert_locale(utente,name,mqs,capienza):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo,Ruoli.Istruttore,Ruoli.Cliente):
        e = connect_user(utente)
        con = e.connect()
        querys = locali.insert().values({locali.c.nome : name, locali.c.mq : mqs, locali.c.capienza_massima : capienza})
        con.execute(querys)
        con.execute("commit")
        return 1
    else:
        return 0


def insert_corso(utente,nomes,descri,istr,local):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo,Ruoli.Istruttore,Ruoli.Cliente):
        e = connect_user(utente)
        con = e.connect()
        querys = corsi.insert().values({corsi.c.nome : nomes,corsi.c.descrizione : descri, corsi.c.istruttore : istr, corsi.c.locale: local})
        con.execute(querys)



def insert_corsi_seguiti(utente,corso):

    if controlla_ruolo_utente(utente,Ruoli.Anonimo):
        e = connect_user(utente)
        con = e.connect()
        querys = corsi_seguiti.insert().values({corsi_seguiti.c.utente: utente.get_id(), corsi_seguiti.c.corso_id :corso})
        con.execute(querys)



def insert_lezione(utente,corso,descr,giorno,number):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo,Ruoli.Cliente):
        e = connect_user(utente)
        con = e.connect()
        querys = lezioni.insert().values({lezioni.c.codice_corso:corso,lezioni.c.descrizione : descr,
                                          lezioni.c.Data_e_ora:giorno,lezioni.c.persone_consentite:number})
        con.execute(querys)
        return 1


#istruttore
def update_persone_consentite(utente, number,lezione_id):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo,Ruoli.Cliente):
        s = get_session().query(lezioni).filter(lezioni.c.id_lezione==lezione_id).update({lezioni.c.persone_consentite : number})
        s.commit()
        s.close()


#tutti


#passato l'id di lezione,corso e utente inserire nel db una prenotazione.

def insert_prenotazione(utente,lezione,corso):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo):
        con = connect_user(utente)
        s = get_session()
        p = s.query(prenotazioni).filter(prenotazioni.c.lezione==lezione).count()

        n = s.query(lezioni.c.persone_consentite).where(lezioni.c.id_lezione==lezione).one()
        for i in n:
            r2 = i
        if p < r2:
            querys = prenotazioni.insert().values(
                {prenotazioni.c.utente: utente.get_id(), prenotazioni.c.corso: corso,prenotazioni.c.lezione : lezione})
            con.execute(querys)
            return 1




def delete_prenotazione(utente,lezione,corso):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo):
            return None
    else:
        con = engine.connect()
        querys = delete(prenotazioni).where(or_(prenotazioni.c.lezione==lezione,
                                                prenotazioni.c.utente == utente.get_id(),
                                                prenotazioni.c.corso==corso)
                                            )
        con.execute(querys)

#rivere la tabella e impostare la cancellazione per bene!
def delete_corso(utente,corso):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo):
        return None
    else:
        con= engine.connect()
        s = text("DELETE FROM corsi WHERE corsi.id_corso=:x;")
        con.execute(s,{"x":corso})

def delete_lezione(utente,lezione):
    if controlla_ruolo_utente(utente, Ruoli.Anonimo,Ruoli.Cliente):
        con= engine.connect()
        s = text("DELETE FROM lezioni WHERE lezioni.id_lezione=:x;")
        con.execute(s,{"x":lezione})



#ritorna tutto l'oggetto lezione.
def search_lezione(lezione):
    s= get_session()
    querys=s.query(lezioni).where(lezioni.c.id_lezione==lezione)
    r = session.execute(querys)
    for i in r:
        return i

#prende il nome del corso o l'id
#ritorna tutto l'oggeto corso.
def search_corso(corso):
    s = get_session()
    querys = s.query(corsi).where(corsi.c.id_corso == corso)
    r = session.execute(querys)
    for i in r:
        return i


def update_tampone(utente,val):
    if controlla_ruolo_utente(utente,Ruoli.Anonimo):
        querys = update([utenti.c.tapone]).where(utente == utenti.c.id_utente).values({"tampone":val})
        return con.execute(querys).fetch_one()


#preso l'id di un utente ritorna il tampone.
def rTampone(utente):
    querys = select(utenti.c.tapone).where(or_(utenti.c.id_utente==utente)
                                             )
    return con.execute(querys).fetch_one()


def search_id_utente(utente):
    querys = select(utenti.c.id).where((utenti.c.email==utente))
    return con.execute(querys).fetch_one()

