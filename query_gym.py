from select import select
from app import *
from sqlalchemy import update, func, insert,delete,values,or_,select,and_
from flask_login import current_user
from select import *
from sqlalchemy.orm import sessionmaker
from db import utenti,prenotazioni, Ruoli,con,corsi,lezioni,locali, corsi_seguiti
from orm_automap import *

#TODO: tutte le query ritornano 1 o 0 solo per debug! rimuovre i ruturn quando si finisce

#prende un oggetto utente e controlla il ruolo.
def connect_user(utente):
    engine.connect("mysql+pymysql://" + str(utente.email) + ":" + str(utente.passw) + "@localhost/gym")
    return engine

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()



def controlla_ruolo_utente(utente,*args):
    if utente.get_ruolo() != args:
            return False,"Il tuo ruolo non ti permette di fare questa operazione!"
    else:
            return True


#query del gestore
#passati l'id e il nuovo ruolo, questo lo cambia all'interno della tabella utenti
def change_role(utente,Id_utente, new_role:String):
    Session = sessionmaker(bind=engine)
    session = Session()
    if controlla_ruolo_utente(utente, Ruoli.Gestore):
        # session.execute(update(utenti,values={"ruolo" : "Cliente"})) funziona
        # session.commit()
        session.query(utenti).filter(utenti.c.id_utente == Id_utente).update({utenti.c.ruolo: new_role})
        session.commit()
        session.execute("flush privileges")
    session.close()


def update_istruttore_corso(utente,corso_id,new_istruttore):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        session = get_session()
        session.query(corsi).filter(corsi.c.id_corso == corso_id).update({corsi.c.istruttore: new_istruttore})
        session.commit()
    else:
        return "istruttore non aggiornato"

def update_locale_corso(utente,corso, new_locale):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        session = get_session()
        session.query(corsi).filter(corsi.c.id_corso == corso).update({corsi.c.locale: new_locale})
        session.commit()
        session.close()
    else:
        return "locale non aggiornato"



def update_data_lezione(utente,lezione_id,ora):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        session = get_session()
        session.query(lezioni).filter(lezioni.c.id_lezione == lezione_id).update({lezioni.c.ora :ora})
        session.commit()
        session.close()



def update_capienza_locali(utente,number,locali_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        s =get_session().query(locali).filter(locali.c.id_locali==locali_id).update({locali.c.capienza_massima:number})
        s.commit()
        s.close()

def insert_locale(utente,name,mqs,capienza):
    e =connect_user(utente)
    con = e.connect()
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        querys = locali.insert().values({locali.c.nome : name, locali.c.mq : mqs, locali.c.capienza_massima : capienza})
        con.execute(querys)
        con.execute("commit")
        return 1
    else:
        return 0


def insert_corso(utente,nomes,descri,istr,local):
    e = connect_user(utente)
    con = e.connect()
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        querys = corsi.insert().values({corsi.c.nome : nomes,corsi.c.descrizione : descri, corsi.c.istruttore : istr, corsi.c.locale: local})
        con.execute(querys)



def insert_corsi_seguiti(utene,corso):
    e = connect_user(utene)
    con = e.connect()
    if controlla_ruolo_utente(utene,Ruoli.Gestore,Ruoli.Istruttore,Ruoli.Cliente):
        querys = corsi_seguiti.insert().values({corsi_seguiti.c.utente: utene.get_id(), corsi_seguiti.c.corso_id :corso})
        con.execute(querys)



def insert_lezione(utente,corso,descr,giorno,number):
    e = connect_user(utente)
    con = e.connect()
    if controlla_ruolo_utente(utente, Ruoli.Gestore, Ruoli.Istruttore, Ruoli.Cliente):
        querys = lezioni.insert().values({lezioni.c.codice_corso:corso,lezioni.c.descrizione : descr,
                                          lezioni.c.Data_e_ora:giorno,lezioni.c.persone_consentite:number})
        con.execute(querys)
        return 1


#istruttore
def update_persone_consentite(utente, number,lezione_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        s = get_session().query(lezioni).filter(lezioni.c.id_lezione==lezione_id).update({lezioni.c.persone_consentite : number})
        s.commit()
        s.close()


#tutti


#passato l'id di lezione,corso e utente inserire nel db una prenotazione.

def insert_prenotazione(utente,lezione,corso):
    if(controlla_ruolo_utente(utente,Ruoli.Anonimo)):
        return "utente anonimo. non sei autorizzato a fare questa query!"
    else:
        p= select(prenotazioni).where((lezioni.id_lezione == lezione))
        prenotazioni_effettuate_in_precedenza= select(func.count()).select_form(p)

        numero_massimo_di_persone_consentite = select(lezioni.persone_consentite).where(lezioni.id_lezione==lezione)

        if prenotazioni_effettuate_in_precedenza < numero_massimo_di_persone_consentite or rTampone(utente.get_id()):
            querys = prenotazioni.insert(prenotazioni).values({prenotazioni.c.utente:utente.get_id(),prenotazioni.c.corso:
                                                  corso,prenotazioni.id_lezione:lezione})
            return con.execute(querys)
        else:
            return "non puoi effettuare prenotazioni per questa lezione."



def delete_prenotazione(utente,lezione,corso):
    if not controlla_ruolo_utente(utente,Ruoli.Anonimo):
            return None
    else:
        querys = delete(prenotazioni).where(or_(prenotazioni.c.lezione==lezione,
                                                prenotazioni.c.utente == utente,
                                                prenotazioni.c.corso==corso)
                                            )
        return con.execute(querys)
#rivere la tabella e impostare la cancellazione per bene!

def delete_corso(utente,corso):
    if not controlla_ruolo_utente(utente,Ruoli.Gestore):
        return None
    else:
        con= engine.connect()
        s = text("DELETE FROM corsi WHERE corsi.id_corso=:x;")
        con.execute(s,{"x":corso})


def delete_lezione(lezione):
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

