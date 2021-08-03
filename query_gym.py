from select import select

import db
from sqlalchemy import update, values, func, insert
from db import utenti,prenotazioni, Ruoli,con,corsi,lezioni,locali
from app import User

#TODO: tutte le query ritornano 1 o 0 solo per debug! sono da eliminare quando si finisce.

def controlla_ruolo_utente(utente,*args):
    if utente.get_ruolo != args:
            return False,"Il tuo ruolo non ti permette di fare questa operazione!"
    else:
            return True


#query del gestore
#passati l'id e il nuovo ruolo, questo lo cambia all'interno della tabella utenti


def chaange_role(utente,Id_utente, new_role):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        con.connect()
        querys =(
            update(utenti).where(utenti.c.id_utente== Id_utente).values({"utenti.ruolo": new_role}))
        if con.execute(querys) != None:
            con.execute("grant"+str(new_role)+" to :x@'localhost'; ",{"x":Id_utente})
            return 1
        else:
            return 0


def update_istruttore_corso(utente,corso,new_istruttore):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        con.connect()
        querys= (
            update(corsi).where(corsi.c.id_corso == corso).values({"corsi.istruttore":new_istruttore})
        )
        if con.execute(querys) != None:
            return 1
        else:
            return 0


def update_locale_corso(utente,corso, new_locale):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        querys = (
            update(corsi).where(corsi.c.id_corso == corso).values({"corsi.locale": new_locale})
        )
        if con.execute(querys) != None:
            return 1
        else:
            return 0

def update_data_lezione(utente,lezione_id,ora):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        querys = update(lezioni).where(lezioni.c.id_lezione==lezione_id).values({"lezioni.ora":ora})
        if con.execute(querys) != None:
            return 1
        else:
            return 0

def update_persone_consentite(utente, number,lezione_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        query = update(lezioni).where(lezioni.c.id_lezione == lezione_id).values({"persone_consentite":number})
    if con.execute(query) != None:
        return 1
    else:
        return 0


def update_capienza_locali(utente,number,locali_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        query = update(locali).where(locali.c.id_locali==locali_id).values({"capienza_massima": number})
    if(con.execute(query))!=None:
        return 1
    else:
        return 0


def insert_prenotazione(utente,lezione,corso):
    if(controlla_ruolo_utente(utente,Ruoli.Anonimo)):
        return "utente anonimo. non sei autorizzato a fare questa query!"
    else:
        p= select([prenotazioni]).where((lezioni.id_lezione == lezione))
        prenotazioni_effettuate_in_precedenza= select([func.count()]).select_from(p)

        numero_massimo_di_persone_consentite = select([lezioni.persone_consentite]).where(lezioni.id_lezione==lezione)

        if prenotazioni_effettuate_in_precedenza<numero_massimo_di_persone_consentite:
            querys = insert(prenotazioni).values({"prenotazioni.c.utente":utente,"prenotazioni.c.corso":
                                                  corso,"prenotazioni.id_lezione":lezione})
            con.execute(querys)
        else:
            return "non puoi effettuare prenotazioni per questa lezione."






