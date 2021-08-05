from select import select
from flask_login import current_user
import db
from sqlalchemy import update, func, insert,delete,values,or_,select
from select import *
from db import utenti,prenotazioni, Ruoli,con,corsi,lezioni,locali, corsi_seguiti
from app import User

#TODO: tutte le query ritornano 1 o 0 solo per debug! rimuovre i ruturn quando si finisce

#prende un oggetto utente e controlla il ruolo.

def controlla_ruolo_utente(utente,*args):
    if utente.get_ruolo != args:
            return False,"Il tuo ruolo non ti permette di fare questa operazione!"
    else:
            return True


#query del gestore
#passati l'id e il nuovo ruolo, questo lo cambia all'interno della tabella utenti
def chaange_role(utente,Id_utente, new_role):
    if not controlla_ruolo_utente(utente,Ruoli.Gestore):
            return "NON HAI L'autorizzazione!"
    else:
        con.connect()
        querys =(
            update(utenti).where(utenti.c.id_utente== Id_utente).values({"utenti.ruolo": new_role}))
        if con.execute(querys) != None:
            con.execute("grant"+str(new_role)+" to :x@'localhost'; ",{"x":Id_utente})
            con.execute("flush privileges ")
            con.execute("commit")


def update_istruttore_corso(utente,corso,new_istruttore):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        con.connect()
        querys= (
            update(corsi).where(corsi.c.id_corso == corso).values({"corsi.istruttore":new_istruttore})
        )
        return con.execute(querys)

def update_locale_corso(utente,corso, new_locale):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        querys = (
            update(corsi).where(corsi.c.id_corso == corso).values({"corsi.locale": new_locale})
        )
        return con.execute(querys)




def update_data_lezione(utente,lezione_id,ora):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        querys = update(lezioni).where(lezioni.c.id_lezione==lezione_id).values({"lezioni.ora":ora})
        return con.execute(querys)



def update_capienza_locali(utente,number,locali_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore):
        query = update(locali).where(locali.c.id_locali==locali_id).values({"capienza_massima": number})
        return con.execute(query)


#istruttore
def update_persone_consentite(utente, number,lezione_id):
    if controlla_ruolo_utente(utente,Ruoli.Gestore,Ruoli.Istruttore):
        query = update(lezioni).where(lezioni.c.id_lezione == lezione_id).values({"persone_consentite":number})
        return con.execute(query)
#utenti:

def insert_corsi_seguiti(utente,id_corso):
    if(controlla_ruolo_utente(utente,Ruoli.Anonimo)):
        return "non puoi effettuare questa operazione"
    else:
        querys = insert(corsi_seguiti).values({"utente":utente.get_id(), "corso_id": id_corso})
        return con.execute(querys)



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
            querys = insert(prenotazioni).values({"prenotazioni.c.utente":utente.get_id(),"prenotazioni.c.corso":
                                                  corso,"prenotazioni.id_lezione":lezione})
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



#ritorna tutto l'oggetto lezione.
def search_lezione(utente,lezione):
    if(controlla_ruolo_utente(utente,Ruoli.Anonimo)):
        return None
    else:
        querys = select(lezioni).where(or_(lezioni.c.id_lezione == lezione,
                                              lezioni.c.giorno== lezione,
                                              lezioni.c.codice_corso == lezione)
                                          )
        rquery = con.execute(querys).fetch_one()
        if(rquery != None):
                return rquery
        return None

#prende il nome del corso o l'id
#ritorna tutto l'oggeto corso.
def search_corso(corso):
    querys  = select(corsi).where(or_(corsi.c.nome==corso,corsi.c.id_corso == corso))
    rquery1 = con.execute(querys).fetch_one()
    if(rquery1!= None):
        return rquery1
    else:
        return None


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